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

SEMANTIC_PATTERN = r"\d+\.\d+\.\d+"
SEMANTIC_RELEASE_PATTERN = r"^{0}$".format(SEMANTIC_PATTERN)
DRYRUN_SUFFIX_PATTERN = r"^({0})-dryrun\d*$".format(SEMANTIC_PATTERN)


def main():
    pipeline_id = sys.argv[1]
    ref_name = sys.argv[2]

    dryrun_result = re.search(DRYRUN_SUFFIX_PATTERN, ref_name)
    if re.search(SEMANTIC_RELEASE_PATTERN, ref_name) is not None:
        # Semantic release tag, so just propagate the semantic release
        print("{0}".format(ref_name))
    elif dryrun_result is not None:
        # Release dry run tag, so propagate the semantic version with the pipeline id
        print("{0}.{1}".format(dryrun_result.group(1), pipeline_id))
    else:
        # Just use the pipeline id
        print("0.0.0.{0}".format(pipeline_id))


if __name__ == "__main__":
    main()
