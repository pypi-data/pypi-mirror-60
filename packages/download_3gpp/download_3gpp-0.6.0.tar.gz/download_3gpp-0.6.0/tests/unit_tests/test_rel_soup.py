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
from download_3gpp.download import get_series_urls

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture
def html_data() -> str:
    with open(os.path.join(DATA_DIR, "rel16_index.html"), "r") as this_file:
        mock_rel_data = this_file.read()

    return mock_rel_data


class TestRelSoup:
    def test_get_all_urls(self, mocker, html_data: str):
        mocker.patch("download_3gpp.download.get_index", return_value=html_data)
        result = get_series_urls("https://www.3gpp.org/some/url", None)

        expected_values = list(range(21, 39)) + list(range(41, 53)) + [55]
        assert [x.value for x in result] == expected_values

        expected_basenames = ["{0}_series".format(x) for x in expected_values]
        assert [x.basename for x in result] == expected_basenames

        expected_urls = [
            "https://www.3gpp.org/ftp/Specs/latest/Rel-16/{0}/".format(x)
            for x in expected_basenames
        ]
        assert [x.url for x in result] == expected_urls

    def test_get_specific_url(self, mocker, html_data: str):
        mocker.patch("download_3gpp.download.get_index", return_value=html_data)
        result = get_series_urls("https://www.3gpp.org/some/url", 25)

        assert [x.value for x in result] == [25]
        assert [x.basename for x in result] == ["25_series"]
        assert [x.url for x in result] == [
            "https://www.3gpp.org/ftp/Specs/latest/Rel-16/25_series/"
        ]
