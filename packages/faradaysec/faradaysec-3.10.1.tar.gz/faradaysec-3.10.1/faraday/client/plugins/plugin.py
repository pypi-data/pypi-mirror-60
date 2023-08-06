"""
Faraday Penetration Test IDE
Copyright (C) 2013  Infobyte LLC (http://www.infobytesec.com/)
See the file 'doc/LICENSE' for the license information

"""
import os
import re
import time
import logging
import traceback
import deprecation
from threading import Thread

import faraday.server.config
import faraday.client.model.api
import faraday.client.model.common
from faraday import __license_version__ as license_version
from faraday.client.model.common import factory
from faraday.client.persistence.server.models import get_host, update_host
from faraday.client.persistence.server.models import (
    Host,
    Service,
    Vuln,
    VulnWeb,
    Credential,
    Note
)
from faraday.client.model import Modelactions

from faraday.config.configuration import getInstanceConfiguration
CONF = getInstanceConfiguration()
VERSION = license_version.split('-')[0].split('rc')[0]
logger = logging.getLogger(__name__)


class PluginBase:
    # TODO: Add class generic identifier
    class_signature = "PluginBase"

    def __init__(self):
        self.data_path = CONF.getDataPath()
        self.persistence_path = CONF.getPersistencePath()
        self.workspace = CONF.getLastWorkspace()
        # Must be unique. Check that there is not
        # an existant plugin with the same id.
        # TODO: Make script that list current ids.
        self.id = None
        self._rid = id(self)
        self.version = None
        self.name = None
        self.description = ""
        self._command_regex = None
        self._output_file_path = None
        self.framework_version = None
        self._completition = {}
        self._new_elems = []
        self._settings = {}
        self.command_id = None
        self.logger = logger.getChild(self.__class__.__name__)

    def report_belongs_to(self, **kwargs):
        return False

    def has_custom_output(self):
        return bool(self._output_file_path)

    def get_custom_file_path(self):
        return self._output_file_path

    def set_actions_queue(self, _pending_actions):
        """
            We use plugin controller queue to add actions created by plugins.
            Plugin controller will consume this actions.

        :param controller: plugin controller
        :return: None
        """
        self._pending_actions = _pending_actions

    def setCommandID(self, command_id):
        self.command_id = command_id

    def getSettings(self):
        for param, (param_type, value) in self._settings.items():
            yield param, value

    def get_ws(self):
        return CONF.getLastWorkspace()

    def getSetting(self, name):
        setting_type, value = self._settings[name]
        return value

    def addSetting(self, param, param_type, value):
        self._settings[param] = param_type, value

    def updateSettings(self, new_settings):
        for name, value in new_settings.items():
            if name in self._settings:
                setting_type, curr_value = self._settings[name]
                self._settings[name] = setting_type, setting_type(value)

    def canParseCommandString(self, current_input):
        """
        This method can be overriden in the plugin implementation
        if a different kind of check is needed
        """
        return (self._command_regex is not None and
                self._command_regex.match(current_input.strip()) is not None)

    def getCompletitionSuggestionsList(self, current_input):
        """
        This method can be overriden in the plugin implementation
        if a different kind of check is needed
        """
        words = current_input.split(" ")
        cword = words[len(words) - 1]
        options = {}
        for k, v in self._completition.items():
            if re.search(str("^" + cword), k, flags=re.IGNORECASE):
                options[k] = v
        return options

    def processOutput(self, term_output):
        output = term_output
        if self.has_custom_output() and os.path.isfile(self.get_custom_file_path()):
            self._parse_filename(self.get_custom_file_path())
        else:
            self.parseOutputString(output)

    def _parse_filename(self, filename):
        with open(filename, 'rb') as output:
            self.parseOutputString(output.read())

    def processReport(self, filepath):
        if os.path.isfile(filepath):
            self._parse_filename(filepath)

    def parseOutputString(self, output):
        """
        This method must be implemented.
        This method will be called when the command finished executing and
        the complete output will be received to work with it
        Using the output the plugin can create and add hosts, interfaces,
        services, etc.
        """
        raise NotImplementedError('This method must be implemented.')

    def processCommandString(self, username, current_path, command_string):
        """
        With this method a plugin can add aditional arguments to the
        command that it's going to be executed.
        """
        return None

    def __addPendingAction(self, *args):
        """
        Adds a new pending action to the queue
        Action is build with generic args tuple.
        The caller of this function has to build the action in the right
        way since no checks are preformed over args
        """
        if self.command_id:
            args = args + (self.command_id, )
        else:
            logger.warning('Warning command id not set for action {%s}', args)
        logger.debug('AddPendingAction %s', args)
        self._pending_actions.put(args)

    def createAndAddHost(self, name, os="unknown", hostnames=None, mac=None):
        host_obj = factory.createModelObject(
            Host.class_signature,
            name,
            os=os,
            parent_id=None,
            workspace_name=self.workspace,
            hostnames=hostnames,
            mac=mac)
        host_obj._metadata.creatoserverr = self.id
        self.__addPendingAction(Modelactions.ADDHOST, host_obj)
        return host_obj.getID()

    @deprecation.deprecated(deprecated_in="3.0", removed_in="3.5",
                            current_version=VERSION,
                            details="Interface object removed. Use host or service instead")
    def createAndAddInterface(
        self, host_id, name="", mac="00:00:00:00:00:00",
        ipv4_address="0.0.0.0", ipv4_mask="0.0.0.0", ipv4_gateway="0.0.0.0",
        ipv4_dns=None, ipv6_address="0000:0000:0000:0000:0000:0000:0000:0000",
        ipv6_prefix="00",
        ipv6_gateway="0000:0000:0000:0000:0000:0000:0000:0000", ipv6_dns=None,
        network_segment="", hostname_resolution=None):
        if ipv4_dns is None:
            ipv4_dns = []
        if ipv6_dns is None:
            ipv6_dns = []
        if hostname_resolution is None:
            hostname_resolution = []
        if not isinstance(hostname_resolution, list):
            logger.warning("hostname_resolution parameter must be a list and is (%s)", type(hostname_resolution))
            hostname_resolution = [hostname_resolution]
        # We don't use interface anymore, so return a host id to maintain
        # backwards compatibility
        # Little hack because we dont want change all the plugins for add hostnames in Host object.
        # SHRUG
        try:
            host = get_host(self.workspace, host_id=host_id)
            host.hostnames += hostname_resolution
            host.mac = mac
            update_host(self.workspace, host, command_id=self.command_id)
        except:
            logger.info("Error updating Host with right hostname resolution...")
        return host_id

    @deprecation.deprecated(deprecated_in="3.0", removed_in="3.5",
                            current_version=VERSION,
                            details="Interface object removed. Use host or service instead. Service will be attached to Host!")
    def createAndAddServiceToInterface(self, host_id, interface_id, name,
                                       protocol="tcp?", ports=None,
                                       status="open", version="unknown",
                                       description=""):
        if not ports:
            ports = []
        if status not in ("open", "closed", "filtered"):
            self.log(
                'Unknown service status %s. Using "open" instead' % status,
                'WARNING'
            )
            status = 'open'

        serv_obj = faraday.client.model.common.factory.createModelObject(
            Service.class_signature,
            name, protocol=protocol, ports=ports, status=status,
            version=version, description=description,
            parent_type='Host', parent_id=host_id,
            workspace_name=self.workspace)

        serv_obj._metadata.creator = self.id
        self.__addPendingAction(Modelactions.ADDSERVICEHOST, serv_obj)
        return serv_obj.getID()

    def createAndAddServiceToHost(self, host_id, name,
                                       protocol="tcp?", ports=None,
                                       status="open", version="unknown",
                                       description=""):
        if not ports:
            ports = []
        if status not in ("open", "closed", "filtered"):
            self.log(
                'Unknown service status %s. Using "open" instead' % status,
                'WARNING'
            )
            status = 'open'

        serv_obj = faraday.client.model.common.factory.createModelObject(
            Service.class_signature,
            name, protocol=protocol, ports=ports, status=status,
            version=version, description=description,
            parent_type='Host', parent_id=host_id,
            workspace_name=self.workspace)

        serv_obj._metadata.creator = self.id
        self.__addPendingAction(Modelactions.ADDSERVICEHOST, serv_obj)
        return serv_obj.getID()

    def createAndAddVulnToHost(self, host_id, name, desc="", ref=None,
                               severity="", resolution="", data="", external_id=None):
        if not ref:
            ref = []
        vuln_obj = faraday.client.model.common.factory.createModelObject(
            Vuln.class_signature,
            name, data=data, desc=desc, refs=ref, severity=severity,
            resolution=resolution, confirmed=False,
            parent_id=host_id, parent_type='Host',
            workspace_name=self.workspace,external_id=external_id)

        vuln_obj._metadata.creator = self.id
        self.__addPendingAction(Modelactions.ADDVULNHOST, vuln_obj)
        return vuln_obj.getID()

    @deprecation.deprecated(deprecated_in="3.0", removed_in="3.5",
                            current_version=VERSION,
                            details="Interface object removed. Use host or service instead. Vuln will be added to Host")
    def createAndAddVulnToInterface(self, host_id, interface_id, name,
                                    desc="", ref=None, severity="",
                                    resolution="", data=""):
        if not ref:
            ref = []
        vuln_obj = faraday.client.model.common.factory.createModelObject(
            Vuln.class_signature,
            name, data=data, desc=desc, refs=ref, severity=severity,
            resolution=resolution, confirmed=False,
            parent_type='Host', parent_id=host_id,
            workspace_name=self.workspace)

        vuln_obj._metadata.creator = self.id
        self.__addPendingAction(Modelactions.ADDVULNHOST, vuln_obj)
        return vuln_obj.getID()

    def createAndAddVulnToService(self, host_id, service_id, name, desc="",
                                  ref=None, severity="", resolution="", data="", external_id=None):
        if not ref:
            ref = []
        vuln_obj = faraday.client.model.common.factory.createModelObject(
            Vuln.class_signature,
            name, data=data, desc=desc, refs=ref, severity=severity,
            resolution=resolution, confirmed=False,
            parent_type='Service', parent_id=service_id,
            workspace_name=self.workspace, external_id=external_id)

        vuln_obj._metadata.creator = self.id

        self.__addPendingAction(Modelactions.ADDVULNSRV, vuln_obj)
        return vuln_obj.getID()

    def createAndAddVulnWebToService(self, host_id, service_id, name, desc="",
                                     ref=None, severity="", resolution="",
                                     website="", path="", request="",
                                     response="", method="", pname="",
                                     params="", query="", category="", data="", external_id=None):
        if not ref:
            ref = []
        vulnweb_obj = faraday.client.model.common.factory.createModelObject(
            VulnWeb.class_signature,
            name, data=data, desc=desc, refs=ref, severity=severity,
            resolution=resolution, website=website, path=path,
            request=request, response=response, method=method,
            pname=pname, params=params, query=query,
            category=category, confirmed=False, parent_id=service_id,
            parent_type='Service',
            workspace_name=self.workspace, external_id=external_id)

        vulnweb_obj._metadata.creator = self.id
        self.__addPendingAction(Modelactions.ADDVULNWEBSRV, vulnweb_obj)
        return vulnweb_obj.getID()

    def createAndAddNoteToHost(self, host_id, name, text):
        return None

    def createAndAddNoteToInterface(self, host_id, interface_id, name, text):
        return None

    def createAndAddNoteToService(self, host_id, service_id, name, text):
        return None

    def createAndAddNoteToNote(self, host_id, service_id, note_id, name, text):
        return None

    def createAndAddCredToService(self, host_id, service_id, username,
                                  password):

        cred_obj = faraday.client.model.common.factory.createModelObject(
            Credential.class_signature,
            username, password=password, parent_id=service_id, parent_type='Service',
            workspace_name=self.workspace)

        cred_obj._metadata.creator = self.id
        self.__addPendingAction(Modelactions.ADDCREDSRV, cred_obj)
        return cred_obj.getID()

    def log(self, msg, level='INFO'):
        self.__addPendingAction(Modelactions.LOG, msg, level)

    def devlog(self, msg):
        self.__addPendingAction(Modelactions.DEVLOG, msg)


