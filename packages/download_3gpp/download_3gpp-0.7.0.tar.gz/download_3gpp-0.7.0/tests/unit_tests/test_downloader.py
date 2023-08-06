#
# Copyright 2020 Russell Smiley
#
# This file is part of 3gpp_download.
#
# 3gpp_download is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 3gpp_download is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 3gpp_download.  If not, see <http://www.gnu.org/licenses/>.
#

import re

import pytest

# DO NOT DELETE! Used by mocker.patch below
import download_3gpp.download
from download_3gpp.download import Downloader
from download_3gpp.options import UserOptions


@pytest.fixture
def user_options() -> UserOptions:
    options = UserOptions()
    options.parse_arguments(list())

    return options


class TestDownloader:
    def test_get_rel_urls_fail(self, mocker, user_options: UserOptions):
        mocker.patch("download_3gpp.download.get_rel_urls", return_value=list())
        mocker.patch("download_3gpp.download.get_series_urls", return_value=list())
        mocker.patch("download_3gpp.download.get_std_urls", return_value=list())
        mocker.patch("download_3gpp.download.os.makedirs")
        mock_warning = mocker.patch("download_3gpp.download.log.warning")

        under_test = Downloader(user_options)
        under_test.get_files()

        warning_call_args = mock_warning.call_args

        assert (
            re.match(
                r"^Huh\. No releases found\. Are you sure you\'ve got the correct base "
                r"url\?",
                warning_call_args[0][0],
            )
            is not None
        )

    def test_get_series_urls_fail(self, mocker, user_options: UserOptions):
        mocker.patch(
            "download_3gpp.download.get_rel_urls",
            return_value=[("rel_basename", 15, "rel/path")],
        )
        mocker.patch("download_3gpp.download.get_series_urls", return_value=list())
        mocker.patch("download_3gpp.download.get_std_urls", return_value=list())
        mocker.patch("download_3gpp.download.os.makedirs")
        mock_warning = mocker.patch("download_3gpp.download.log.warning")

        under_test = Downloader(user_options)
        under_test.get_files()

        warning_call_args = mock_warning.call_args

        assert (
            re.match(
                r"^Huh\. No series found\. Does that make sense to you\?",
                warning_call_args[0][0],
            )
            is not None
        )

    def test_get_std_urls_fail(self, mocker, user_options: UserOptions):
        mocker.patch(
            "download_3gpp.download.get_rel_urls",
            return_value=[("rel_basename", 15, "rel/path")],
        )
        mocker.patch(
            "download_3gpp.download.get_series_urls",
            return_value=[("series_base", 25, "series/path")],
        )
        mocker.patch("download_3gpp.download.get_std_urls", return_value=list())
        mocker.patch("download_3gpp.download.os.makedirs")
        mock_warning = mocker.patch("download_3gpp.download.log.warning")

        under_test = Downloader(user_options)
        under_test.get_files()

        warning_call_args = mock_warning.call_args

        assert (
            re.match(
                r"^Hmm\. No standards found\. Does that make sense to you\?",
                warning_call_args[0][0],
            )
            is not None
        )

    def test_local_file_fail(self, mocker, user_options: UserOptions):
        mocker.patch(
            "download_3gpp.download.get_rel_urls",
            return_value=[("rel_basename", 15, "rel/path")],
        )
        mocker.patch(
            "download_3gpp.download.get_series_urls",
            return_value=[("series_base", 25, "series/path")],
        )
        mocker.patch(
            "download_3gpp.download.get_std_urls",
            return_value=[("file.zip", "std/path")],
        )
        mocker.patch("download_3gpp.download.os.makedirs")
        mocker.patch("download_3gpp.download.os.path.isfile", return_value=True)
        mock_warning = mocker.patch("download_3gpp.download.log.warning")

        under_test = Downloader(user_options)
        under_test.get_files()

        warning_call_args = mock_warning.call_args

        assert (
            re.match(r"^Skipping download of existing file", warning_call_args[0][0])
            is not None
        )

    def test_file_get(self, mocker, user_options: UserOptions):
        mocker.patch(
            "download_3gpp.download.get_rel_urls",
            return_value=[("rel_basename", 15, "rel/path")],
        )
        mocker.patch(
            "download_3gpp.download.get_series_urls",
            return_value=[("series_base", 25, "series/path")],
        )
        mocker.patch(
            "download_3gpp.download.get_std_urls",
            return_value=[("file.zip", "std/path")],
        )
        mocker.patch("download_3gpp.download.os.makedirs")
        mocker.patch("download_3gpp.download.os.path.isfile", return_value=False)
        mock_get = mocker.patch("download_3gpp.download.requests.get")

        open_mock_instance = mocker.mock_open()
        mocker.patch("download_3gpp.download.open", open_mock_instance, create=True)

        under_test = Downloader(user_options)
        under_test.get_files()

        mock_get.assert_called_once_with("std/path")
        handle = open_mock_instance()
        handle.write.assert_called_once_with(mock_get.return_value.content)
