# -*- coding: utf8 -*-

# Copyright (C) 2016 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import datetime

from resources.lib import dailymotion
from kodi65 import utils
from kodi65 import ItemList
from kodi65 import VideoItem

video_infos = ["aspect_ratio", "audience", "available_formats", "created_time", "duration", "description",
               "genre", "id", "embed_url", "stream_h264_hd1080_url", "thumbnail_720_url", "title", "views_total"]

d = dailymotion.Dailymotion()


def handle_videos(results):
    listitems = ItemList(content_type="videos")
    for item in results:
        listitem = VideoItem(label=item.get('title'),
                             artwork={'thumb': item.get("thumbnail_720_url")})
        date = datetime.datetime.fromtimestamp(int(item.get('created_time'))).strftime('%Y-%m-%d')
        listitem.set_infos({'mediatype': "video",
                            "duration": item.get("duration"),
                            "premiered": date})
        listitem.set_properties({'genre': item.get('genre'),
                                 'youtube_id': item.get('key'),
                                 'duration': utils.format_seconds(item.get("duration")),
                                 'id': item.get('embed_url')})
        listitems.append(listitem)
    return listitems


def explore(search_str="", hd="", orderby="recent", limit=40, extended=True, page="", filters=None, media_type="video"):
    params = {"page": page,
              "fields": ",".join(video_infos),
              "limit": limit,
              "sort": orderby,
              "search": search_str}
    params = utils.merge_dicts(params, filters if filters else {})
    params = {k: v for k, v in params.iteritems() if v}
    params = ["%s=%s" % (k, v) for k, v in params.iteritems()]
    params = "&".join(params)
    videos = d.get("/videos?%s" % (params))
    utils.pp(videos)
    listitems = handle_videos(videos["list"])
    totals = videos.get("total", len(listitems))
    listitems.set_totals(totals)
    listitems.set_total_pages(totals / limit)
    return listitems
