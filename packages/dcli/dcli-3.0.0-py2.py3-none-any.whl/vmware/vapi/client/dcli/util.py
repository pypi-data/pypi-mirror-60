"""
dcli util classes
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2015-2020 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import os
import io
import sys
import textwrap
import logging
import time
import json
import re
import six
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from requests.exceptions import SSLError
from vmware.vapi.data.value import OptionalValue
from vmware.vapi.client.dcli.options import CliOptions

if six.PY2:
    from cgi import escape as imported_html_escape
else:
    from html import escape as imported_html_escape

try:
    from html import unescape  # python 3.4+
except ImportError:
    try:
        from html.parser import HTMLParser  # python 3.x (<3.4)
    except ImportError:
        from HTMLParser import HTMLParser  # python 2.x
    unescape = HTMLParser().unescape

try:
    have_pyprompt = True
    from prompt_toolkit import print_formatted_text, HTML, prompt  # pylint: disable=W0611
    import pygments  # pylint: disable=W0611
except ImportError:
    have_pyprompt = False


def print_dcli_text(*values, **kwargs):
    """
    Uses prompt_toolkit HTML syntax to print console output
    If prompt_toolkit not provided, removes and tags like chars from string
    and prints using builtin print function
    Text need to be html escaped!
    """
    if have_pyprompt and CliOptions.DCLI_COLORS_ENABLED and CliOptions.DCLI_COLORED_OUTPUT:
        if values:
            return print_formatted_text(HTML(*values), **kwargs)
        return print_formatted_text(*values, **kwargs)
    # we need to remove tags from string if there's no prompt_toolkit
    edited_values = []
    for val in values:
        edited_values.append(unescape(re.sub(r'<.*?>', '', val)))
    return print(*edited_values, **kwargs)


def html_escape(text):
    """
    Html escapes text. Used in this module to do proper import
    for each python in one place.

    :type  text: :class:`str`
    :param text: Text to be html escaped

    :rtype:  :class:`str`
    :return: html escaped text
    """
    return imported_html_escape(text, quote=False)  # pylint: disable=W1505


class StatusCode(object):
    """
    CLI client status codes
    """
    SUCCESS = 0
    INVALID_COMMAND = 1
    INVALID_ARGUMENT = 2
    INVALID_ENV = 3
    NOT_AUTHENTICATED = 4

    def __init__(self):
        pass


try:
    import argparse
except ImportError as e:
    print_dcli_text('<ansired>Error: No argparse module present quitting.</ansired>', file=sys.stderr)
    sys.exit(StatusCode.INVALID_ENV)

from vmware.vapi.client.dcli.exceptions import (  # pylint: disable=C0413,C0412
    handle_error, handle_ssl_error, ParsingExit, InvalidCSPToken,
    ParsingError)


command_exec_report = {}

logger = logging.getLogger(__name__)

UNION_CASE = "UnionCase"
UNION_TAG = "UnionTag"


class ServerTypes(object):
    """
    Defines server types dcli currently supports
    """
    Internal = 0
    VSPHERE = 1
    VMC = 2
    NSX = 3
    NSX_ONPREM = 4


def get_console_size():
    """ Get console height and width """
    # Twisted from ActiveState receipe 440694
    height, width = 25, 80
    import struct
    if os.name == 'nt':
        # Windows
        from ctypes import windll, create_string_buffer

        struct_fmt = "hhhhhhhhhhh"
        buf_size = len(struct_fmt) * 2
        hdl = windll.kernel32.GetStdHandle(-12)
        screen_buf_inf = create_string_buffer(buf_size)
        ret = windll.kernel32.GetConsoleScreenBufferInfo(hdl, screen_buf_inf)

        if ret:
            (_, _, _, _, _, sr_windows_left, sr_windows_top,
             sr_windows_right, sr_windows_bottom, _, _) = struct.unpack(struct_fmt, screen_buf_inf.raw)
            width = sr_windows_right - sr_windows_left + 1
            height = sr_windows_bottom - sr_windows_top + 1
    else:
        # Posix
        import fcntl
        import termios
        tio_get_windows_size = struct.pack(str("HHHH"), 0, 0, 0, 0)
        try:
            ret = fcntl.ioctl(1, termios.TIOCGWINSZ, tio_get_windows_size)
        except Exception:
            logger.warning('ioctl to determine console size failed')
            return height, width
        height, width = struct.unpack("HHHH", ret)[:2]

    if height > 0 and width > 0:
        return height, width
    return 25, 80


def get_wrapped_text(text, width):
    """
    Word wrap a given text based upon given width

    :type  text: :class:`str`
    :param text: Text to be word wrapped
    :type  width: :class:`int`
    :param width: Width to be word wrapped to

    :rtype:  :class:`list` of :class:`str`
    :return: List of word wrapped strings
    """
    wrapper = textwrap.TextWrapper(width=width)
    return wrapper.wrap(text)


default_options_warning_showed = False


def show_default_options_warning(configuration_file):
    """
    Helper method which takes care to show warning for
    invalid configuration file only once.

    :type configuration_file: :class:`bool`
    :param configuration_file: The invalid configuration file
    """
    global default_options_warning_showed  # pylint: disable=W0603
    if default_options_warning_showed is False:
        warning_msg = ("WARNING: Invalid configuration file detected: '{}'.\n"
                       "Turning off default options feature.").format(configuration_file)
        handle_error(warning_msg, prefix_message='')
        default_options_warning_showed = True


def print_top_level_help(interactive_mode, server_type):
    """
    Print the top level dcli help

    :type interactive_mode: :class:`bool`
    :param interactive_mode: Specifies whether dcli is in interactive mode or not
    """
    print_dcli_text('<b>Welcome to VMware Datacenter CLI (DCLI)</b>\n')
    if not interactive_mode:
        help_msg = 'usage: <b>{} {}</b>\n\n'.format(CliOptions.CLI_CLIENT_NAME, html_escape('<namespaces> <command>'))
        help_msg += 'To connect to specified vAPI server: <b>{} +server {}</b>\n'.format(CliOptions.CLI_CLIENT_NAME, html_escape('<server>'))
        help_msg += 'To connect to VMC: <b>{0} +vmc-server</b> or simply: <b>{0} +vmc</b>\n'.format(CliOptions.CLI_CLIENT_NAME)
        help_msg += 'To connect to NSX: <b>{0} +nsx-server {1}</b> or simply: <b>{0} +nsx {1}</b>\n'.format(CliOptions.CLI_CLIENT_NAME, html_escape('<nsx-server>'))
        help_msg += 'To enter interactive shell mode: <b>{0} +interactive</b> or simply: <b>{0} +i</b>\n'.format(CliOptions.CLI_CLIENT_NAME)
        help_msg += 'To execute dcli internal command: <b>{0} env</b>\n'.format(CliOptions.CLI_CLIENT_NAME)
        help_msg += 'For detailed help please use: <b>{0} --help</b>\n'.format(CliOptions.CLI_CLIENT_NAME)
    else:
        help_msg = 'usage: <b>{}</b>\n\n'.format(html_escape('<namespaces> <command>'))
        help_msg += 'To auto-complete and browse DCLI namespaces:   <b>[TAB]</b>\n'
        if ServerTypes.VSPHERE == server_type:
            help_msg += 'If you need more help for a command:           <b>vcenter vm get --help</b>\n'
            help_msg += 'If you need more help for a namespace:         <b>vcenter vm --help</b>\n'
        elif ServerTypes.VMC == server_type:
            help_msg += 'If you need more help for a command:           <b>vmc orgs sddc get --help</b>\n'
            help_msg += 'If you need more help for a namespace:         <b>vmc orgs --help</b>\n'
        elif ServerTypes.NSX == server_type:
            help_msg += 'If you need more help for a command:           <b>nsx policy api v1 infra get --help</b>\n'
            help_msg += 'If you need more help for a namespace:         <b>nsx policy api v1 infra --help</b>\n'
        else:
            help_msg += 'To connect to specified vAPI server: <b>+server {}</b>\n'.format(html_escape('<server>'))
            help_msg += 'To connect to VMC: <b>+vmc-server</b> or simply: <b>+vmc</b>\n'
            help_msg += 'To connect to NSX: <b>+nsx-server {0}</b> or simply: <b>+nsx {0}</b>\n'.format(html_escape('<nsx-server>'))
        help_msg += 'To execute dcli internal command: <b>env</b>\n'
        help_msg += 'For detailed information on DCLI usage visit:  <b>http://vmware.com/go/dcli</b>\n'
    print_dcli_text(help_msg)


def prompt_for_credentials(server_type, username=None, credstore_add=None, org_id=None, is_gov_cloud=None):
    """
    Prompts user for credentials

    :type server_type: :class:`int`
    :param server_type: server type to give string value for
    :type username: :class:`str`
    :param username: username; if different from None, function does not prompt for it.
    :type credstore_add: :class:`bool`
    :param credstore_add: specifies whether to add credentials in credentials store and not ask for confirmation
    :type org_id: :class:`str`
    :param org_id: If provided and server_type is VMC or NSX ask for refresh token for specified organization
    :type is_gov_cloud: :class:`bool`
    :param is_gov_cloud: specifies whether credentials needed are for gov cloud instance or not

    :return: prompted username, password, and whether credentials should
        be stored in credstore
    """
    if server_type == ServerTypes.Internal:
        return None, None, False
    password = None

    try:
        # For Python 3 compatibility
        input_func = raw_input  # pylint: disable=W0622
    except NameError:
        input_func = input

    import getpass
    if server_type in (ServerTypes.VMC, ServerTypes.NSX) or is_gov_cloud:
        if org_id is None:
            input_message = 'Refresh Token: '
        else:
            input_message = "Refresh Token (for Organization with ID {}): ".format(org_id)
        username = None
        if have_pyprompt:
            password = prompt(input_message, is_password=True)
        else:
            password = getpass.getpass(input_message).strip()
    else:
        if not username:
            username = input_func('Username: ')
        if have_pyprompt:
            password = prompt('Password: ', is_password=True)
        else:
            password = getpass.getpass(str('Password: '))

    if credstore_add:
        return username, password, True

    credstore_flag = False
    if server_type in (ServerTypes.VMC, ServerTypes.NSX):
        credstore_answer = \
            input_func('Do you want to save refresh token in the '
                       'credstore? (y or n) [y]:')
    else:
        credstore_answer = \
            input_func('Do you want to save credentials in the '
                       'credstore? (y or n) [y]:')
    if credstore_answer.lower().strip() in ['', 'true', 'yes', 'y', 't']:
        credstore_flag = True

    return username, password, credstore_flag


def derive_key_and_iv(password, salt, key_length, iv_length):
    """
    Get key and initialization vector for AES encryption

    :type   password: :class:`str`
    :param  password: Password used for encryption
    :type   salt: :class:`str`
    :param  salt: Encryption salt
    :type   key_length: :class:`str`
    :param  key_length: Encryption key length
    :type   iv_length: :class:`str`
    :param  iv_length: IV length

    :rtype:  :class:`str`
    :return: Encryption Key
    :rtype:  :class:`str`
    :return: Initialization Vector
    """
    d = d_i = ''
    from hashlib import sha256
    while len(d) < key_length + iv_length:
        d_i = sha256(d_i.encode() + password.encode() + salt).hexdigest()
        d += d_i
    key = d[:key_length]
    iv = d[key_length:key_length + iv_length]

    if six.PY2:
        key = key.encode('utf-8')
        iv = iv.encode('utf-8')
    else:
        key = six.b(key)
        iv = six.b(iv)

    return key, iv


def encrypt(input_pwd, password, key_length=32):
    """
    Method to encrypt password

    :type   input_pwd: :class:`str`
    :param  input_pwd: Password to be encrypted
    :type   password: :class:`str`
    :param  password: Password used to do encryption
    :type   key_length: :class:`int`
    :param  key_length: Encryption key length

    :rtype: :class:`str`
    :return: Base64 encoded encrypted password
    """
    block_size = 16
    salt = os.urandom(block_size - len('Salted__'))
    key, iv = derive_key_and_iv(password, salt, key_length, block_size)
    backend = default_backend()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()

    # Add padding if input password is not multiple of block size
    if not input_pwd or len(input_pwd) % block_size != 0:
        padding_length = (block_size - len(input_pwd) % block_size) or block_size
        input_pwd += padding_length * chr(padding_length)

    if six.PY2:
        input_pwd = input_pwd.encode('utf-8')
    else:
        input_pwd = six.b(input_pwd)

    encrypted = b'Salted__' + salt + encryptor.update(input_pwd) + encryptor.finalize()
    import base64
    return (base64.encodestring(encrypted) if six.PY2 else  # pylint: disable=W1505
            base64.encodebytes(encrypted))  # pylint: disable=E1101,W1505


def decrypt(encoded_pwd, password, key_length=32):
    """
    Method to decrypt password

    :type   encoded_pwd: :class:`str`
    :param  encoded_pwd: Password to be decrypted
    :type   password: :class:`str`
    :param  password: Password used to do encryption
    :type   key_length: :class:`int`
    :param  key_length: Encryption key length

    :rtype: :class:`str`
    :return: Decrypted password
    """
    import base64
    if six.PY3 and not isinstance(encoded_pwd, bytes):
        encoded_pwd = encoded_pwd.encode()
    encoded_pwd = base64.decodestring(encoded_pwd)  # pylint: disable=W1505

    block_size = 16
    salt = encoded_pwd[:block_size][len('Salted__'):]
    key, iv = derive_key_and_iv(password, salt, key_length, block_size)
    backend = default_backend()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()

    pwd = decryptor.update(encoded_pwd[block_size:]) + decryptor.finalize()

    if six.PY3:
        pwd = pwd.decode()

    # return password after removing padding
    if pwd and pwd[-1] in [chr(i) for i in range(15)]:
        pwd = pwd.rstrip(pwd[-1])

    return pwd


def calculate_time(fn, info, command=None):
    """
    Helper function to measure execution time of a function

    :param fn: function to execute
    :type fn: :class:`function`
    :param info: short information for the executable function
    :type info: :class:`str`
    :param command: dcli command currently executed.
    If none the measurement result is appended to the last command added.
    :type command: :class:`str`
    :return: Actual result from the :param fn: function
    :rtype: :class:`object`
    """
    if CliOptions.DCLI_PROFILE_FILE:
        if command:
            if 'command' not in command_exec_report:
                command_exec_report['command'] = command
                report_item = command_exec_report
            elif command_exec_report['command'] == command:
                report_item = command_exec_report
            else:
                report_item = {'command': command}
                command_exec_report.setdefault('shell_commands', []).append(report_item)
        else:
            if 'shell_commands' in command_exec_report:
                report_item = command_exec_report['shell_commands'][-1]
            else:
                report_item = command_exec_report

        measurement = {'info': info}

        # to ensure report tree has correct hierarchical structure
        # add measurement to the right most node of report tree which has no time_taken filled yet.
        while 'measurements' in report_item and report_item['measurements']:
            if 'time_taken' in report_item['measurements'][-1]:
                break
            report_item = report_item['measurements'][-1]
        report_item.setdefault('measurements', []).append(measurement)

        start_time = time.time()
        result = fn()
        execution_time = time.time() - start_time

        measurement['time_taken'] = '{0:2f}sec'.format(execution_time)
    else:
        result = fn()

    return result


def save_report_to_file():
    """
    Saves dcli commands execution report
    to the file specified by DCLI_PROFILE_FILE env variable

    :return:
    :rtype: None
    """
    if CliOptions.DCLI_PROFILE_FILE:
        with io.open(CliOptions.DCLI_PROFILE_FILE, 'a', encoding='utf-8') as times_file:
            val = json.dumps(command_exec_report, indent=4, sort_keys=True)
            result = six.text_type(val if times_file.tell() == 0 else ',' + val)
            times_file.write(result)


def is_field_union_tag(field_name, metadata_struct_info):
    """
    Checks whether a given structure field name is found in a structure and is
    a union tag

    :param field_name: field name of the structure's member
    :type field_name: :class:`str`
    :param metadata_struct_info: metadata info of the structure to check
        against
    :type metadata_struct_info:
        :class:`vmware.vapi.client.dcli.metadata.metadata_info.StructureInfo`
    :return: True if given field_name is union tag, False otherwise
    :rtype: :class:`bool`
    """
    if not metadata_struct_info:
        return False
    return next((True for mm_field in metadata_struct_info.fields
                 if mm_field.name == field_name and mm_field.is_union_tag()), False)


def is_field_union_case(field_name, metadata_struct_info):
    """
    Checks whether a given structure field name is found in a structure and is
    a union case

    :param field_name: field name of the structure's member
    :type field_name: :class:`str`
    :param metadata_struct_info: metadata info of the structure to check
        against
    :type metadata_struct_info:
        :class:`vmware.vapi.client.dcli.metadata.metadata_info.StructureInfo`
    :return: True if given field_name is union case, False otherwise
    :rtype: :class:`bool`
    """
    if not metadata_struct_info:
        return False
    return next((True for mm_field in metadata_struct_info.fields
                 if mm_field.name == field_name and mm_field.is_union_case()), False)


def get_metadata_field_info(field_name, metadata_struct_info):
    """
    Get metamodel information for a field

    :param field_name: field name of the structure's member
    :type field_name: :class:`str`
    :param metadata_struct_info: metamodel info of the structure
    :type metadata_struct_info:
        :class:`com.vmware.vapi.metadata.metamodel_client.StructureInfo`
    :return: Metamodel representation object
    :rtype: :class:`com.vmware.vapi.metadata.metamodel_client.FieldInfo`
    """
    return next((mm_field for mm_field in metadata_struct_info.fields
                 if mm_field.name == field_name), None)


def union_case_matches_union_tag_value(union_field_info, union_tags):
    """
    Verifies whether a union case field should be visible based on a union tag

    :param union_field_info: metamodel presentation of the union case
    :type union_field_info: :class:`com.vmware.vapi.metadata.metamodel_client
                                                            .FieldInfo`
    :param union_tags: datavalue presentation of the union tags
    :type union_tags: :class: class:`list` of :class:`tuple`
    :return: True if UnionCase field matches UnionTag value
    :rtype: :class:`bool`
    """
    if not union_field_info.is_union_case():
        err_msg = 'Invalid union field value found.'
        handle_error(err_msg)
        return False

    for tag_name, tag_value in union_tags:
        if isinstance(tag_value, OptionalValue):
            if tag_value.value is None:
                return False
            tag_value = tag_value.value
        if tag_name != union_field_info.union_case.tag_name:
            continue
        for union_case_value in union_field_info.union_case.list_value:
            if tag_value.value == union_case_value:
                return True
    return False


def get_csp_encoded_tokens(session, refresh_token):
    """
    Fetches VMC authentication token

    :param session: requests session object which would make the http requests
    :type session: :class: `requests.sessions.Session`
    :param refresh_token: refresh token to get csp JWT encoded tokens for
    :type refresh_token: :class:`str`

    :return: VMC token
    :rtype: :class:`str`
    """
    # get CSP server uri
    auth_token = id_token = None
    csp_uri = CliOptions.DCLI_VMC_CSP_URL
    if not csp_uri:
        error_msg = ('Please set DCLI_VMC_CSP_URL environment variable to '
                     'valid CSP service URL.')
        handle_error(error_msg)
        raise Exception(error_msg)
    logger.info('Using CSP address "%s"', csp_uri)

    if not refresh_token:
        error_msg = ('No refresh token provided. Provide a '
                     'valid refresh token for authentication to VMC '
                     'when prompted')
        handle_error(error_msg)
        raise Exception(error_msg)
    try:
        # striping last / so that the user provided url with
        # or without it would be valid
        csp_uri = csp_uri.strip().rstrip('/')  # triming last slash and any whitespaces
        request_url = CliOptions.GET_VMC_ACCESS_TOKEN_PATH.format(csp_uri)
        data = "refresh_token=%s" % refresh_token.strip()  # removing any whitespaces before or after refresh token
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        logger.info('Making request for getting csp token to "%s"', request_url)
        token_response = session.post(request_url,
                                      data=data,
                                      headers=headers)
        if token_response.status_code == 400:
            raise InvalidCSPToken('Invalid token response returned', token_response)
        auth_token = token_response.json()['access_token']
        id_token = token_response.json()['id_token']
    except SSLError as e:
        handle_ssl_error(e)
    except Exception as e:
        error_msg = ('Unable to obtain VMC authentication token. '
                     'Using CSP login address: %s (override using DCLI_VMC_CSP_URL env var). '
                     'Are you sure you have provided correct refresh token?\r\n'
                     'Error: %s' % (csp_uri, str(e)))
        handle_error(error_msg, exception=e)
        raise e
    return auth_token, id_token


def get_decoded_JWT_token(refresh_token=None, encoded_token=None, session=None):
    """
    Returns decoded JWT CSP token either provided directly or
    produced from refresh token. If produced from refresh token
    authentication token is used from response.
    If both refresh_token and encoded_token
    provided, method would raise an Exception.

    :param refresh_token: CSP Refresh token to get auth token from
    :type refresh_token: :class:`str`
    :param encoded_token: Decoded JWT token to decode
    :type encoded_token: :class:`str`
    :param session: requests session object which would make the http requests
        in case of refresh token provided
    :type session: :class: `requests.sessions.Session`
    :return: decoded JWT token
    :rtype: :class:`str`
    """
    if refresh_token is None and encoded_token is None \
            or refresh_token and encoded_token:
        raise Exception('You need to provide either refresh_token or encoded_token.')

    if session is None:
        import requests
        session = requests.Session()
        session.verify = CliOptions.DCLI_CACERTS_BUNDLE

    if refresh_token is not None:
        token, _ = get_csp_encoded_tokens(session, refresh_token)
    else:
        token = encoded_token

    payload = token.split('.')[1]

    pad = len(payload) % 4
    if pad > 0:
        payload += '=' * (4 - pad)

    import base64
    # getting payload of token and returning decoded json object
    if six.PY2:
        return json.loads(base64.decodestring(payload))  # pylint: disable=W1505
    else:
        if not isinstance(payload, bytes):
            payload = bytes(payload, encoding='utf-8')
        return json.loads(base64.decodebytes(payload).decode())


class DcliContext(object):
    """
    Class used to collect dcli context
    """
    def __init__(self, **kwargs):
        self.configuration_path = kwargs.get('configuration_path')
        self.server = kwargs.get('server')
        self.server_type = kwargs.get('server_type')


class CliGenericTypes(object):
    """
    Defines dcli recognized generic types
    """
    list_type = 'list'
    optional_type = 'optional'
    optional_list_type = 'optional_list'
    list_of_optional_type = 'list_optional'
    none_type = ''


class TypeInfoGenericTypes(object):
    """
    Defines generic types used by
    :class:`com.vmware.vapi.client.dcli.metadata.metadata_info.TypeInfo`
    """
    optional_type = 'optional'
    list_type = 'list'
    set_type = 'set'
    map_type = 'map'


class CliArgParser(argparse.ArgumentParser):
    """
    Class to catch argparse errors
    """
    def error(self, message):
        """
        Extend argparse error method
        """
        raise ParsingError(message)

    def exit(self, status=0, message=None):
        """
        Extend argparse exit method
        """
        raise ParsingExit(status, message)


class CliHelpFormatter(argparse.HelpFormatter):
    """
    Class to define dcli help formatter to use screen width for help
    """
    def __init__(self,
                 prog,
                 width=None):
        _, width = get_console_size()
        argparse.HelpFormatter.__init__(self, prog, width=width)
        return


class BoolAction(argparse.Action):
    """
    Class to define boolean argparse action
    """
    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,   # pylint: disable=W0622
                 choices=None,
                 required=False,
                 help=None,  # pylint: disable=W0622
                 metavar=None):
        argparse.Action.__init__(self,
                                 option_strings=option_strings,
                                 dest=dest,
                                 nargs=nargs,
                                 const=const,
                                 default=default,
                                 type=type,
                                 choices=choices,
                                 required=required,
                                 help=help,
                                 metavar=metavar)
        return

    def __call__(self, parser, namespace, values, option_string=None):
        values = CliHelper.str_to_bool(values)
        setattr(namespace, self.dest, values)


class BoolAppendAction(argparse.Action):
    """
    Class to define boolean argparse append action
    """
    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,   # pylint: disable=W0622
                 choices=None,
                 required=False,
                 help=None,  # pylint: disable=W0622
                 metavar=None):
        argparse.Action.__init__(self,
                                 option_strings=option_strings,
                                 dest=dest,
                                 nargs=nargs,
                                 const=const,
                                 default=default,
                                 type=type,
                                 choices=choices,
                                 required=required,
                                 help=help,
                                 metavar=metavar)
        return

    def __call__(self, parser, namespace, values, option_string=None):
        values = CliHelper.str_to_bool(values)

        if getattr(namespace, self.dest) is None:
            setattr(namespace, self.dest, [])
        items = getattr(namespace, self.dest)
        items.append(values)
        setattr(namespace, self.dest, items)


class SecurityContextManager(object):
    """Context manager class which ensures security context for provided connector is not changed permanently"""

    def __init__(self, connector, security_context):
        self.security_context = security_context
        self.connector = connector
        self.previous_security_context = connector.get_api_provider().get_security_context(None)

    def __enter__(self):
        self.connector.set_security_context(self.security_context)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.connector.set_security_context(self.previous_security_context)


class CliHelper(object):
    """
    CLI helper class to provide various helper functions for CLI client
    """
    def __init__(self):
        pass

    @staticmethod
    def get_parser(interactive):
        """
        Get the CliArgParser object with all input vcli arguments configured

        :type: :class:`bool`
        :param: Flag if we are in interactive mode or not

        :rtype:  :class:`CliArgParser`
        :return: CliArgParser object
        """
        parser = CliArgParser(prog=CliOptions.CLI_CLIENT_NAME,
                              prefix_chars='+',
                              description='VMware Datacenter Command Line Interface',
                              formatter_class=CliHelpFormatter,
                              add_help=False)
        mutex_groups = {}

        options = CliOptions.get_interactive_parser_plus_options()
        if not interactive and have_pyprompt:
            # insert interactive and prompt options, right after server parameters
            options[5:5] = CliOptions.get_non_interactive_parser_plus_options()

        for option in options:
            kwargs = {
                'action': option.arg_action,
                'help': option.description,
            }

            if option.choices:
                kwargs['choices'] = option.choices
            if option.default is not None:
                kwargs['default'] = option.default
            if option.const is not None:
                kwargs['const'] = option.const
            if option.nargs is not None:
                kwargs['nargs'] = option.nargs

            if option.mutex_group:
                if option.mutex_group not in mutex_groups:
                    mutex_groups[option.mutex_group] = parser.add_mutually_exclusive_group()
                mutex_groups[option.mutex_group].add_argument(option.name, **kwargs)
            else:
                parser.add_argument(option.name, **kwargs)

        parser.add_argument('args', nargs='*', help='CLI command')

        return parser

    @staticmethod
    def str_to_bool(value):
        """
        Method to convert a string to boolean type
        """
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        else:
            raise ParsingError("Invalid boolean value '%s' specified" % value)

    @staticmethod
    def strip_quotes(value):
        """
        Method to strip quotes from start and end of a string
        """
        return value.lstrip('"').rstrip('"').lstrip("'").rstrip("'")

    @staticmethod
    def get_cli_args(command):
        """
        Method to convert tokens into cli-friendly args
        """
        # XXX Revisit this tokenizer logic to be more robust

        tokens = re.split(r'\s', command)
        arg_list = []
        prev = ''
        in_word = False
        for token in tokens:
            if in_word:
                prev += ' %s' % token
                if token.endswith('"') or token.endswith("'"):
                    arg_list.append(prev)
                    prev = ''
                    in_word = False
            elif token.startswith('"') or token.startswith("'"):
                prev += token
                if token.endswith('"') or token.endswith("'"):
                    arg_list.append(prev)
                    prev = ''
                else:
                    in_word = True
            elif token:
                arg_list.append(token)

        return [CliHelper.strip_quotes(arg) for arg in arg_list]

    @staticmethod
    def get_args_values(command):
        """
        For given command returns dictionary of all the input arguments
        and their value

        :type command: :class:`int`
        :param command: dcli command string
        :rtype: :class:`dict` of :class:`str` and :class:`str`
        :return: dictionary of all input arguments and their values
        """
        tokens_regex = re.compile(r'(--[^\s]*|\+[^\s]*)\s*(".*"|\'.*\'|(?!--)(?!\+)[^\s]*)')
        return {group[0]: group[1] for group in tokens_regex.findall(command)}

    @staticmethod
    def get_module_name(server_type):
        """
        gives string value for specified server type

        :type server_type: :class:`int`
        :param server_type: server type to give string value for
        :rtype: :class:`str`
        :return: string representation of module name
        """
        if server_type == ServerTypes.VMC:
            return 'vmc'
        elif server_type == ServerTypes.NSX:
            return 'nsx'
        elif server_type == ServerTypes.VSPHERE:
            return 'vsphere'
        return 'dcli'

    @staticmethod
    def configure_logging(log_level, verbose=False, file_path=None):
        """
        Method to configure dcli logging
        """
        if file_path is None:
            file_path = CliOptions.LOG_FILE_DEFAULT_VALUE

        if log_level == 'debug':
            log_level = logging.DEBUG
        elif log_level == 'info':
            log_level = logging.INFO
        elif log_level == 'warning':
            log_level = logging.WARNING
        elif log_level == 'error':
            log_level = logging.ERROR
        elif log_level == 'critical':
            log_level = logging.CRITICAL

        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)-15s %(message)s')
        file_handler.setFormatter(formatter)

        def update_logger(dcli_logger):
            """
            Decorate each logger as necessary for correct output in dcli context.

            :type dcli_logger: :class:`obj`
            :param dcli_logger: server type to give string value for
            """

            dcli_logger.setLevel(log_level)
            dcli_logger.addHandler(file_handler)

            if verbose:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.name = 'console_handler'
                console_handler.setLevel(logging.DEBUG)
                dcli_logger.setLevel(logging.DEBUG)
                console_handler.setFormatter(formatter)
                dcli_logger.addHandler(console_handler)
            else:
                remove_handlers = [handler for handler in root_logger.handlers
                                   if handler.name == 'console_handler']
                for handler in remove_handlers:
                    dcli_logger.removeHandler(handler)

        # Configure the root logger
        root_logger = logging.getLogger()
        update_logger(root_logger)

        # get vapi runtime requests logger
        from vmware.vapi.protocol.client.msg.json_connector import request_logger as vapi_requests_logger
        update_logger(vapi_requests_logger)

        global logger  # pylint: disable=W0603
        logger = logging.getLogger('vmware.vapi.client.dcli.util')
