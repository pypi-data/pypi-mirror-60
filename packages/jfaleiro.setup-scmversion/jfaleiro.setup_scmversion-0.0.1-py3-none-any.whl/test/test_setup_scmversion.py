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

import unittest

from setup_scmversion import ScmParser, version


class Test(unittest.TestCase):

    def testVersion(self):
        self.assertIsNotNone(version())

    def testInvalidParser(self):
        with self.assertRaises(ValueError):
            version(scm='invalid_parser')

    def testDefaultParserIsGit(self):
        self.assertEqual(version(), version(scm='git'))

    def testBuildVersion(self):
        self.assertEqual(ScmParser.build_version('release/0.0.1', '12', None),
                         '0.0.1.dev12')
        self.assertEqual(ScmParser.build_version('release/0.0.1', '12', ''),
                         '0.0.1.dev12')
        self.assertEqual(ScmParser.build_version('master', '12', '0.0.1'),
                         '0.0.1')
        self.assertEqual(ScmParser.build_version('master', '12', None),
                         'master.dev12')
        self.assertEqual(ScmParser.build_version('master', '12', ''),
                         'master.dev12')

    def testParser(self):
        v = version()
        self.assertTrue(v.startswith('master') or v[0].isnumeric())


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
