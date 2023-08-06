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

DEFAULT_URL: str

class UserOptions:
    __parsed_arguments: typing.Optional[typing.Any]
    __parser: typing.Any
    def __init__(self): ...
    def __getattr__(self, item: str) -> typing.Union[str, int]: ...
    def parse_arguments(self, command_line_arguments: typing.List[str]): ...
    # BEGIN TYPE HINTING PROPERTIES
    # The following properties are made available via ``UserOptions.__getattr__`` but are defined
    # explicitly in this stub file to enable hinting in an IDE.
    @property
    def base_url(self) -> str: ...
    @property
    def destination(self) -> str: ...
    @property
    def rel(self) -> int: ...
    @property
    def series(self) -> int: ...
    @property
    def std(self) -> str: ...
