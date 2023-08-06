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

import logging
import sys
import typing

from .download import Downloader
from .options import UserOptions

log = logging.getLogger(__name__)


def main(command_line_arguments: typing.List[str]):
    try:
        user_options = UserOptions()

        user_options.parse_arguments(command_line_arguments)

        this_download = Downloader(user_options)
        this_download.get_files()
    except KeyboardInterrupt:
        log.warning("Aborting program due to keyboard interrupt.")


def flit_entry():
    main(sys.argv[1:])
