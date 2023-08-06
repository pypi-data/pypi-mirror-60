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

import os.path

import pytest

# DO NOT DELETE! Use by mocker.patch below
import download_3gpp.download
from download_3gpp.download import get_std_urls

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture
def html_data() -> str:
    with open(os.path.join(DATA_DIR, "25_series_index.html"), "r") as this_file:
        mock_rel_data = this_file.read()

    return mock_rel_data


class TestSeriesSoup:
    def test_get_all_urls(self, mocker, html_data: str):
        mocker.patch("download_3gpp.download.get_index", return_value=html_data)
        result = get_std_urls("https://www.3gpp.org/some/url", 25, None)

        expected_files = [
            "25101-g10.zip",
            "25104-g00.zip",
            "25123-g00.zip",
            "25133-g00.zip",
            "25141-g00.zip",
        ]
        assert [x.file for x in result] == expected_files

        expected_urls = [
            "https://www.3gpp.org/ftp/Specs/latest/Rel-16/25_series/{0}".format(x)
            for x in expected_files
        ]
        assert [x.url for x in result] == expected_urls

    def test_get_specific_url(self, mocker, html_data: str):
        mocker.patch("download_3gpp.download.get_index", return_value=html_data)
        result = get_std_urls("https://www.3gpp.org/some/url", 25, "104")

        expected_files = ["25104-g00.zip"]
        assert [x.file for x in result] == expected_files
        assert [x.url for x in result] == [
            "https://www.3gpp.org/ftp/Specs/latest/Rel-16/25_series/25104-g00.zip",
        ]
