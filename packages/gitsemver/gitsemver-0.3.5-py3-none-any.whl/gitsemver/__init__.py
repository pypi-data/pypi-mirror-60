from .index import semver
from .config import Config
from pathlib import Path
from subprocess import run, PIPE


def main():
    logs = run(['git', 'log'], stdout=PIPE, stderr=PIPE).stdout.decode()
    config = Config.from_yaml(Path.cwd() / 'gitsemver.yml')
    print(semver(logs, config))
