from .iface import Filter
from typing import Generator


class NullFilter(Filter):
    def __init__(self, **kwargs):
        pass

    def render(self, s: str, vals: dict) -> str:
        return s

    def renderfn(self, s: str, vals: dict) -> Generator[str, None, None]:
        yield self.render(s, vals)
