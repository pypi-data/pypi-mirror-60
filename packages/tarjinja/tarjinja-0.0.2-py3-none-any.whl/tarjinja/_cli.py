import os
import sys
import functools
import click
import subprocess
import yaml
import tempfile
import requests
import json
import string
from .choice import input_items, output_items, filter_items
from .multifilter import MultiFilter
from .iface import Pipeline
from .version import VERSION
from logging import getLogger, basicConfig, INFO, DEBUG

log = getLogger(__name__)


@click.version_option(version=VERSION, prog_name="tarjinja")
@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


def set_verbose(flag):
    fmt = '%(asctime)s %(levelname)s %(message)s'
    if flag:
        basicConfig(level=DEBUG, format=fmt)
    else:
        basicConfig(level=INFO, format=fmt)


_cli_option = [
    click.option("--verbose/--no-verbose"),
]

_value_option = [
    click.option("--value-from", type=click.File('r')),
    click.option("--value", default='{}', type=str),
    click.option("--gitconfig/--no-gitconfig"),
    click.option("--github-user/--no-github-user"),
]

_inout_option = [
    click.argument("input", type=click.Path(), required=True),
    click.argument("output", type=click.Path(), required=True),
]


def multi_options(decs):
    def deco(f):
        for dec in reversed(decs):
            f = dec(f)
        return f
    return deco


def cli_option(func):
    @functools.wraps(func)
    def wrap(verbose, *args, **kwargs):
        set_verbose(verbose)
        return func(*args, **kwargs)
    return multi_options(_cli_option)(wrap)


def value_option(func):
    @functools.wraps(func)
    def wrap(value, value_from, gitconfig, github_user, *args, **kwargs):
        if value_from:
            vals = yaml.load(value_from, Loader=yaml.FullLoader)
        else:
            vals = json.loads(value)
        if gitconfig:
            p = subprocess.run(["git", "config", "-l"],
                               stdout=subprocess.PIPE, encoding="UTF-8", stdin=subprocess.DEVNULL)
            for l in p.stdout.split("\n"):
                if "=" not in l:
                    continue
                k, v = l.strip().split("=", 1)
                v = v.strip()
                if v in ["true", "false"] + list(string.digits):
                    continue
                k = "git_" + k.replace(".", "_")
                if len(v) != 0:
                    vals[k] = v
        if github_user:
            p = subprocess.run(["hub", "api", "user"], stdout=subprocess.PIPE,
                               encoding="UTF-8", stdin=subprocess.DEVNULL)
            data = json.loads(p.stdout)
            for k, v in data.items():
                if isinstance(v, str) and v != "":
                    vals["github_" + k] = v
        return func(value=vals, *args, **kwargs)
    return multi_options(_value_option)(wrap)


def inout_option(func):
    @functools.wraps(func)
    def wrap(input, output, *args, **kwargs):
        if "://" in input:
            tmpd = tempfile.TemporaryDirectory()
            tmpfn = os.path.join(tmpd.name, os.path.basename(input))
            with open(tmpfn, 'wb') as ofp:
                ofp.write(requests.get(input).content)
            input = tmpfn
        return func(input=input, output=output, *args, **kwargs)
    return multi_options(_inout_option)(wrap)


def auto_detect(filename, defval):
    extmap = {
        ".tar.gz": "Tar",
        ".tar.bz2": "Tar",
        ".tar.xz": "Tar",
        ".tar": "Tar",
        ".tgz": "Tar",
        ".tbz2": "Tar",
        ".txz": "Tar",
        ".zip": "Zip",
    }
    if os.path.isdir(filename):
        return "Dir"
    for k, v in extmap.items():
        if filename.endswith(k):
            return v
    return defval


def do_pipe(in_type, out_type, input, output, filter_type, vals, thru=None, notag=False):
    log.debug("input: %s (%s), output: %s (%s), filter: %s",
              input, in_type, output, out_type, filter_type)
    input_val = dict(input_items()).get(in_type)(input)
    output_val = dict(output_items()).get(out_type)(output)
    if isinstance(filter_type, (list, tuple)):
        if len(filter_type) == 1:
            filter_val = dict(filter_items()).get(filter_type[0])()
        else:
            filter_val = MultiFilter()
            for f in filter_type:
                filter_val.add_filter(dict(filter_items()).get(f)())
    else:
        filter_val = dict(filter_items()).get(filter_type)()
    if notag:
        filter_val.tag_escape = {}
    pipeline = Pipeline(input_val, filter_val, output_val, thru)
    pipeline.render(vals)


@cli.command()
@cli_option
@value_option
@inout_option
@click.option("--out-type", type=click.Choice(dict(output_items())), required=True)
@click.option("--in-type", type=click.Choice(dict(input_items())), required=True)
@click.option("--filter-type", type=click.Choice(dict(filter_items())), multiple=True)
@click.option("--thru", type=str, default=None)
def copy(in_type, out_type, filter_type, input, output, value, thru):
    do_pipe(in_type, out_type, input, output, filter_type, value, thru)


@cli.command()
@cli_option
@value_option
@click.option("--filter-type", type=click.Choice(dict(filter_items())), default="Jinja")
@inout_option
def tarc(output, input, value, filter_type):
    out_type = auto_detect(output, "Tar")
    in_type = auto_detect(input, "Dir")
    do_pipe(in_type, out_type, input, output, filter_type, value)


@cli.command()
@cli_option
@click.option("--filter-type", type=click.Choice(dict(filter_items())), default="Jinja")
@value_option
@click.option("--verbose/--no-verbose")
@inout_option
def tarx(output, input, value, filter_type):
    out_type = auto_detect(output, "Dir")
    in_type = auto_detect(input, "Tar")
    do_pipe(in_type, out_type, input, output, filter_type, value)


@cli.command()
@cli_option
@click.option("--filter-type", type=click.Choice(dict(filter_items())), default="Jinja")
@value_option
@click.option("--dry/--no-dry")
@click.option("--skiptag/--no-skiptag", default=False)
@inout_option
def rsync(output, input, value, filter_type, dry, skiptag):
    log.info("input %s, output %s", input, output)
    in_type = auto_detect(input, "Single")
    if dry:
        out_type = "List"
    else:
        out_type = auto_detect(output, "Dir")
    do_pipe(in_type, out_type, input, output,
            filter_type, value, None, skiptag)


@cli.command()
@cli_option
@value_option
def dump_value(value):
    json.dump(value, sys.stdout)


if __name__ == "__main__":
    cli()