class PluginTerminalOutput(PluginBase):
    def __init__(self):
        super().__init__()

    def processOutput(self, term_output):
        try:
            self.parseOutputString(term_output)
        except Exception as e:
            self.logger.exception(e)


class PluginCustomOutput(PluginBase):
    def __init__(self):
        super().__init__()

    def processOutput(self, term_output):
        # we discard the term_output since it's not necessary
        # for this type of plugins
        self.processReport(self._output_file_path)


class PluginByExtension(PluginBase):
    def __init__(self):
        super().__init__()
        self.extension = []

    def report_belongs_to(self, extension="", **kwargs):
        match = False
        if type(self.extension) == str:
            match = (self.extension == extension)
        elif type(self.extension) == list:
            match = (extension in self.extension)
        self.logger.debug("Extension Match: [%s =/in %s] -> %s", extension, self.extension, match)
        return match


class PluginXMLFormat(PluginByExtension):

    def __init__(self):
        super().__init__()
        self.identifier_tag = []
        self.extension = ".xml"

    def report_belongs_to(self, main_tag="", **kwargs):
        match = False
        if super().report_belongs_to(**kwargs):
            if type(self.identifier_tag) == str:
                match = (main_tag == self.identifier_tag)
            elif type(self.identifier_tag) == list:
                match = (main_tag in self.identifier_tag)
        self.logger.debug("Tag Match: [%s =/in %s] -> %s", main_tag, self.identifier_tag, match)
        return match


