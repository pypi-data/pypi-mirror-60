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

from download_3gpp.download import extract_base_network_location


class TestBaseNetworkLocation:
    def test_default_url(self):
        url_text = "https://www.3gpp.org/ftp/Specs/latest/"

        actual_text = extract_base_network_location(url_text)

        assert actual_text == "https://www.3gpp.org/"
