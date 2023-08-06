#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Faraday Penetration Test IDE
Copyright (C) 2013  Infobyte LLC (http://www.infobytesec.com/)
See the file 'doc/LICENSE' for the license information

"""
from past.builtins import basestring
from builtins import range

import os
import time
import shlex
import logging
from threading import Thread
from multiprocessing import JoinableQueue, Process

from faraday.config.configuration import getInstanceConfiguration
from faraday.client.plugins.plugin import PluginProcess
import faraday.client.model.api
from faraday.client.model.commands_history import CommandRunInformation
from faraday.client.model import Modelactions

from faraday.config.constant import (
    CONST_FARADAY_ZSH_OUTPUT_PATH,
)

from faraday.client.start_client import (
    CONST_FARADAY_HOME_PATH,
)
CONF = getInstanceConfiguration()

logger = logging.getLogger(__name__)


class PluginCommiter(Thread):

    def __init__(self, output_queue, output, pending_actions, plugin, command, mapper_manager, end_event=None):
        super(PluginCommiter, self).__init__(name="PluginCommiterThread")
        self.output_queue = output_queue
        self.pending_actions = pending_actions
        self.stop = False
        self.plugin = plugin
        self.command = command
        self.mapper_manager = mapper_manager
        self.output = output
        self._report_path = os.path.join(CONF.getReportPath(), command.workspace)
        self._report_ppath = os.path.join(self._report_path, "process")
        self._report_upath = os.path.join(self._report_path, "unprocessed")
        self.end_event = end_event

    def stop(self):
        self.stop = True

    def commit(self):
        logger.info('Plugin end. Commiting to faraday server.')
        self.pending_actions.put(
            (Modelactions.PLUGINEND, self.plugin.id, self.command.getID()))
        self.command.duration = time.time() - self.command.itime
        self.mapper_manager.update(self.command)
        if self.end_event:
            self.end_event.set()

    def run(self):
        name = ''
        try:
            self.output_queue.join()
            self.commit()
            if b'\0' not in self.output and os.path.isfile(self.output):
                # sometimes output is a filepath
                name = os.path.basename(self.output)
                os.rename(self.output,
                    os.path.join(self._report_ppath, name))
        except Exception as ex:
            logger.exception(ex)
            logger.warning('Something failed, moving file to unprocessed')
            os.rename(self.output, os.path.join(self._report_upath, name))



class PluginController(Thread):
    """
    TODO: Doc string.
    """
    def __init__(self, id, plugin_manager, mapper_manager, pending_actions, end_event=None):
        super(PluginController, self).__init__(name="PluginControllerThread")
        self.plugin_manager = plugin_manager
        self._plugins = plugin_manager.getPlugins()
        self.id = id
        self._actionDispatcher = None
        self._setupActionDispatcher()
        self._mapper_manager = mapper_manager
        self.output_path = os.path.join(
            os.path.expanduser(CONST_FARADAY_HOME_PATH),
            CONST_FARADAY_ZSH_OUTPUT_PATH)
        self._active_plugins = {}
        self.plugin_sets = {}
        self.plugin_manager.addController(self, self.id)
        self.stop = False
        self.pending_actions = pending_actions
        self.end_event = end_event

    def _find_plugin(self, plugin_id):
        return self._plugins.get(plugin_id, None)

    def _is_command_malformed(self, original_command, modified_command):
        """
        Checks if the command to be executed is safe and it's not in the
        block list defined by the user. Returns False if the modified
        command is ok, True if otherwise.
        """
        block_chars = {"|", "$", "#"}

        if original_command == modified_command:
            return False

        orig_cmd_args = shlex.split(original_command)

        if not isinstance(modified_command, basestring):
            modified_command = ""
        mod_cmd_args = shlex.split(modified_command)

        block_flag = False
        orig_args_len = len(orig_cmd_args)
        for index in range(0, len(mod_cmd_args)):
            if (index < orig_args_len and
                    orig_cmd_args[index] == mod_cmd_args[index]):
                continue

            for char in block_chars:
                if char in mod_cmd_args[index]:
                    block_flag = True
                    break

        return block_flag

    def _get_plugins_by_input(self, cmd, plugin_set):
        for plugin in plugin_set.values():
            if isinstance(cmd, bytes):
                cmd = cmd.decode()
            if plugin.canParseCommandString(cmd):
                return plugin
        return None

    def getAvailablePlugins(self):
        """
        Return a dictionary with the available plugins.
        Plugin ID's as keys and plugin instences as values
        """
        return self._plugins

    def stop(self):
        self.plugin_process.stop()
        self.stop = True

    def processOutput(self, plugin, output, command, isReport=False):
        """
            Process the output of the plugin. This will start the PluginProcess
            and also PluginCommiter (thread) that will informa to faraday server
            when the command finished.

        :param plugin: Plugin to execute
        :param output: read output from plugin or term
        :param command_id: command id that started the plugin
        :param isReport: Report or output from shell
        :return: None
        """
        output_queue = JoinableQueue()
        plugin.set_actions_queue(self.pending_actions)
        self.plugin_process = PluginProcess(plugin, output_queue, isReport)
        logger.info("Created plugin_process (%d) for plugin instance (%d)", id(self.plugin_process), id(plugin))
        self.pending_actions.put((Modelactions.PLUGINSTART, plugin.id, command.getID()))
        output_queue.put((output, command.getID()))
        plugin_commiter = PluginCommiter(
            output_queue,
            output,
            self.pending_actions,
            plugin,
            command,
            self._mapper_manager,
            self.end_event,
        )
        plugin_commiter.start()
        # This process is stopped when plugin commiter joins output queue
        self.plugin_process.start()

    def _processAction(self, action, parameters):
        """
        decodes and performs the action given
        It works kind of a dispatcher
        """
        logger.debug("_processAction - %s - parameters = %s", action, parameters)
        self._actionDispatcher[action](*parameters)

    def _setupActionDispatcher(self):
        self._actionDispatcher = {
            Modelactions.ADDHOST: faraday.client.model.api.addHost,
            Modelactions.ADDSERVICEHOST: faraday.client.model.api.addServiceToHost,
            #Vulnerability
            Modelactions.ADDVULNHOST: faraday.client.model.api.addVulnToHost,
            Modelactions.ADDVULNSRV: faraday.client.model.api.addVulnToService,
            #VulnWeb
            Modelactions.ADDVULNWEBSRV: faraday.client.model.api.addVulnWebToService,
            #Note
            Modelactions.ADDNOTEHOST: faraday.client.model.api.addNoteToHost,
            Modelactions.ADDNOTESRV: faraday.client.model.api.addNoteToService,
            Modelactions.ADDNOTENOTE: faraday.client.model.api.addNoteToNote,
            #Creds
            Modelactions.ADDCREDSRV:  faraday.client.model.api.addCredToService,
            #LOG
            Modelactions.LOG: faraday.client.model.api.log,
            Modelactions.DEVLOG: faraday.client.model.api.devlog,
            # Plugin state
            Modelactions.PLUGINSTART: faraday.client.model.api.pluginStart,
            Modelactions.PLUGINEND: faraday.client.model.api.pluginEnd
        }

    def updatePluginSettings(self, plugin_id, new_settings):
        for plugin_set in self.plugin_sets.values():
            if plugin_id in plugin_set:
                plugin_set[plugin_id].updateSettings(new_settings)
        if plugin_id in self._plugins:
            self._plugins[plugin_id].updateSettings(new_settings)

    def createPluginSet(self, pid):
        self.plugin_sets[pid] = self.plugin_manager.getPlugins()

    def processCommandInput(self, pid, cmd, pwd):
        """
        This method tries to find a plugin to parse the command sent
        by the terminal (identiefied by the process id).
        """
        if pid not in self.plugin_sets:
            self.createPluginSet(pid)

        plugin = self._get_plugins_by_input(cmd, self.plugin_sets[pid])

        if plugin:
            modified_cmd_string = plugin.processCommandString("", pwd, cmd)
            if not self._is_command_malformed(cmd, modified_cmd_string):

                cmd_info = CommandRunInformation(
                    **{'workspace': faraday.client.model.api.getActiveWorkspace().name,
                        'itime': time.time(),
                        'import_source': 'shell',
                        'command': cmd.split()[0],
                        'params': ' '.join(cmd.split()[1:])})
                cmd_info.setID(self._mapper_manager.save(cmd_info))

                self._active_plugins[pid] = plugin, cmd_info

                return plugin.id, modified_cmd_string

        return None, None

    def onCommandFinished(self, pid, exit_code, term_output):
        if pid not in list(self._active_plugins.keys()):
            return False
        if exit_code != 0:
            del self._active_plugins[pid]
            return False

        plugin, cmd_info = self._active_plugins.get(pid)

        cmd_info.duration = time.time() - cmd_info.itime
        self._mapper_manager.update(cmd_info)

        self.processOutput(plugin, term_output, cmd_info)
        del self._active_plugins[pid]
        return True

    def processReport(self, plugin_id, filepath, ws_name=None):
        if plugin_id not in self._plugins:
            logger.warning("Unknown Plugin ID: %s", plugin_id)
            return False
        if not ws_name:
            ws_name = faraday.client.model.api.getActiveWorkspace().name

        cmd_info = CommandRunInformation(
            **{'workspace': ws_name,
               'itime': time.time(),
               'import_source': 'report',
               'command': plugin_id,
               'params': filepath,
            })

        self._mapper_manager.createMappers(ws_name)
        command_id = self._mapper_manager.save(cmd_info)
        cmd_info.setID(command_id)

        if plugin_id in self._plugins:
            logger.info('Processing report with plugin {0}'.format(plugin_id))
            self._plugins[plugin_id].workspace = ws_name
            with open(filepath, 'rb') as output:
                self.processOutput(self._plugins[plugin_id], output.read(), cmd_info, True)
            return command_id

        # Plugin to process this report not found, update duration of plugin process
        cmd_info.duration = time.time() - cmd_info.itime
        self._mapper_manager.update(cmd_info)
        return False

    def clearActivePlugins(self):
        self._active_plugins = {}


# I'm Py3
