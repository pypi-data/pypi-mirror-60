from typing import List
from jinja2 import Environment
from .iface import Filter


class JinjaFilter(Filter):
    def __init__(self, **kwargs):
        self.env = Environment(**kwargs)
        self.addfilter("brace", self.brace)

    def addfilter(self, name, fn):
        self.env.filters[name] = fn

    def brace(self, vals):
        if isinstance(vals, (tuple, list)):
            vals = [self.brace(x) for x in vals]
            return "{" + ",".join(vals) + "}"
        return str(vals)

    def render(self, s: str, vals: dict) -> str:
        tmpl = self.env.from_string(s)
        return tmpl.render(**vals)

    def var_names(self, s: str) -> List[str]:
        res = set()
        for b in self.env.parse(source=s).body:
            res.update([x.name for x in filter(
                lambda f: f.__class__.__name__ == "Name", b.nodes)])
        return res
