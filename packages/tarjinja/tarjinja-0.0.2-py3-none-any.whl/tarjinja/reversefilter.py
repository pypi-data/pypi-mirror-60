from logging import getLogger
from .iface import Filter

log = getLogger(__name__)


class AbstractReverseFilter(Filter):
    def placeholder(self, name: str) -> str:
        raise NotImplementedError("placeholder")

    tag_escape = {}

    def render(self, s: str, vals: dict) -> str:
        valmap = {}
        for k, v in vals.items():
            if not v.__hash__:
                continue
            if v not in valmap:
                valmap[v] = self.placeholder(k)
        for k, v in self.tag_escape.items():
            valmap[k] = v
        log.debug("strtr: %s", valmap)
        res = self.strtr(s, valmap)
        log.debug("changed: %s <- %s", repr(res[:100]), repr(s[:100]))
        return res


class ReverseJinjaFilter(AbstractReverseFilter):
    tag_escape = dict([(x, "{%raw%}" + x + "{%endraw%}")
                       for x in ["{{", "}}", "{%", "%}"]])

    def placeholder(self, name: str) -> str:
        return "{{" + name + "}}"


class ReverseTemplateFilter(AbstractReverseFilter):
    tag_escape = {"$": "$$"}

    def placeholder(self, name: str) -> str:
        return "${" + name + "}"


class ReverseFormatFilter(AbstractReverseFilter):
    tag_escape = {"{": "{{", "}": "}}"}

    def placeholder(self, name: str) -> str:
        return "{" + name + "}"


class ReversePercentFilter(AbstractReverseFilter):
    tag_escape = {"%": "%%"}

    def placeholder(self, name: str) -> str:
        return "%(" + name + ")s"


class ReverseFstringFilter(ReverseFormatFilter):
    pass
