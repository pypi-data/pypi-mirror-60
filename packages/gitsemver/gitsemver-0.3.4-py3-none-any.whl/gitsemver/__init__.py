from .index import semver
from .config import Config
from pathlib import Path
from subprocess import run


def main():
    logs = run(['git', 'log'], capture_output=True).stdout.decode()
    config = Config.from_yaml(Path.cwd() / 'gitsemver.yml')
    print(semver(logs, config))
