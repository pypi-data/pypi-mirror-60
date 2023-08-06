import os

from .iface import Filter, Input, Output
from .jinjafilter import *
from .multifilter import *
from .reversefilter import *
from .strfilter import *
from .makofilter import *
from .nullfilter import *
from .tar import *
from .zip import *
from .dirtree import *
from .git import *


def isX(v, x):
    if not isinstance(v, type):
        return False
    if not issubclass(v, x):
        return False
    if "Abstract" in v.__name__:
        return False
    if v is x:
        return False
    return True


def input_items():
    for k, v in globals().items():
        if isX(v, Input):
            if k.endswith("Input"):
                k = k[:-len("Input")]
            yield k, v


def output_items():
    for k, v in globals().items():
        if isX(v, Output):
            if k.endswith("Output"):
                k = k[:-len("Output")]
            yield k, v


def filter_items():
    for k, v in globals().items():
        if isX(v, Filter):
            if k.endswith("Filter"):
                k = k[:-len("Filter")]
            yield k, v


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
        ".git": "Git",
    }
    if os.path.isdir(filename):
        return "Dir"
    for k, v in extmap.items():
        if filename.endswith(k):
            return v
    if os.path.exists(os.path.join(filename, ".git")) or filename.startswith("http"):
        return "Git"
    if os.path.exists(filename):
        return "Single"
    return defval


def detect_input(fn: str, guess: str) -> Input:
    return dict(input_items()).get(auto_detect(fn, guess))


def detect_output(fn: str, guess: str) -> Output:
    return dict(output_items()).get(auto_detect(fn, guess), DirOutput)
