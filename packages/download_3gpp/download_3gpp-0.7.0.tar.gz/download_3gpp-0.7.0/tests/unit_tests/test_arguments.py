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

from download_3gpp.options import DEFAULT_URL, UserOptions


class TestUserOptions:
    def test_defaults(self):
        under_test = UserOptions()

        under_test.parse_arguments(list())

        assert under_test.base_url == DEFAULT_URL
        assert under_test.destination == "."
        assert under_test.rel is None
        assert under_test.series is None
        assert under_test.std is None

    def test_base_url(self):
        arguments = [
            "--base-url",
            "some/url",
        ]

        under_test = UserOptions()
        under_test.parse_arguments(arguments)

        assert under_test.base_url == arguments[1]

    def test_destination(self):
        arguments = [
            "--destination",
            "some/path",
        ]

        under_test = UserOptions()
        under_test.parse_arguments(arguments)

        assert under_test.destination == arguments[1]

    def test_rel(self):
        arguments = [
            "--rel",
            "16",
        ]

        under_test = UserOptions()
        under_test.parse_arguments(arguments)

        assert under_test.rel == int(arguments[1])

    def test_series(self):
        arguments = [
            "--series",
            "25",
        ]

        under_test = UserOptions()
        under_test.parse_arguments(arguments)

        assert under_test.series == int(arguments[1])

    def test_std(self):
        arguments = [
            "--std",
            "123",
        ]

        under_test = UserOptions()
        under_test.parse_arguments(arguments)

        assert under_test.std == arguments[1]
