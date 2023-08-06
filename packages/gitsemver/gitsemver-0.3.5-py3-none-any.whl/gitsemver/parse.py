import re
from .config import Config
import attr as a


class ParseError(Exception):
    pass


@a.s(auto_attribs=True)
class LogParser(object):

    config: Config

    @property
    def commit_match(self):
        return re.compile(f'\\n\\n\\s{{4}}({self.config.major}|{self.config.minor}|{self.config.patch}).*\\n\\n')

    @property
    def patterns(self) -> list:
        return [re.compile(v) for v in self.config.to_list()]

    def map_log(self, log: str) -> int:
        for i, v in enumerate(self.patterns):
            if v.match(log):
                return i
        else:
            raise ParseError(
                f"log {log} extracted in search, but not matched in translation to version level - "
                f"this shouldn't happen."
            )

    def parse_commits(self, logs: str):
        commits = self.commit_match.findall(logs)
        commits = [c[0] if isinstance(c, tuple) else c for c in commits]
        return reversed(list(map(self.map_log, commits)))

