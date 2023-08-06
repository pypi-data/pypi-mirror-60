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

import pytest_mock

# DO NOT DELETE! Used by mocker.patch below
import download_3gpp.entrypoint
from download_3gpp.entrypoint import main


class TestMain:
    def test_execution(self, mocker):
        arguments = ["--base-url", "some/url"]

        mock_downloader = mocker.patch("download_3gpp.entrypoint.Downloader")
        mock_user_options = mocker.patch("download_3gpp.entrypoint.UserOptions")

        main(arguments)

        mock_options_instance = mock_user_options.return_value
        mock_options_instance.parse_arguments.assert_called_once_with(arguments)

        mock_downloader.assert_called_once_with(mock_user_options.return_value)
        mock_downloader.return_value.get_files.assert_called_once()
