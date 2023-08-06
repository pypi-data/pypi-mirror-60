# -*- coding: utf-8 -*-
"""Module to download a complete playlist from a youtube channel"""

import json
import logging
import re
from collections import OrderedDict
from datetime import date, datetime
from typing import List, Optional, Iterable, Dict
from urllib.parse import parse_qs

from pytube import request, YouTube
from pytube.helpers import cache, deprecated
from pytube.mixins import install_proxy

logger = logging.getLogger(__name__)


class Playlist:
    """Handles all the task of manipulating and downloading a whole YouTube
    playlist
    """

    def __init__(self, url: str, proxies: Optional[Dict[str, str]] = None):
        if proxies:
            install_proxy(proxies)

        try:
            self.playlist_id: str = parse_qs(url.split("?")[1])["list"][0]
        except IndexError:  # assume that url is just the id
            self.playlist_id = url

        self.playlist_url: str = (
            "https://www.youtube.com/playlist?list=" + self.playlist_id
        )
        self.html = request.get(self.playlist_url)

        # Needs testing with non-English
        self.last_update: Optional[date] = None
        results = re.search(
            r"<li>Last updated on (\w{3}) (\d{1,2}), (\d{4})<\/li>", self.html
        )
        if results:
            month, day, year = results.groups()
            self.last_update = datetime.strptime(
                f"{month} {day:0>2} {year}", "%b %d %Y"
            ).date()

    @staticmethod
    def _find_load_more_url(req: str) -> Optional[str]:
        """Given an html page or a fragment thereof, looks for
        and returns the "load more" url if found.
        """
        match = re.search(
            r"data-uix-load-more-href=\"(/browse_ajax\?" 'action_continuation=.*?)"',
            req,
        )
        if match:
            return "https://www.youtube.com" + match.group(1)

        return None

    def parse_links(self, until_watch_id: Optional[str] = None) -> List[str]:
        """Parse the video links from the page source, extracts and
        returns the /watch?v= part from video link href
        """
        req = self.html

        # split the page source by line and process each line
        content = [x for x in req.split("\n") if "pl-video-title-link" in x]
        link_list = [x.split('href="', 1)[1].split("&", 1)[0] for x in content]

        # The above only returns 100 or fewer links
        # Simulating a browser request for the load more link
        load_more_url = self._find_load_more_url(req)
        while load_more_url:  # there is an url found
            if until_watch_id:
                try:
                    trim_index = link_list.index(f"/watch?v={until_watch_id}")
                    return link_list[:trim_index]
                except ValueError:
                    pass
            logger.debug("load more url: %s", load_more_url)
            req = request.get(load_more_url)
            load_more = json.loads(req)
            videos = re.findall(
                r"href=\"(/watch\?v=[\w-]*)", load_more["content_html"],
            )
            # remove duplicates
            link_list.extend(list(OrderedDict.fromkeys(videos)))
            load_more_url = self._find_load_more_url(
                load_more["load_more_widget_html"],
            )

        return link_list

    def trimmed(self, video_id: str) -> List[str]:
        """Retrieve a list of YouTube video URLs trimmed at the given video ID
        i.e. if the playlist has video IDs 1,2,3,4 calling trimmed(3) returns [1,2]
        :type video_id: str
            video ID to trim the returned list of playlist URLs at
        :rtype: List[str]
        :returns:
            List of video URLs from the playlist trimmed at the given ID
        """
        trimmed_watch = self.parse_links(until_watch_id=video_id)
        return [self._video_url(watch_path) for watch_path in trimmed_watch]

    @property  # type: ignore
    @cache
    def video_urls(self) -> List[str]:
        """Complete links of all the videos in playlist
        :rtype: List[str]
        :returns:
            List of video URLs
        """
        return [self._video_url(watch_path) for watch_path in self.parse_links()]

    @property
    def videos(self) -> Iterable[YouTube]:
        for url in self.video_urls:
            yield YouTube(url)

    @deprecated(
        "This call is unnecessary, you can directly access .video_urls or .videos"
    )
    def populate_video_urls(self) -> List[str]:
        """Complete links of all the videos in playlist
        :rtype: List[str]
        :returns:
            List of video URLs
        """

        return self.video_urls

    @deprecated("This function will be removed in the future.")
    def _path_num_prefix_generator(self, reverse=False):  # pragma: no cover
        """
        This generator function generates number prefixes, for the items
        in the playlist.
        If the number of digits required to name a file,is less than is
        required to name the last file,it prepends 0s.
        So if you have a playlist of 100 videos it will number them like:
        001, 002, 003 ect, up to 100.
        It also adds a space after the number.
        :return: prefix string generator : generator
        """
        digits = len(str(len(self.video_urls)))
        if reverse:
            start, stop, step = (len(self.video_urls), 0, -1)
        else:
            start, stop, step = (1, len(self.video_urls) + 1, 1)
        return (str(i).zfill(digits) for i in range(start, stop, step))

    @deprecated(
        "This function will be removed in the future. Please iterate through .videos"
    )
    def download_all(
        self,
        download_path: Optional[str] = None,
        prefix_number: bool = True,
        reverse_numbering: bool = False,
        resolution: str = "720p",
    ) -> None:  # pragma: no cover
        """Download all the videos in the the playlist. Initially, download
        resolution is 720p (or highest available), later more option
        should be added to download resolution of choice

        :param download_path:
            (optional) Output path for the playlist If one is not
            specified, defaults to the current working directory.
            This is passed along to the Stream objects.
        :type download_path: str or None
        :param prefix_number:
            (optional) Automatically numbers playlists using the
            _path_num_prefix_generator function.
        :type prefix_number: bool
        :param reverse_numbering:
            (optional) Lets you number playlists in reverse, since some
            playlists are ordered newest -> oldest.
        :type reverse_numbering: bool
        :param resolution:
            Video resolution i.e. "720p", "480p", "360p", "240p", "144p"
        :type resolution: str
        """

        logger.debug("total videos found: %d", len(self.video_urls))
        logger.debug("starting download")

        prefix_gen = self._path_num_prefix_generator(reverse_numbering)

        for link in self.video_urls:
            youtube = YouTube(link)
            dl_stream = (
                youtube.streams.get_by_resolution(resolution=resolution)
                or youtube.streams.get_lowest_resolution()
            )
            assert dl_stream is not None

            logger.debug("download path: %s", download_path)
            if prefix_number:
                prefix = next(prefix_gen)
                logger.debug("file prefix is: %s", prefix)
                dl_stream.download(download_path, filename_prefix=prefix)
            else:
                dl_stream.download(download_path)
            logger.debug("download complete")

    @cache
    def title(self) -> Optional[str]:
        """return playlist title (name)"""
        open_tag = "<title>"
        end_tag = "</title>"
        pattern = re.compile(open_tag + "(.+?)" + end_tag)
        match = pattern.search(self.html)

        if match is None:
            return None

        return (
            match.group()
            .replace(open_tag, "")
            .replace(end_tag, "")
            .replace("- YouTube", "")
            .strip()
        )

    @staticmethod
    def _video_url(watch_path: str):
        return f"https://www.youtube.com{watch_path}"
