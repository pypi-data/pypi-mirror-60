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
from download_3gpp.download import get_rel_urls

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture
def html_data() -> str:
    with open(os.path.join(DATA_DIR, "latest_index.html"), "r") as this_file:
        mock_rel_data = this_file.read()

    return mock_rel_data


class TestLatestSoup:
    def test_get_all_urls(self, mocker, html_data: str):
        mocker.patch("download_3gpp.download.get_index", return_value=html_data)
        result = get_rel_urls("https://www.3gpp.org/some/url", None)

        assert [x.basename for x in result] == [
            "Rel-10",
            "Rel-11",
            "Rel-12",
            "Rel-13",
            "Rel-14",
            "Rel-15",
            "Rel-16",
            "Rel-17",
            "Rel-8",
            "Rel-9",
        ]
        assert [x.value for x in result] == [10, 11, 12, 13, 14, 15, 16, 17, 8, 9]
        assert [x.url for x in result] == [
            "https://www.3gpp.org/ftp/Specs/latest/Rel-10/",
            "https://www.3gpp.org/ftp/Specs/latest/Rel-11/",
            "https://www.3gpp.org/ftp/Specs/latest/Rel-12/",
            "https://www.3gpp.org/ftp/Specs/latest/Rel-13/",
            "https://www.3gpp.org/ftp/Specs/latest/Rel-14/",
            "https://www.3gpp.org/ftp/Specs/latest/Rel-15/",
            "https://www.3gpp.org/ftp/Specs/latest/Rel-16/",
            "https://www.3gpp.org/ftp/Specs/latest/Rel-17/",
            "https://www.3gpp.org/ftp/Specs/latest/Rel-8/",
            "https://www.3gpp.org/ftp/Specs/latest/Rel-9/",
        ]

    def test_get_specific_url(self, mocker, html_data: str):
        mocker.patch("download_3gpp.download.get_index", return_value=html_data)
        result = get_rel_urls("https://www.3gpp.org/some/url", 16)

        assert [x.basename for x in result] == ["Rel-16"]
        assert [x.value for x in result] == [16]
        assert [x.url for x in result] == [
            "https://www.3gpp.org/ftp/Specs/latest/Rel-16/"
        ]
