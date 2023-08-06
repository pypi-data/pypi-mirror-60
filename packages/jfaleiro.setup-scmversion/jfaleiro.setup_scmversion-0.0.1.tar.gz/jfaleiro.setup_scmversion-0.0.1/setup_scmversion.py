#
#  setup_scmversion - Builds a pythonic version number sbased on scm tags and branches.
#
#  Copyright (C) 2019 Jorge M. Faleiro Jr.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import logging
import subprocess
from abc import ABC, abstractmethod
from functools import lru_cache


def execute_command(command):
    return subprocess.check_output(command.split()).strip().decode('ascii')


class ScmParser(ABC):

    @property
    @lru_cache()
    def branch(self) -> str:
        return self._branch()

    @property
    @lru_cache()
    def commits(self) -> str:
        return self._commits()

    @property
    @lru_cache()
    def tag(self) -> str:
        return self._tag()

    @staticmethod
    def build_version(branch: str, commits: str, tag: str) -> str:
        if branch == 'master':
            if tag is None or len(tag.strip()) == 0:
                return 'master.dev%s' % commits
            else:
                return tag
        elif branch.startswith('release/'):
            return branch.split('/')[-1] + '.dev%s' % commits
        else:
            return 'no_version.dev%s' % commits

    def parse(self) -> str:
        return ScmParser.build_version(self.branch, self.commits, self.tag)

    @abstractmethod
    def _branch(self) -> str:
        pass

    @abstractmethod
    def _tag(self) -> str:
        pass

    @abstractmethod
    def _commits(self) -> str:
        pass


class GitParser(ScmParser):
    def _branch(self):
        return execute_command('git rev-parse --abbrev-ref HEAD')

    def _commits(self):
        return execute_command('git rev-list --count %s' % self.branch)

    def _tag(self):
        try:
            tag = execute_command('git describe --tags --abbrev=0')
            # check for tag out of the ordinary, i.e.
            # fatal: No names found, cannot describe anything.
            if tag.startswith('fatal:'):
                logging.info('no tags (release branch?): %s' % tag)
                tag = None
        except subprocess.CalledProcessError as _:
            logging.info('cannot describe tag, will use None')
            tag = None
        return tag


PARSERS = dict(
    git=GitParser(),
)


def version(scm: str = 'git') -> str:
    """builds a version number based on information on the scm"""
    if scm not in PARSERS:
        raise ValueError("scm '%s' invalid (options: %s)" %
                         (scm, PARSERS.keys()))
    return PARSERS[scm].parse()


def main():
    print(version())
