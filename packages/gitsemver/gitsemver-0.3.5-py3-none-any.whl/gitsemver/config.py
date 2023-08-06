from yaml import safe_load
from collections import OrderedDict
import attr as a


@a.s(auto_attribs=True)
class Config(object):

    major: str
    minor: str
    patch: str

    @classmethod
    def from_yaml(cls, path: str):
        with open(path, 'r') as f:
            return cls(**safe_load(f))

    def to_list(self) -> list:
        return [self.major, self.minor, self.patch]

    def to_dict(self) -> dict:
        return OrderedDict({
            ('patch', self.patch),
            ('minor', self.minor),
            ('major', self.major)
        })
