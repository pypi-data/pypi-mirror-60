#
# Copyright 2020 Russell Smiley
#
# This file is part of download_3gpp.
#
# download_3gpp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# download_3gpp is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with download_3gpp.  If not, see <http://www.gnu.org/licenses/>.
#

from urllib.parse import urlparse

from download_3gpp.download import url_basename


class TestUrlBasename:
    def test_dirname_no_slash(self):
        u = urlparse("https://www.somewhere/some/path")

        actual = url_basename(u)

        assert actual == "path"

    def test_dirname_end_slash(self):
        u = urlparse("https://www.somewhere/some/path/")

        actual = url_basename(u)

        assert actual == "path"

    def test_filename(self):
        u = urlparse("https://www.somewhere/some/path/some.zip")

        actual = url_basename(u)

        assert actual == "some.zip"
