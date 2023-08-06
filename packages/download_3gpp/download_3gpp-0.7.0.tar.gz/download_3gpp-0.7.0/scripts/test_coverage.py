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
import sys


def main():
    coverage_threshold = int(sys.argv[1])

    current_coverage = 0
    lines = sys.stdin.readlines()
    for this_line in lines:
        match_result = re.search(
            r"^.*((TOTAL)|((T|t)otal)).*\s+(\d{1,3})%.*$", this_line
        )
        if match_result is not None:
            current_coverage = int(match_result.group(5))

    if current_coverage < coverage_threshold:
        sys.exit(
            "FAILED: coverage threshold {0} (current) < {1} (threshold)".format(
                current_coverage, coverage_threshold
            )
        )


if __name__ == "__main__":
    main()
