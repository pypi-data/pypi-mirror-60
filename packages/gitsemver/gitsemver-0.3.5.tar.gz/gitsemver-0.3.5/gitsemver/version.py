

class Versioner(object):

    def __init__(self, version: list=None):
        self._version = [0, 1, 0]

        if isinstance(version, (list, tuple)):
            if len(version) == 3:
                self._version = list(version)
            else:
                raise ValueError(f'version must be list of length 3, got {version}')

    def bump(self, lvl: int):
        self._version[lvl] += 1
        self._version[lvl+1:] = [0]*(2-lvl)

    @property
    def version(self):
        return self._version
