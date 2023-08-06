from .parse import LogParser
from .config import Config
from .version import Versioner
import attr as a


@a.s(auto_attribs=True)
class SemVer(object):

    log_parser: LogParser
    versioner: Versioner

    def __call__(self, logs: str) -> str:
        lvls = self.log_parser.parse_commits(logs)
        for lvl in lvls:
            self.versioner.bump(lvl)
        return self.versioner.version


def semver(logs: str, config: Config) -> str:
    sv = SemVer(
        LogParser(config),
        Versioner()
    )
    version = sv(logs)
    return '.'.join((str(v) for v in version))
