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

# DO NOT DELETE! Used by mocker.patch below
import download_3gpp.download
from download_3gpp.download import get_index


class TestGetIndex:
    def test_get_index(self, mocker):
        expected_url = "https://www.3gpp.org/ftp/Specs/latest/"
        with mocker.patch(
            "download_3gpp.download.requests.get", return_value=mocker.MagicMock()
        ) as mock_requests_get:
            get_index(expected_url)

        assert mock_requests_get.called_once_with(mocker.call(expected_url))
