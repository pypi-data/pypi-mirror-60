"""
Faraday Penetration Test IDE
Copyright (C) 2013  Infobyte LLC (http://www.infobytesec.com/)
See the file 'doc/LICENSE' for the license information
"""
import argparse
import base64
import hashlib
import os
import pickle
import re
import shlex
import socket
import sqlite3
import sys
from urllib.parse import urlparse
from io import StringIO
from http.server import BaseHTTPRequestHandler

from collections import defaultdict

from faraday.client.plugins.plugin import PluginTerminalOutput
from faraday.client.plugins.plugin_utils import get_vulnweb_url_fields

try:
    import xml.etree.cElementTree as ET
    import xml.etree.ElementTree as ET_ORIG
    ETREE_VERSION = ET_ORIG.VERSION
except ImportError:
    import xml.etree.ElementTree as ET
    ETREE_VERSION = ET.VERSION

ETREE_VERSION = [int(i) for i in ETREE_VERSION.split(".")]

current_path = os.path.abspath(os.getcwd())

__author__ = "Francisco Amato"
__copyright__ = "Copyright (c) 2013, Infobyte LLC"
__credits__ = ["Francisco Amato"]
__license__ = ""
__version__ = "1.0.0"
__maintainer__ = "Francisco Amato"
__email__ = "famato@infobytesec.com"
__status__ = "Development"


# This is the value of the HASHDB_MILESTONE_VALUE constant
# in the lib/core/settings.py file of sqlmap.
# If that value is changed in a newer version of SQLMap, it means that the
# hashdb mechanism has backwards-incompatible changes that probably will
# break our plugin, so the plugin will show an error and abort
SUPPORTED_HASHDB_VERSIONS = {
    "dPHoJRQYvs",  # 1.0.11
    "BZzRotigLX",  # 1.2.8
    "OdqjeUpBLc",  # 1.3.6..1.3.10
}


class Database:

    def __init__(self, database):
        self.database = database

    def connect(self, who="server"):

        self.connection = sqlite3.connect(
            self.database, timeout=3, isolation_level=None)

        self.cursor = self.connection.cursor()

    def disconnect(self):
        self.cursor.close()
        self.connection.close()

    def commit(self):
        self.cursor.commit()

    def execute(self, statement, arguments=None):
        if arguments:
            self.cursor.execute(statement, arguments)
        else:
            self.cursor.execute(statement)

        if statement.lstrip().upper().startswith("SELECT"):
            return self.cursor.fetchall()


