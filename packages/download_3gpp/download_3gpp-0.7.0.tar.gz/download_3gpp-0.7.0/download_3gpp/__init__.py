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

"""Command line utility for downloading standards documents from the 3GPP download site."""

import os.path

here = os.path.abspath(os.path.dirname(__file__))
version_file_path = os.path.abspath(os.path.join(here, "VERSION"))

with open(version_file_path) as version_file:
    version = version_file.read().strip()

__version__ = version
