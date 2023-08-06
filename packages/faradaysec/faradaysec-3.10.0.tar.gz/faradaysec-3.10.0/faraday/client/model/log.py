#!/usr/bin/env python
"""
Faraday Penetration Test IDE
Copyright (C) 2013  Infobyte LLC (http://www.infobytesec.com/)
See the file 'doc/LICENSE' for the license information

"""
from __future__ import absolute_import

import logging
from faraday.client.gui.customevents import (ShowPopupCustomEvent,
                              ShowDialogCustomEvent)
import faraday.client.model.guiapi
from faraday.config.configuration import getInstanceConfiguration

CONF = getInstanceConfiguration()

__notifier = None


def getNotifier(singleton=True):
    global __notifier
    if singleton:
        if __notifier is None:
            __notifier = Notifier()
        return __notifier
    else:
        return Notifier()


class Notifier:
    """
    This class is used to show information to the user using dialog boxes or
    little pop ups (like tooltips).
    Also all notifications get logged using the Application Logger
    """

    # TODO: change the implementation to send/post custom events to avoid
    # problems with threads like we had before
    def __init__(self):
        self.widget = None

    def _postCustomEvent(self, text, level, customEventClass):
        logging.getLogger(__name__).log(text, "INFO")
        if self.widget is not None:
            event = customEventClass(text, level)
            faraday.client.model.guiapi.postEvent(event, self.widget)

    def showDialog(self, text, level="Information"):
        self._postCustomEvent(text, level, ShowDialogCustomEvent)

    def showPopup(self, text, level="Information"):
        self._postCustomEvent(text, level, ShowPopupCustomEvent)


# I'm Py3
