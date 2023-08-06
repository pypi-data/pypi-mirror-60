#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Faraday Penetration Test IDE
Copyright (C) 2013  Infobyte LLC (http://www.infobytesec.com/)
See the file 'doc/LICENSE' for the license information

"""
from __future__ import absolute_import

import os
import re
import sys
import traceback
import logging

from importlib.machinery import SourceFileLoader

from faraday.config.configuration import getInstanceConfiguration

CONF = getInstanceConfiguration()

logger = logging.getLogger(__name__)

class PluginManager:

    def __init__(self, plugin_repo_path, pending_actions=None):
        self._controllers = {}
        self._plugin_modules = {}
        self._plugin_instances = {}
        self._loadPlugins(plugin_repo_path)
        self._plugin_settings = {}
        self.pending_actions = pending_actions
        self._loadSettings()

    def addController(self, controller, id):
        self._controllers[id] = controller

    def _loadSettings(self):
        _plugin_settings = CONF.getPluginSettings()
        if _plugin_settings:
            self._plugin_settings = _plugin_settings

        activep = self._instancePlugins()
        for plugin_id, plugin in activep.items():
            if plugin_id in _plugin_settings:
                plugin.updateSettings(_plugin_settings[plugin_id]["settings"])
            self._plugin_settings[plugin_id] = {
                "name": plugin.name,
                "description": plugin.description,
                "version": plugin.version,
                "plugin_version": plugin.plugin_version,
                "settings": dict(plugin.getSettings())
                }

        dplugins = []
        for k, v in self._plugin_settings.items():
            if k not in activep:
                dplugins.append(k)

        for d in dplugins:
            del self._plugin_settings[d]

        CONF.setPluginSettings(self._plugin_settings)
        CONF.saveConfig()

    def getSettings(self):
        return self._plugin_settings

    def updateSettings(self, settings):
        self._plugin_settings = settings
        CONF.setPluginSettings(settings)
        CONF.saveConfig()
        for plugin_id, params in settings.items():
            new_settings = params["settings"]
            for c_id, c_instance in self._controllers.items():
                c_instance.updatePluginSettings(plugin_id, new_settings)

    def _instancePlugins(self):
        if not self._plugin_instances:
            for module in self._plugin_modules.values():
                new_plugin = module.createPlugin()
                new_plugin.set_actions_queue(self.pending_actions)
                self._verifyPlugin(new_plugin)
                if new_plugin.id.lower() not in self._plugin_instances:
                    self._plugin_instances[new_plugin.id.lower()] = new_plugin
                else:
                    logger.warning("Duplicated Plugin ID (%s)", new_plugin.id.lower())
        return self._plugin_instances

    def _loadPlugins(self, plugin_repo_path):
        """
        Finds and load all the plugins that are
        available in the plugin_repo_path.
        """
        try:
            os.stat(plugin_repo_path)
        except OSError:
            pass
        sys.path.append(plugin_repo_path)
        dir_name_regexp = re.compile(r"^[\d\w\-\_]+$")
        if not os.path.exists(plugin_repo_path):
            logger.error('Plugins path could not be opened, no pluging will be available!')
            return
        for name in os.listdir(plugin_repo_path):
            if dir_name_regexp.match(name) and name != "__pycache__":
                try:
                    module_path = os.path.join(plugin_repo_path, name)
                    sys.path.append(module_path)
                    module_filename = os.path.join(module_path, "plugin.py")
                    file_ext = os.path.splitext(module_filename)[1]
                    if file_ext.lower() == '.py':
                        loader = SourceFileLoader(name,  module_filename)
                        self._plugin_modules[name] = loader.load_module()
                    logger.debug('Loading plugin {0}'.format(name))
                except Exception as e:
                    logger.debug("An error ocurred while loading plugin %s.\n%s", module_filename, traceback.format_exc())
                    logger.warning(e)

    def getPlugins(self):
        plugins = self._instancePlugins()
        for _id, plugin in plugins.items():
            if _id in self._plugin_settings:
                plugin.updateSettings(self._plugin_settings[_id]["settings"])
        return plugins

    def _verifyPlugin(self, new_plugin):
        """
        Generic method that decides is a plugin is valid
        based on a predefined set of checks.
        """
        try:
            assert(new_plugin.id is not None)
            assert(new_plugin.version is not None)
            assert(new_plugin.name is not None)
            assert(new_plugin.framework_version is not None)
        except (AssertionError, KeyError):
            return False
        return True


# I'm Py3
