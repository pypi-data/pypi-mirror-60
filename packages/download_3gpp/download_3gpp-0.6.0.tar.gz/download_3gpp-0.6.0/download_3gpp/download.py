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

import collections
import logging
import os.path
import re
import typing
from urllib.parse import ParseResult, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .options import UserOptions

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def extract_base_network_location(url_text: str) -> str:
    u = urlparse(url_text)

    return "{0}://{1}/".format(u.scheme, u.netloc)


UrlBasenameData = collections.namedtuple("UrlBasename", ["basename", "value", "url"])


def get_index(url_text: str) -> str:
    """
    Get the index.html document.

    :param url: URL, *not including index.html*

    :return: Requests HTML content
    """
    r = requests.get(url_text)

    return r.content


def get_urls(this_soup: BeautifulSoup) -> typing.List[ParseResult]:
    this_urls = list()
    for link in this_soup.find_all("a"):
        this_urls.append(urlparse(link.get("href")))

    return this_urls


def url_basename(this_url: ParseResult) -> str:
    first_basename = os.path.basename(this_url.path)
    if not first_basename:
        # URLs could have a trailing '/' which has to be dealt with
        return_basename = os.path.basename(os.path.dirname(this_url.path))
    else:
        return_basename = first_basename

    return return_basename


def get_patterned_urls(
    index_url: str, regex_pattern: str
) -> typing.List[UrlBasenameData]:
    """
    Recover URL base data from the specified pattern. Assumes there is an integer value specified
    in ``regex_pattern`` that must also be recovered for the URL "value".

    :param index_soup:
    :param regex_pattern:

    :return: List of extracted data.
    """
    index_soup = BeautifulSoup(get_index(index_url), "html.parser")
    page_urls = get_urls(index_soup)

    filtered_urls = list()
    for this_url in page_urls:
        this_basename = url_basename(this_url)
        match_result = re.match(regex_pattern, this_basename)

        if match_result is not None:
            this_value = int(match_result.group(1))

            this_result = UrlBasenameData(
                basename=this_basename, value=this_value, url=this_url
            )

            filtered_urls.append(this_result)

    return filtered_urls


def get_rel_urls(
    base_page_url: str, user_rel: typing.Optional[int]
) -> typing.List[UrlBasenameData]:
    host = extract_base_network_location(base_page_url)

    # Return all results if user_rel is none, otherwise filter for user_rel.
    return [
        UrlBasenameData(
            basename=x.basename, value=x.value, url=urljoin(host, x.url.path)
        )
        for x in get_patterned_urls(base_page_url, r"^Rel-(\d+)")
        if ((user_rel is not None) and (x.value == user_rel)) or (user_rel is None)
    ]


def get_series_urls(
    rel_page_url: str, user_series: typing.Optional[int]
) -> typing.List[UrlBasenameData]:
    host = extract_base_network_location(rel_page_url)

    # Return all results if user_series is none, otherwise filter for user_series.
    return [
        UrlBasenameData(
            basename=x.basename, value=x.value, url=urljoin(host, x.url.path)
        )
        for x in get_patterned_urls(rel_page_url, r"^(\d+)_series")
        if ((user_series is not None) and (x.value == user_series))
        or (user_series is None)
    ]


StdUrlData = collections.namedtuple("StdUrlData", ["file", "url"])


def get_std_urls(
    series_page_url: str, series_number: int, user_std: typing.Optional[str]
) -> typing.List[StdUrlData]:
    host = extract_base_network_location(series_page_url)
    series_soup = BeautifulSoup(get_index(series_page_url), "html.parser")
    file_urls = get_urls(series_soup)

    filtered_urls = list()
    for this_url in file_urls:
        this_basename = url_basename(this_url)
        match_result = re.match(
            r"^{0}(\d+).*\.zip".format(series_number), this_basename
        )

        if match_result is not None:
            if ((user_std is not None) and (match_result.group(1) == user_std)) or (
                user_std is None
            ):
                this_result = StdUrlData(
                    file=this_basename, url=urljoin(host, this_url.path)
                )

                filtered_urls.append(this_result)
    return filtered_urls


class Downloader:
    def __init__(self, user_options: UserOptions):
        self.__user_options = user_options

    def get_files(self):
        rel_url_data = get_rel_urls(
            self.__user_options.base_url, self.__user_options.rel
        )
        if not rel_url_data:
            log.warning(
                "Huh. No releases found. Are you sure you've got the correct base url?, "
                "{0}".format(self.__user_options.base_url)
            )

        for rel_basename, rel_number, rel_url in rel_url_data:
            this_series_url_data = get_series_urls(rel_url, self.__user_options.series)
            if not this_series_url_data:
                log.warning(
                    "Huh. No series found. Does that make sense to you?, "
                    "{0}".format(rel_url)
                )

            for series_basename, series_number, series_url in this_series_url_data:
                std_url_data = get_std_urls(
                    series_url, series_number, self.__user_options.std
                )
                if not std_url_data:
                    log.warning(
                        "Hmm. No standards found. Does that make sense to you?, "
                        "{0}".format(series_url)
                    )

                for std_file, std_url in std_url_data:
                    local_std_path = os.path.join(
                        self.__user_options.destination,
                        rel_basename,
                        series_basename,
                        std_file,
                    )

                    # Ensure the directory for the file exists, and all intermediate directories.
                    os.makedirs(os.path.dirname(local_std_path), exist_ok=True)

                    if not os.path.isfile(local_std_path):
                        log.info("Downloading file, {0}".format(std_url))
                        r = requests.get(std_url)
                        open(local_std_path, "wb").write(r.content)
                    else:
                        log.warning(
                            "Skipping download of existing file, {0}, {1}".format(
                                std_url, local_std_path
                            )
                        )
