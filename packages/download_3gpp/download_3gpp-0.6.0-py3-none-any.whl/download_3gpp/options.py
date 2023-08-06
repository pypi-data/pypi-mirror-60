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

import argparse
import typing

DEFAULT_URL = "https://www.3gpp.org/ftp/Specs/latest/"


class UserOptions:
    def __init__(self):
        self.__parsed_arguments = None

        self.__parser = argparse.ArgumentParser(
            description="Acquire 3GPP standards packages from archive"
        )

        self.__parser.add_argument(
            "--base-url",
            default=DEFAULT_URL,
            type=str,
            help='Base 3GPP download URL to target, default "{0}"'.format(DEFAULT_URL),
        )

        self.__parser.add_argument(
            "--destination",
            default=".",
            type=str,
            help='Destination download directory, default "./"',
        )

        self.__parser.add_argument(
            "--rel",
            default=None,
            type=int,
            help='3GPP release number to target, default "all"',
        )

        self.__parser.add_argument(
            "--series",
            default=None,
            type=int,
            help='3GPP series number to target, default "all"',
        )

        self.__parser.add_argument(
            "--std",
            default=None,
            type=str,
            help='3GPP standard number to target, default "all"',
        )

    def __getattr__(self, item: str) -> typing.Union[str, int]:
        value = getattr(self.__parsed_arguments, item)

        return value

    def parse_arguments(self, command_line_arguments: typing.List[str]):
        self.__parsed_arguments = self.__parser.parse_args(command_line_arguments)