class PluginJsonFormat(PluginByExtension):

    def __init__(self):
        super().__init__()
        self.json_keys = set()
        self.extension = ".json"

    def report_belongs_to(self, **kwargs):
        match = False
        if super().report_belongs_to(**kwargs):
            pass
        return match


class PluginProcess(Thread):
    def __init__(self, plugin_instance, output_queue, isReport=False):
        """
            Executes one plugin.

        :param plugin_instance: current plugin in execution.
        :param output_queue: queue with raw ouput of that the plugin needs.
        :param isReport: output data was read from file.
        """
        super(PluginProcess, self).__init__(name="PluginProcessThread")
        self.output_queue = output_queue
        self.plugin = plugin_instance
        self.isReport = isReport
        self.setDaemon(True)
        self._must_stop = False

    def run(self):
        proc_name = self.name
        faraday.client.model.api.devlog("-" * 40)
        faraday.client.model.api.devlog(f"proc_name = {proc_name}")
        faraday.client.model.api.devlog(f"Starting run method on PluginProcess")
        faraday.client.model.api.devlog(f"parent process: {os.getppid()}")
        faraday.client.model.api.devlog(f"process id: {os.getpid()}")
        faraday.client.model.api.devlog("-" * 40)
        done = False
        while not done and not self._must_stop:
            output, command_id = self.output_queue.get()
            self.plugin.setCommandID(command_id)
            if output is not None:
                faraday.client.model.api.devlog(f"{proc_name}: New Output")
                try:
                    if isinstance(output, bytes):
                        output = output.decode()
                    self.plugin.processOutput(output)
                except Exception as ex:
                    faraday.client.model.api.devlog("Plugin raised an exception:")
                    faraday.client.model.api.devlog(traceback.format_exc())
            else:
                done = True
                faraday.client.model.api.devlog(f"{proc_name}: Exiting")
            self.output_queue.task_done()
            time.sleep(0.1)

    def stop(self):
        self._must_stop = True

# I'm Py3
