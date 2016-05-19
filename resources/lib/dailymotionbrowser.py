# -*- coding: utf8 -*-

# Copyright (C) 2016 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details


import xbmcgui

# from resources.lib.WindowManager import wm

from kodi65 import DialogBaseList
from kodi65 import addon
from kodi65 import utils
from kodi65 import windows
from kodi65 import ActionHandler
from kodi65 import busy
import dailymotionutils as dm
from windowmanager import wm
ch = ActionHandler()

ID_BUTTON_SORTTYPE = 5001
ID_BUTTON_PUBLISHEDFILTER = 5002
ID_BUTTON_LANGUAGEFILTER = 5003
ID_BUTTON_DIMENSIONFILTER = 5006
ID_BUTTON_DURATIONFILTER = 5008
ID_BUTTON_CAPTIONFILTER = 5009
ID_BUTTON_DEFINITIONFILTER = 5012
ID_BUTTON_TYPEFILTER = 5013


def get_window(window_type):

    class DialogDailyMotionList(DialogBaseList, window_type):

        TYPES = ["video", "playlist", "channel"]

        FILTERS = {"has_game": addon.LANG(19029),
                   "hd": "HD",
                   "featured": "Featured"}

        TRANSLATIONS = {"video": addon.LANG(157),
                        "playlist": addon.LANG(559),
                        "channel": addon.LANG(19029)}

        SORTS = {"video": {"recent": addon.LANG(552),
                           "ranking": addon.LANG(563),
                           "relevance": addon.LANG(32060)}}

        LABEL2 = {"recent": lambda x: x.get_property("recent"),
                  "ranking": lambda x: x.get_property("relevance"),
                  "relevance": lambda x: x.get_info("relevance")}

        @busy.set_busy
        def __init__(self, *args, **kwargs):
            self.type = kwargs.get('type', "video")
            super(DialogDailyMotionList, self).__init__(*args, **kwargs)

        def onClick(self, control_id):
            super(DialogDailyMotionList, self).onClick(control_id)
            ch.serve(control_id, self)

        def onAction(self, action):
            super(DialogDailyMotionList, self).onAction(action)
            ch.serve_action(action, self.getFocusId(), self)

        @ch.click_by_type("video")
        def main_list_click(self, control_id):
            listitem = self.FocusedItem(control_id)
            media_id = listitem.getProperty("id")
            wm.play_youtube_video(youtube_id=media_id,
                                  listitem=listitem)

        @ch.click(ID_BUTTON_LANGUAGEFILTER)
        def set_featured_filter(self, control_id):
            options = [("1", "Yes"),
                       ("0", "No"),
                       ("", "Any")]
            self.choose_filter("featured", 32151, options)

        @ch.click(ID_BUTTON_LANGUAGEFILTER)
        def set_game_filter(self, control_id):
            options = [("1", "Yes"),
                       ("0", "No"),
                       ("", "Any")]
            self.choose_filter("has_game", 32151, options)

        @ch.click(ID_BUTTON_DEFINITIONFILTER)
        def set_definition_filter(self, control_id):
            options = [("true", addon.LANG(419)),
                       ("false", addon.LANG(602)),
                       ("", addon.LANG(593))]
            self.choose_filter("hd", 169, options)

        @ch.click(ID_BUTTON_SORTTYPE)
        def get_sort_type(self, control_id):
            if not self.choose_sort_method(self.type):
                return None
            self.update()

        @ch.context("video")
        def context_menu(self, control_id):
            listitem = self.FocusedItem(control_id)
            if self.type == "video":
                more_vids = "{} [B]{}[/B]".format(addon.LANG(32081),
                                                  listitem.getProperty("channel_title"))
                index = xbmcgui.Dialog().contextmenu(list=[addon.LANG(32069), more_vids])
                if index < 0:
                    return None
                elif index == 0:
                    filter_ = [{"id": listitem.getProperty("youtube_id"),
                                "type": "relatedToVideoId",
                                "label": listitem.getLabel()}]
                    wm.open_youtube_list(filters=filter_)
                elif index == 1:
                    filter_ = [{"id": listitem.getProperty("channel_id"),
                                "type": "channelId",
                                "label": listitem.getProperty("channel_title")}]
                    wm.open_youtube_list(filters=filter_)

        def update_ui(self):
            is_video = self.type == "video"
            self.getControl(ID_BUTTON_DIMENSIONFILTER).setVisible(is_video)
            self.getControl(ID_BUTTON_DURATIONFILTER).setVisible(is_video)
            self.getControl(ID_BUTTON_CAPTIONFILTER).setVisible(is_video)
            self.getControl(ID_BUTTON_DEFINITIONFILTER).setVisible(is_video)
            super(DialogDailyMotionList, self).update_ui()

        @property
        def default_sort(self):
            return "recent"

        def add_filter(self, **kwargs):
            kwargs["typelabel"] = self.FILTERS[kwargs["key"]]
            super(DialogDailyMotionList, self).add_filter(force_overwrite=True,
                                                          **kwargs)

        def fetch_data(self, force=False):
            self.set_filter_label()
            # if self.search_str:
            #     self.filter_label = addon.LANG(32146) % (self.search_str) + "  " + self.filter_label
            return dm.explore(search_str=self.search_str,
                              orderby=self.sort,
                              filters={item["type"]: item["id"] for item in self.filters},
                              media_type=self.type,
                              page=self.page)

    return DialogDailyMotionList


def open(search_str="", filters=None, sort="recent", filter_label="", media_type="video"):
    """
    open video list, deal with window stack
    """
    DailyMotion = get_window(windows.DialogXML)
    dialog = DailyMotion(u'script-%s-YoutubeList.xml' % addon.ID, addon.PATH,
                         search_str=search_str,
                         filters=[] if not filters else filters,
                         filter_label=filter_label,
                         type=media_type)
    return dialog
