import os
import time
import tempfile
import io
from logging import getLogger
from typing import Generator, Tuple
from .iface import Input
import git


log = getLogger(__name__)


class GitInput(Input):
    def __init__(self, ifn: str, name: str, branch: str = "master", tmpdir: str = None):
        log.debug("ifn=%s, name=%s, branch=%s, tmpdir=%s",
                  ifn, name, branch, tmpdir)
        super().__init__(ifn)
        if tmpdir is None:
            self.tmpd = tempfile.TemporaryDirectory()
            self.tmpdir = self.tmpd.name
        else:
            self.tmpdir = tmpdir
        dirn = os.path.join(self.tmpdir, name)
        if os.path.isdir(dirn):
            self.repo = git.repo.Repo(dirn)
            self.repo.remote().fetch(refspec=branch, depth=1)
        else:
            self.repo = git.repo.Repo.clone_from(self.ifn, dirn, bare=True,
                                                 branch=branch, depth=1)
        self.ts = time.time()
        self.files = {}

    def walk(self) -> Generator[Tuple[str, int, float], None, None]:
        for x in self.repo.tree().traverse():
            if x.type != "blob":
                continue
            self.files[x.path] = x
            yield x.path, x.mode, self.ts

    def readfile(self, fn: str) -> str:
        try:
            return io.TextIOWrapper(io.BytesIO(self.files.get(fn).data_stream.read())).read()
        except UnicodeDecodeError as e:
            log.warning("cannot decode", e)
            return ""
