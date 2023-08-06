from mako.template import Template

from .iface import Filter


class MakoFilter(Filter):
    def render(self, s: str, vals: dict) -> str:
        return Template(s).render(**vals)
