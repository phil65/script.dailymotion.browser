# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details


import xbmc
import xbmcgui

from kodi65 import windows
from kodi65 import addon
from kodi65 import utils
from kodi65 import player

LIST_XML = u'script-%s-VideoList.xml' % (addon.NAME)


class WindowManager(object):
    window_stack = []

    def __init__(self):
        self.active_dialog = None
        self.saved_background = addon.get_global("infobackground")
        self.saved_control = xbmc.getInfoLabel("System.CurrentControlId")
        self.saved_dialogstate = xbmc.getCondVisibility("Window.IsActive(Movieinformation)")
        # self.monitor = SettingsMonitor()
        self.busy = 0

    def open_video_list(self, listitems=None, filters=None, mode="filter", list_id=False,
                        filter_label="", force=False, media_type="movie", search_str=""):
        """
        open video list, deal with window stack
        """
        from dialogs import DialogVideoList
        Browser = DialogVideoList.get_window(windows.DialogXML)
        dialog = Browser(LIST_XML,
                         addon.PATH,
                         listitems=listitems,
                         filters=[] if not filters else filters,
                         mode=mode,
                         list_id=list_id,
                         force=force,
                         filter_label=filter_label,
                         search_str=search_str,
                         type=media_type)
        self.open_dialog(dialog)

    def open_dailymotion_list(self, search_str="", filters=None, sort="relevance",
                              filter_label="", media_type="video"):
        """
        open video list, deal with window stack
        """
        import dailymotionbrowser
        dialog = dailymotionbrowser.open()
        self.open_dialog(dialog)

    def open_infodialog(self, dialog):
        if dialog.info:
            self.open_dialog(dialog)
        else:
            self.active_dialog = None
            utils.notify(addon.LANG(32143))

    def open_dialog(self, dialog):
        if self.active_dialog:
            self.window_stack.append(self.active_dialog)
            self.active_dialog.close()
        utils.check_version()
        if not addon.setting("first_start_infodialog"):
            addon.set_setting("first_start_infodialog", "True")
            xbmcgui.Dialog().ok(heading=addon.NAME,
                                line1=addon.LANG(32140),
                                line2=addon.LANG(32141))
        self.active_dialog = dialog
        dialog.doModal()
        if dialog.cancelled:
            addon.set_global("infobackground", self.saved_background)
            self.window_stack = []
            return None
        if self.window_stack:
            self.active_dialog = self.window_stack.pop()
            xbmc.sleep(300)
            self.active_dialog.doModal()
        else:
            addon.set_global("infobackground", self.saved_background)

    def play_youtube_video(self, youtube_id="", listitem=None):
        """
        play youtube vid with info from *listitem
        """
        url, yt_listitem = player.youtube_info_by_id(youtube_id)
        if not listitem:
            listitem = yt_listitem
        if not url:
            utils.notify(header=addon.LANG(257),
                         message="no youtube id found")
            return None
        if self.active_dialog and self.active_dialog.window_type == "dialog":
            self.active_dialog.close()
        xbmc.executebuiltin("Dialog.Close(movieinformation)")
        xbmc.Player().play(item=url,
                           listitem=listitem,
                           windowed=False,
                           startpos=-1)
        if self.active_dialog and self.active_dialog.window_type == "dialog":
            player.wait_for_video_end()
            self.active_dialog.doModal()

    def show_busy(self):
        if self.busy == 0:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.busy += 1

    def hide_busy(self):
        self.busy = max(0, self.busy - 1)
        if self.busy == 0:
            xbmc.executebuiltin("Dialog.Close(busydialog)")

wm = WindowManager()