class SqlmapPlugin(PluginTerminalOutput):
    # Plugin for Sqlmap Tool
    def __init__(self):

        PluginTerminalOutput.__init__(self)
        self.id = "Sqlmap"
        self.name = "Sqlmap"
        self.plugin_version = "0.0.3"
        self.version = "1.2.8"
        self.framework_version = "1.0.0"
        self._current_output = None
        self.url = ""
        self.protocol = ""
        self.hostname = ""
        self.port = "80"
        self.params = ""
        self.fullpath = ""
        self.path = ""
        self.ignore_parsing = False

        self.addSetting("Sqlmap path", str, "/root/tools/sqlmap")

        self.db_port = {
            "MySQL": 3306, "PostgreSQL": "", "Microsoft SQL Server": 1433,
            "Oracle": 1521, "Firebird": 3050,
            "SAP MaxDB": 7210, "Sybase": 5000,
            "IBM DB2": 50000, "HSQLDB": 9001}

        self.ptype = {
            1: "Unescaped numeric",
            2: "Single quoted string",
            3: "LIKE single quoted string",
            4: "Double quoted string",
            5: "LIKE double quoted string",
        }

        self._command_regex = re.compile(
            r'^(python2 ./sqlmap.py|python2.7 ./sqlmap.py|sudo sqlmap|sqlmap|sudo python sqlmap|python sqlmap|\.\/sqlmap).*?')

        global current_path
        self._output_path = ''

    class HTTPRequest(BaseHTTPRequestHandler):

        def __init__(self, request_text):
            super().__init__()
            self.rfile = StringIO(request_text)
            self.raw_requestline = self.rfile.readline()
            self.error_code = self.error_message = None
            self.parse_request()

        def send_error(self, code, message):
            self.error_code = code
            self.error_message = message

    def hashKey(self, key):
        # from sqlmap/lib/utils/hashdb.py
        import six #pylint: disable=import-error,bad-option-value,import-outside-toplevel
        from lib.core.convert import getBytes #pylint: disable=import-error,bad-option-value,import-outside-toplevel
        key = getBytes(key if isinstance(key, six.text_type) else repr(key))
        retVal = int(hashlib.md5(key).hexdigest(), 16) & 0x7fffffffffffffff  # Reference: http://stackoverflow.com/a/4448400
        return retVal

    def hashDBRetrieve(self, key, unserialize=False, db=False):
        """
        Helper function for restoring session data from HashDB
        """

        if self.HASHDB_MILESTONE_VALUE == 'dPHoJRQYvs':
            # Support for old SQLMap versions
            key = "%s%s%s" % (self.url or "%s%s" % (
                self.hostname, self.port), key, self.HASHDB_MILESTONE_VALUE)
        else:
            if not self.url:
                self.log('No URL found while running sqlmap', 'ERROR')
            url = urlparse(self.url)
            key = '|'.join([
                url.hostname,
                url.path.strip('/'),
                key,
                self.HASHDB_MILESTONE_VALUE
            ])

        retVal = ''
        hash_ = self.hashKey(key)

        if not retVal:
            while True:
                try:
                    for row in db.execute("SELECT value FROM storage WHERE id=?", (hash_,)):
                        retVal = row[0]
                except sqlite3.OperationalError as ex:
                    if not 'locked' in ex.message:
                        raise
                else:
                    break
        return retVal if not unserialize else self.base64unpickle(retVal)

    def base64decode(self, value):
        """
        Decodes string value from Base64 to plain format

        >>> base64decode('Zm9vYmFy')
        'foobar'
        """

        return base64.b64decode(value)

    def base64encode(self, value):
        """
        Encodes string value from plain to Base64 format

        >>> base64encode('foobar')
        'Zm9vYmFy'
        """
        return base64.b64encode(value)[:-1].replace("\n", "")

    def base64unpickle(self, value):
        """
        Decodes value from Base64 to plain format and deserializes (with pickle) its content

        >>> base64unpickle('gAJVBmZvb2JhcnEALg==')
        'foobar'
        """
        if value:
            return pickle.loads(self.base64decode(value))

    def xmlvalue(self, db, name, value="query"):

        filepath = "%s" % os.path.join(
            current_path, "plugins/repo/sqlmap/queries.xml")
        with open(filepath, "r") as f:
            try:
                tree = ET.fromstring(f.read())
            except SyntaxError as err:
                self.log("SyntaxError: %s. %s" % (err, filepath), "ERROR")
                return None

        for node in tree.findall("dbms[@value='" + db + "']/" + name + ''):
            return node.attrib[value]

    def getuser(self, data):

        users = re.search(
            r'database management system users \[[\d]+\]:\n((\[\*\] (.*)\n)*)',
            data)

        if users:
            return [x.replace("[*] ", "") for x in users.group(1).split("\n")]

    def getdbs(self, data):

        dbs = re.search(
            r'available databases \[[\d]+\]:\n(((\[\*\] (.*)\n)*))',
            data)

        if dbs:
            return [x.replace("[*] ", "") for x in dbs.group(1).split("\n")]

    def getpassword(self, data):

        users = {}

        password = re.findall(
            r"\n\[\*\] (.*) \[\d\]:\n\s*password hash: (.*)",
            data)

        if password:
            for credential in password:

                user = credential[0]
                mpass = credential[1]
                users[user] = mpass

        return users

    def _get_log_message(self, line):
        """Return the message of a log line.

        If the line isn't from the log it will raise a ValueError

        >>> line = '[16:59:03] [INFO] fetching tables'
        >>> self._get_log_message('line')
        'fetching tables'
        """
        match = re.match(r'\[[0-9:]+\] \[\w+\] (.+)$', line)
        if match is None:
            raise ValueError('Incorrect format of line')
        return match.group(1)

    def _is_log_and_startswith(self, text, line):
        try:
            msg = self._get_log_message(line)
        except ValueError:
            return False
        else:
            return msg.startswith(text)

    def _is_tables_log_line(self, line):
        # [16:59:03] [INFO] fetching tables for databases: 'bWAPP, ...
        return self._is_log_and_startswith('fetching tables for databases',
                                           line)

    def _is_columns_log_line(self, line):
        # [16:59:03] [INFO] fetching columns for table ...
        return self._is_log_and_startswith('fetching columns for table ',
                                           line)

    def _match_start_get_remaining(self, start, text):
        """
        If text starts with start, return text with start stripped.

        Return None if it doesn't match.
        """
        if not text.startswith(start):
            return
        return text[len(start):]

    def gettables(self, data):
        """
        Return enumerated tables of the remote database.
        """
        tables = defaultdict(list)  # Map database names with its tables
        current_database = None
        status = 'find_log_line'
        list_found = False
        for line in data.splitlines():
            if status == 'find_log_line':
                # Look for the correct log line to start searching databases
                if self._is_tables_log_line(line):
                    # Correct line, change status
                    status = 'find_dbname'
            elif self._is_log_and_startswith('', line) and list_found:
                # If another log line is reached, stop looking
                break
            elif status == 'find_dbname':
                database = self._match_start_get_remaining('Database: ', line)
                if database is not None:
                    current_database = database
                    list_found = True
                    status = 'find_list_start'
            elif status == 'find_list_start':
                # Find +--------------+ line
                if re.match(r'^\+\-+\+$', line):
                    # Line found
                    status = 'find_tables'
            elif status == 'find_tables':
                if line.startswith('|') and line.endswith('|'):
                    table = line[1:-1].strip()
                    tables[current_database].append(table)
                elif re.match(r'^\+\-+\+$', line):
                    # Table list for this db ended
                    status = 'find_dbname'
            else:
                raise RuntimeError('unknown status')
        return tables

    def getcolumns(self, data):
        """
        Return enumerated columns of the remote database.
        """
        columns = defaultdict(lambda: defaultdict(list))
        current_table = current_database = None
        status = 'find_log_line'
        list_start_count = 0
        list_found = False
        for line in data.splitlines():
            if status == 'find_log_line':
                if self._is_columns_log_line(line):
                    status = 'find_dbname'
            elif self._is_log_and_startswith('', line) and list_found:
                # Don't accept log lines if the DB dump started
                break
            elif status == 'find_dbname':
                database = self._match_start_get_remaining('Database: ', line)
                if database is not None:
                    list_found = True
                    current_database = database
                    status = 'find_table_name'
            elif status == 'find_table_name':
                table = self._match_start_get_remaining('Table: ', line)
                if database is not None:
                    current_table = table
                    status = 'find_two_list_starts'
            elif status == 'find_two_list_starts':
                if re.match(r'^\+[\-\+]+\+$', line):
                    list_start_count += 1
                    if list_start_count == 2:
                        # Start fetching columns
                        list_start_count = 0
                        status = 'find_columns'
            elif status == 'find_columns':
                if line.startswith('|') and line.endswith('|'):
                    (name, type_) = [val.strip()
                                     for val in line[1:-1].split('|')]
                    columns[current_database][current_table].append(
                        (name, type_))
                elif re.match(r'^\+[\-\+]+\+$', line):
                    status = 'find_dbname'
            else:
                raise RuntimeError('unknown status')
        return columns

    def getAddress(self, hostname):
        """
        Returns remote IP address from hostname.
        """
        try:
            return socket.gethostbyname(hostname)
        except socket.error:
            return self.hostname

    def parseOutputString(self, output, debug=False):
        """
        This method will discard the output the shell sends, it will read it from
        the xml where it expects it to be present.

        NOTE: if 'debug' is true then it is being run from a test case and the
        output being sent is valid.
        """

        if self.ignore_parsing:
            return
        sys.path.append(self.getSetting("Sqlmap path"))

        try:
            from lib.core.settings import HASHDB_MILESTONE_VALUE #pylint: disable=import-error,bad-option-value,import-outside-toplevel
            from lib.core.enums import HASHDB_KEYS #pylint: disable=import-error,import-outside-toplevel
            from lib.core.settings import UNICODE_ENCODING #pylint: disable=import-error,import-outside-toplevel
        except:
            self.log('Remember set your Sqlmap Path Setting!... Abort plugin.', 'ERROR')
            return

        if HASHDB_MILESTONE_VALUE not in SUPPORTED_HASHDB_VERSIONS:
            self.log(
                "Your version of SQLMap is not supported with this plugin. "
                "Please use an older version of SQLMap (the suggested one "
                "is \"{}\"). Also, we suggest you to open issue in our GitHub "
                "issue tracker: https://github.com/infobyte/faraday/issues/".format(self.version),
                'ERROR')
            return

        self.HASHDB_MILESTONE_VALUE = HASHDB_MILESTONE_VALUE
        self.HASHDB_KEYS = HASHDB_KEYS
        self.UNICODE_ENCODING = UNICODE_ENCODING

        password = self.getpassword(output)

        webserver = re.search("web application technology: (.*?)\n", output)
        if webserver:
            webserver = webserver.group(1)

        users = self.getuser(output)
        dbs = self.getdbs(output)
        tables = self.gettables(output)
        columns = self.getcolumns(output)

        db = Database(self._output_path)
        db.connect()

        absFilePaths = self.hashDBRetrieve(
            self.HASHDB_KEYS.KB_ABS_FILE_PATHS, True, db)

        brute_tables = self.hashDBRetrieve(
            self.HASHDB_KEYS.KB_BRUTE_TABLES, True, db)

        brute_columns = self.hashDBRetrieve(
            self.HASHDB_KEYS.KB_BRUTE_COLUMNS, True, db)

        xpCmdshellAvailable = self.hashDBRetrieve(
            self.HASHDB_KEYS.KB_XP_CMDSHELL_AVAILABLE, True, db)

        dbms_version = self.hashDBRetrieve(self.HASHDB_KEYS.DBMS, False, db)

        self.ip = self.getAddress(self.hostname)

        h_id = self.createAndAddHost(self.ip)

        i_id = self.createAndAddInterface(
            h_id,
            name=self.ip,
            ipv4_address=self.ip,
            hostname_resolution=[self.hostname])

        s_id = self.createAndAddServiceToInterface(
            h_id,
            i_id,
            self.protocol,
            'tcp',
            [self.port],
            status="open",
            version=webserver)

        db_port = 0
        for item in self.db_port.keys():
            if dbms_version.find(item) >= 0:
                db_port = self.db_port[item]

        s_id2 = self.createAndAddServiceToInterface(
            h_id,
            i_id,
            name=dbms_version,
            protocol="tcp",
            status="closed",
            version=str(dbms_version),
            ports=[str(db_port)],
            description="DB detect by SQLi")

        # sqlmap.py --users
        if users:
            for v in users:
                if v:
                    self.createAndAddCredToService(h_id, s_id2, v, '')

        # sqlmap.py --passwords
        if password:
            for k, v in password.items():
                self.createAndAddCredToService(h_id, s_id2, k, v)

        # sqlmap.py --file-dest
        if absFilePaths:
            self.createAndAddNoteToService(
                h_id,
                s_id2,
                "sqlmap.absFilePaths",
                '\n'.join(absFilePaths))

        # sqlmap.py --common-tables
        if brute_tables:
            for item in brute_tables:
                self.createAndAddNoteToService(
                    h_id,
                    s_id2,
                    "sqlmap.brutetables",
                    item[1])

        # sqlmap.py --tables
        if tables:
            table_names = ['{}.{}'.format(db_name, table)
                           for (db_name, db_tables) in tables.items()
                           for table in db_tables]
            self.createAndAddNoteToService(
                h_id,
                s_id2,
                "sqlmap.tables",
                '\n'.join(table_names)
                )

        # sqlmap.py --columns
        if columns:
            # Create one note per database
            for (database, tables) in columns.items():
                text = ''
                for (table_name, columns) in tables.items():
                    columns_text = ', '.join(
                        '{} {}'.format(col_name, type_)
                        for (col_name, type_) in columns)
                    text += '{}: {}\n'.format(table_name, columns_text)
                self.createAndAddNoteToService(
                    h_id,
                    s_id2,
                    "sqlmap.columns." + database,
                    text)

        # sqlmap.py --common-columns
        if brute_columns:

            text = (
                'Db: ' + brute_columns[0][0] +
                '\nTable: ' + brute_columns[0][1] +
                '\nColumns:')

            for element in brute_columns:
                text += str(element[2]) + '\n'

            self.createAndAddNoteToService(
                h_id,
                s_id2,
                "sqlmap.brutecolumns",
                text)

        # sqlmap.py  --os-shell
        if xpCmdshellAvailable:
            self.createAndAddNoteToService(
                h_id,
                s_id2,
                "sqlmap.xpCmdshellAvailable",
                str(xpCmdshellAvailable))

        # sqlmap.py --dbs
        if dbs:
            self.createAndAddNoteToService(
                h_id,
                s_id2,
                "db.databases",
                '\n'.join(dbs))

        for inj in self.hashDBRetrieve(self.HASHDB_KEYS.KB_INJECTIONS, True, db) or []:

            for k, v in inj.data.items():
                self.createAndAddVulnWebToService(
                    h_id,
                    s_id,
                    name=inj.data[k]['title'],
                    desc="Payload:" + str(inj.data[k]['payload']) + "\nVector:" + str(inj.data[k]['vector']) +
                    "\nParam type:" + str(self.ptype[inj.ptype]),
                    ref=[],
                    pname=inj.parameter,
                    severity="high",
                    method=inj.place,
                    params=self.params,
                    **get_vulnweb_url_fields(self.fullpath))

    def processCommandString(self, username, current_path, command_string):

        parser = argparse.ArgumentParser(conflict_handler='resolve')

        parser.add_argument('-h')
        parser.add_argument('-u')
        parser.add_argument('-s')
        parser.add_argument('-r')

        try:
            args, unknown = parser.parse_known_args(
                shlex.split(re.sub(r'\-h|\-\-help', r'', command_string)))
        except SystemExit:
            pass

        if args.r:
            filename = os.path.expanduser(args.r)
            if not os.path.isabs(filename):
                self.log('Please use an absolute path in -r option of sqlmap', 'ERROR')
                self.ignore_parsing = True
                return
            with open(filename, 'r') as f:
                request = self.HTTPRequest(f.read())
                args.u = "http://" + request.headers['host'] + request.path
                f.close()

        if args.u:

            if args.u.find('http://') < 0 and args.u.find('https://') < 0:
                urlComponents = urlparse('http://' + args.u)
            else:
                urlComponents = urlparse(args.u)

            self.protocol = urlComponents.scheme
            self.hostname = urlComponents.netloc

            if urlComponents.port:
                self.port = urlComponents.port
            else:
                self.port = '80'

            if urlComponents.query:
                self.path = urlComponents.path
                self.params = urlComponents.query

            self.url = self.protocol + "://" + self.hostname + ":" + str(self.port) + self.path
            self.fullpath = self.url + "?" + self.params

            self._output_path = "%s%s" % (
                os.path.join(self.data_path, "sqlmap_output-"),
                re.sub(r'[\n\/]', r'', base64.b64encode(args.u.encode()).strip().decode()))

        if not args.s:
            return "%s -s %s" % (command_string, self._output_path)

    def setHost(self):
        pass


def createPlugin():
    return SqlmapPlugin()


# I'm Py3
