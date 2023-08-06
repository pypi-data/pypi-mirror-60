"""
This module handles dcli credstore operations
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2015-2020 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

from collections import OrderedDict
from functools import wraps
import os
import stat
import sys
import logging
import six

from vmware.vapi.client.dcli.util import (
    StatusCode, encrypt, decrypt, get_decoded_JWT_token)
from vmware.vapi.client.dcli.exceptions import (
    extract_error_msg, handle_error, InvalidCSPToken)
from vmware.vapi.client.dcli.options import CliOptions
from vmware.vapi.client.lib.formatter import Formatter

try:
    import simplejson as json
except ImportError:
    import json

logger = logging.getLogger(__name__)


try:
    from ctypes import windll, create_string_buffer
    import msvcrt

    # XXX: Pepify all the names
    class AutoFileLockBase(object):
        """
        Base class for windows credstore file locking
        """
        # Size of 64 bits OVERLAPPED struct
        _OVERLAPPED_BUFSIZE = 8 * 2 + 4 * 2 + 8

        # Lock region low, high dword
        _LOCK_LOW, _LOCK_HIGH = 0x0, 0x80000000

        def __init__(self):
            pass

        @staticmethod
        def _GetLockFlags():
            """
            Returns flag for SHARED, EXCLUSIVE, FLAGS_NB
            """
            return 0x0, 0x2, 0x1

        @staticmethod
        def _GetHandle(fd):
            """
            Get Windows Handle from python file handle
            """
            return msvcrt.get_osfhandle(fd.fileno())

        @staticmethod
        def _LockFile(fd, op):
            """
            Lock file
            """
            hdl = AutoFileLockBase._GetHandle(fd)
            dwReserved = 0
            overlapped = create_string_buffer(AutoFileLockBase._OVERLAPPED_BUFSIZE)
            ret = windll.kernel32.LockFileEx(hdl, op, dwReserved,
                                             AutoFileLockBase._LOCK_LOW,
                                             AutoFileLockBase._LOCK_HIGH,
                                             overlapped)
            if ret == 0:
                dwError = windll.kernel32.GetLastError()
                ioError = IOError("%d" % dwError)
                if dwError == 33:  # ERROR_LOCK_VIOLATION
                    import errno
                    ioError.errno = errno.EAGAIN
                raise ioError

        @staticmethod
        def _UnlockFile(fd):
            """
            Unlock file
            """
            hdl = AutoFileLockBase._GetHandle(fd)
            dwReserved = 0
            overlapped = create_string_buffer(AutoFileLockBase._OVERLAPPED_BUFSIZE)
            windll.kernel32.UnlockFileEx(hdl, dwReserved,
                                         AutoFileLockBase._LOCK_LOW,
                                         AutoFileLockBase._LOCK_HIGH,
                                         overlapped)
except ImportError:
    import fcntl

    class AutoFileLockBase(object):
        """
        Base class for posix credstore file locking
        """
        def __init__(self):
            pass

        @staticmethod
        def _GetLockFlags():
            """
            Returns flag for SHARED, EXCLUSIVE, FLAGS_NB
            """
            return fcntl.LOCK_SH, fcntl.LOCK_EX, fcntl.LOCK_NB

        @staticmethod
        def _LockFile(fd, op):
            """
            Lock file
            """
            # Note:
            # - If IOError with [Errno 9] Bad file descriptor, check to make
            #   sure fd is opened with "r+" / "w+"
            # - If non-blocking, but will block, lockf will raise IOError, with
            #   errno set to EACCES or EAGAIN
            fcntl.lockf(fd, op)

        @staticmethod
        def _UnlockFile(fd):
            """
            Unlock file
            """
            fcntl.lockf(fd, fcntl.LOCK_UN)


class AutoFileLock(AutoFileLockBase):
    """
    Class to provide platform independent locking for an open file
    """
    SHARED, EXCLUSIVE, FLAGS_NB = AutoFileLockBase._GetLockFlags()

    # AutoFileLock init
    # @param fd Open file handle
    # @param op SHARED / EXCLUSIVE, optionally or with FLAGS_NB for
    #           non-blocking
    #           If non-blocking and will block, __init__ will raise IOError,
    #           with errno set to EACCES or EAGAIN
    def __init__(self, fd, op):
        """
        AutoFileLock init

        :type  fd: File handle
        :param fd: Open file handle
        :type  op: Locking flags
        :param op: SHARED / EXCLUSIVE, optionally or with FLAGS_NB for
                   non-blocking.
                   If non-blocking and will block, __init__ will raise IOError,
                   with errno set to EACCES or EAGAIN
        """
        super(AutoFileLock, self).__init__()
        self.fd = None
        self._LockFile(fd, op)
        self.fd = fd

    def __enter__(self):
        return self.fd

    def __exit__(self, exc_type, exc_value, traceback):
        if self.fd:
            self._UnlockFile(self.fd)
            self.fd = None


def lock_file(func):
    """
    Decorator used to open credentials store file with read permissions.
    If file does not exist it creates one with read and write owner permissions
    All methods which use this decorator MUST have key-value parameter locked_fd,
    used to further manipulate the file object

    :type   func: :class:`function`
    :param  func: Function to wrap

    :rtype:  :class:`function`
    :return: function which wrapps provided function
    """
    @wraps(func)
    def func_wrapper(*fargs, **kwargs):
        """
        Wrapper function called instead of decorated function.
        """
        return_value = None
        try:
            umask_original = os.umask(0)
            # Only owner should have read-write permissions
            mode = stat.S_IRUSR | stat.S_IWUSR  # This is 0o600 in octal

            # Open and share lock credstore file
            with os.fdopen(os.open(fargs[0].credstore_path, os.O_RDWR | os.O_CREAT, mode), 'r+') as fd:
                with AutoFileLock(fd, AutoFileLock.SHARED) as locked_fd:

                    # adding the file object as argument to be treated further by wrapped functions
                    kwargs['locked_fd'] = locked_fd
                    return_value = func(*fargs, **kwargs)

        except IOError as e:
            if func.__name__ in ['get_vapi_credstore_item', 'get_csp_credstore_item']:
                # wrapper needs to act differently only for the get_vapi_credstore_item and get_csp_credstore_item
                # methods. In this case we need to return None.
                return None

            msg = extract_error_msg(e)
            if msg:
                error_msg = 'Unable to open credstore file %s.'\
                            'Message: %s' % (fargs[0].credstore_path, msg)
                handle_error(error_msg, exception=e)
            return_value = StatusCode.INVALID_ENV
        finally:
            os.umask(umask_original)
        return return_value
    return func_wrapper


_CREDSTORE = 'credstore'
_TYPE = 'type'
_SECRETS = 'secrets'
_ITEMS = 'items'
_VERSION = 'version'
_SERVER = 'server'
_USER = 'user'
_PASSWORD = 'password'
_SESSION_ID = 'session_id'
_AUTH_TOKEN = 'auth_token'
_SESSION_MGR = 'session_manager'
_VMC_ADDRESS = 'vmc_address'
_ORG_ID = 'org_id'
_REFRESH_TOKEN = 'refresh_token'

_CSP_CREDS_TYPE = 'csp'
_VAPI_CREDS_TYPE = 'vapi'


class CredentialsStore(object):
    """
    Class to provide credential store operations for dcli
    """

    _SUPPORTED_VERSION = '1.0'

    def __init__(self, credstore_path):
        """
        CredentialsStore init method
        """
        self.credstore_path = credstore_path
        self.convert_to_version_1_dot_0()

    @lock_file
    def convert_to_version_1_dot_0(self, locked_fd=None):
        """
        Converts credential store to version 1.0 if not converted already

        :type   locked_fd: :class:`file`
        :param  locked_fd: file object representing credentials store file content.
            Automatically passed through @lock_file decorator

        :type   credstore_path: :class:`str`
        :param  credstore_path: Path to credential store file
        """
        try:
            credstore = json.load(locked_fd)
        except ValueError:
            # Likely empty credstore file, set version and return
            credstore = {}
            credstore[_CREDSTORE] = {}
            credstore[_CREDSTORE][_VERSION] = self._SUPPORTED_VERSION

            locked_fd.seek(0)
            locked_fd.truncate()
            locked_fd.write(json.dumps(credstore, indent=4) + '\n')

        if isinstance(credstore[_CREDSTORE], dict) \
                and 'version' in credstore[_CREDSTORE] \
                and credstore[_CREDSTORE][_VERSION] == '1.0':
            return

        items = credstore[_CREDSTORE]

        credstore[_CREDSTORE] = {}
        credstore[_CREDSTORE][_VERSION] = self._SUPPORTED_VERSION

        converted_items = []

        for cred_item in items:
            if cred_item[_USER] == 'vmc_user':
                vmc_user_item = OrderedDict()
                vmc_user_item[_TYPE] = _CSP_CREDS_TYPE
                vmc_user_item[_VMC_ADDRESS] = cred_item[_SERVER]

                try:
                    decrypted_refresh_token = decrypt(cred_item[_PASSWORD],
                                                      vmc_user_item[_VMC_ADDRESS] + 'vmc_user')
                except Exception:
                    error_msg = \
                        ('Error occured while converting credentials store '
                         'and trying to decrypt old password for server address '
                         '"{}" and user "{}"').format(vmc_user_item[_VMC_ADDRESS], cred_item[_USER])
                    handle_error(error_msg)
                    continue

                # in case of staging VMC environment used, we need to set staging csp url too
                backup_csp_value = CliOptions.DCLI_VMC_CSP_URL
                try:
                    if CliOptions.DCLI_VMC_STAGING_SERVER in vmc_user_item[_VMC_ADDRESS]:
                        CliOptions.DCLI_VMC_CSP_URL = CliOptions.DCLI_VMC_STAGING_CSP_URL

                    decoded_token = get_decoded_JWT_token(refresh_token=decrypted_refresh_token)
                except InvalidCSPToken:
                    # either invalid token or invalid VMC address
                    # do not process that entry
                    error_msg = \
                        ('Either invalid refresh token used or invalid vmc address. \n'
                         'Credstore entry for vmc address \'{}\' and user \'{}\' not processed '
                         'credential store conversion.').format(vmc_user_item[_VMC_ADDRESS], cred_item[_USER])
                    handle_error(error_msg)
                    continue
                finally:
                    if backup_csp_value is not None:
                        CliOptions.DCLI_VMC_CSP_URL = backup_csp_value

                vmc_user_item[_USER] = decoded_token["username"]
                vmc_user_item[_ORG_ID] = decoded_token["context_name"]

                new_decrypted_token = encrypt(decrypted_refresh_token, vmc_user_item[_VMC_ADDRESS] + vmc_user_item[_USER])
                vmc_user_item[_SECRETS] = {}
                vmc_user_item[_SECRETS][_REFRESH_TOKEN] = str(new_decrypted_token)

                converted_items.append(vmc_user_item)
            else:
                vapi_creds_item = OrderedDict()
                vapi_creds_item[_TYPE] = _VAPI_CREDS_TYPE
                vapi_creds_item[_SERVER] = cred_item[_SERVER]
                vapi_creds_item[_USER] = cred_item[_USER]
                vapi_creds_item[_SECRETS] = {}
                vapi_creds_item[_SECRETS][_PASSWORD] = cred_item[_PASSWORD]
                vapi_creds_item[_SESSION_MGR] = cred_item[_SESSION_MGR]
                converted_items.append(vapi_creds_item)

        credstore[_CREDSTORE][_ITEMS] = converted_items

        locked_fd.seek(0)
        locked_fd.truncate()
        locked_fd.write(json.dumps(credstore, indent=4) + '\n')

    @lock_file
    def list_all(self, formatter='table', locked_fd=None, fp=sys.stdout):
        """
        List credential store entries from credstore file

        :type   formatter: :class:`str`
        :param  formatter: Output formatter
        :type   locked_fd: :class:`file`
        :param  locked_fd: file object representing credentials store file content.
            Automatically passed through @lock_file decorator

        :rtype:  :class:`StatusCode`
        :return: Status code
        """
        credstore = {}
        # Open and share lock credstore file
        try:
            credstore = json.load(locked_fd)
        except ValueError as e:
            error_msg = 'Invalid credstore file %s' % self.credstore_path
            handle_error(error_msg, exception=e)
            return StatusCode.INVALID_ENV

        from vmware.vapi.data.value import (StringValue, StructValue, ListValue)

        entries = credstore[_CREDSTORE].get(_ITEMS, [])
        # create a data value object so that dcli can output result
        list_val = ListValue()
        for entry in entries:
            struct_val = StructValue('credstore')
            for key, value in six.iteritems(entry):
                if key == 'secrets':
                    continue
                struct_val.set_field(key, StringValue(value))
            list_val.add(struct_val)

        if formatter is None:
            formatter = Formatter('table', fp)
        formatter.format_output(list_val)
        return StatusCode.SUCCESS


class VapiCredentialsStore(CredentialsStore):
    """
    Handles credentials store logic for vapi related credentials
    """

    def __init__(self, credstore_path):
        CredentialsStore.__init__(self, credstore_path)

    @lock_file
    def add(self, server, user, pwd, session_mgr, session_id=None, auth_token=None, locked_fd=None):
        """
        Add a credential store entry to credstore file

        :type   server: :class:`str`
        :param  server: vAPI server URL
        :type   user: :class:`str`
        :param  user: User name to be stored
        :type   pwd: :class:`str`
        :param  pwd: Plain-text password to be stored
        :type   session_mgr: :class:`str`
        :param  session_mgr: Session manager
        :type   session_id: :class:`str`
        :param  session_id: Session id
        :type   auth_token: :class:`str`
        :param  auth_token: authentication token
        :type   locked_fd: :class:`file`
        :param  locked_fd: file object representing credentials store file content.
            Automatically passed through @lock_file decorator

        :rtype:  :class:`StatusCode`
        :return: Status code
        """
        if pwd:
            encrypted_pwd = encrypt(pwd, server + user + session_mgr)
            if six.PY3:
                encrypted_pwd = encrypted_pwd.decode()
            del pwd
        else:
            encrypted_pwd = None

        found = False

        credstore = None
        entries = []

        try:
            credstore = json.load(locked_fd)
        except ValueError:
            # Likely empty credstore file, ignore error and move on
            credstore = None

        if credstore:
            entries = credstore[_CREDSTORE].get(_ITEMS, [])
            for entry in entries:
                json_server = entry.get(_SERVER)
                json_session_mgr = entry.get(_SESSION_MGR)
                json_user = entry.get(_USER)

                if json_server == server and json_user == user and json_session_mgr == session_mgr:
                    # update the password
                    entry[_SECRETS][_PASSWORD] = encrypted_pwd if encrypted_pwd is not None else ''
                    if auth_token:
                        entry[_SECRETS][_AUTH_TOKEN] = auth_token
                    if session_id:
                        entry[_SECRETS][_SESSION_ID] = session_id
                    found = True
                    break

        if not found:
            # create new credstore entry
            new_entry = {}
            new_entry[_TYPE] = _VAPI_CREDS_TYPE
            new_entry[_SERVER] = server
            new_entry[_SESSION_MGR] = session_mgr
            new_entry[_USER] = user if user is not None else ''
            new_entry[_SECRETS] = {}
            new_entry[_SECRETS][_PASSWORD] = encrypted_pwd if encrypted_pwd is not None else ''
            if auth_token:
                new_entry[_SECRETS][_AUTH_TOKEN] = auth_token
            if session_id:
                new_entry[_SECRETS][_SESSION_ID] = session_id
            entries.append(new_entry)

        if credstore is None:
            credstore = {_CREDSTORE: {_VERSION: self._SUPPORTED_VERSION}}
        if _ITEMS not in credstore:
            credstore[_CREDSTORE][_ITEMS] = []

        credstore[_CREDSTORE][_ITEMS] = entries
        locked_fd.seek(0)
        locked_fd.truncate()
        locked_fd.write(json.dumps(credstore, indent=4) + '\n')
        return StatusCode.SUCCESS

    @lock_file
    def remove(self, server, user, session_mgr, locked_fd=None):
        """
        Remove a credential store entry from credstore file

        :type   server: :class:`str`
        :param  server: vAPI server URL
        :type   user: :class:`str`
        :param  user: User name
        :type   session_mgr: :class:`str`
        :param  session_mgr: Session manager, if session manager is None and if only 1 entry exists
                for given user and server it will be removed
        :type   locked_fd: :class:`file`
        :param  locked_fd: file object representing credentials store file content.
            Automatically passed through @lock_file decorator

        :rtype:  :class:`StatusCode`
        :return: Status code
        """
        if user is None:
            user = ''

        credstore = {}
        try:
            credstore = json.load(locked_fd)
        except ValueError:
            error_msg = 'Invalid credstore file %s' % self.credstore_path
            handle_error(error_msg)
            return StatusCode.INVALID_ENV

        entries = credstore[_CREDSTORE].get(_ITEMS, [])
        vapi_entries = [entry for entry in entries if entry[_TYPE] == _VAPI_CREDS_TYPE]
        other_entries = [entry for entry in entries if entry[_TYPE] != _VAPI_CREDS_TYPE]

        # remove node with given server/user/session_mgr combination
        try:
            if session_mgr:
                non_match_entries = [entry for entry in vapi_entries
                                     if not (entry.get(_SERVER) == server
                                             and entry.get(_SESSION_MGR) == session_mgr
                                             and entry.get(_USER) == user)]
                if non_match_entries == vapi_entries:
                    raise Exception()
            else:
                entry_match = []
                non_match_entries = []
                for entry in vapi_entries:
                    if entry.get(_SERVER) == server:
                        if not user or entry.get(_USER) == user:
                            entry_match.append(entry)
                    else:
                        non_match_entries.append(entry)

                if not entry_match:
                    raise Exception()

                if len(entry_match) > 1:
                    handle_error('Found more than one credstore entry for given user and server, pass session manager')
                    return StatusCode.INVALID_COMMAND
        except Exception as e:
            err_msg = "Couldn't find credstore entry. "
            err_msg += "Please pass correct user and server values"
            handle_error(err_msg, exception=e)
            return StatusCode.INVALID_COMMAND
        credstore[_CREDSTORE][_ITEMS] = non_match_entries + other_entries
        locked_fd.seek(0)
        locked_fd.truncate()
        locked_fd.write(json.dumps(credstore, indent=4) + '\n')
        return StatusCode.SUCCESS

    @lock_file
    def remove_session_ids(self, server=None, user=None, session_manager=None, locked_fd=None):
        """
        Removes session ids in credentials store for specified one or none of
        server, user, and session manager

        :type   server: :class:`str`
        :param  server: Server
        :type   user: :class:`str`
        :param  user: user name
        :type   session_manager: :class:`str`
        :param  session_manager: session manager string
        :type   locked_fd: :class:`file`
        :param  locked_fd: file object representing credentials store file content.
            Automatically passed through @lock_file decorator
        """
        credstore = {}
        try:
            credstore = json.load(locked_fd)
        except ValueError:
            error_msg = 'Invalid credstore file %s' % self.credstore_path
            handle_error(error_msg)
            return
        entries = credstore[_CREDSTORE].get(_ITEMS, [])
        vapi_entries = [entry for entry in entries if entry[_TYPE] == _VAPI_CREDS_TYPE]
        other_entries = [entry for entry in entries if entry[_TYPE] != _VAPI_CREDS_TYPE]

        non_match_entries = []
        match_entries = []
        if not server:
            match_entries = vapi_entries
        else:
            if user is None:
                for entry in vapi_entries:
                    if entry.get(_SERVER) == server \
                            and (session_manager is None
                                 or entry.get(_SESSION_MGR) == session_manager):
                        match_entries.append(entry)
                    else:
                        non_match_entries.append(entry)
            else:
                for entry in vapi_entries:
                    if entry.get(_SERVER) == server \
                            and (session_manager is None
                                 or entry.get(_SESSION_MGR) == session_manager) \
                            and entry.get(_USER) == user:
                        match_entries.append(entry)
                    else:
                        non_match_entries.append(entry)

        for entry in match_entries:
            if _AUTH_TOKEN in entry[_SECRETS]:
                del entry[_SECRETS][_AUTH_TOKEN]
            if _SESSION_ID in entry[_SECRETS]:
                del entry[_SECRETS][_SESSION_ID]

        result_entries = other_entries + match_entries + non_match_entries

        credstore[_CREDSTORE][_ITEMS] = result_entries
        locked_fd.seek(0)
        locked_fd.truncate()
        locked_fd.write(json.dumps(credstore, indent=4) + '\n')

    @lock_file
    def list(self, server=None, formatter=None, locked_fd=None, fp=sys.stdout):
        """
        List credential store entries from credstore file

        :type   formatter: :class:`str`
        :param  formatter: Output formatter
        :type   locked_fd: :class:`file`
        :param  locked_fd: file object representing credentials store file content.
            Automatically passed through @lock_file decorator

        :rtype:  :class:`StatusCode`
        :return: Status code
        """
        credstore = {}
        # Open and share lock credstore file
        try:
            credstore = json.load(locked_fd)
        except ValueError as e:
            error_msg = 'Invalid credstore file %s' % self.credstore_path
            handle_error(error_msg, exception=e)
            return StatusCode.INVALID_ENV

        from vmware.vapi.data.value import (StringValue, StructValue, ListValue)

        entries = credstore[_CREDSTORE].get(_ITEMS, [])
        entries = [entry for entry in entries if entry[_TYPE] == _VAPI_CREDS_TYPE]

        if server is not None:
            entries = [entry for entry in entries if entry[_SERVER] == server]

        # create a data value object so that dcli can output result
        list_val = ListValue()
        for entry in entries:
            struct_val = StructValue('credstore')
            for key, value in six.iteritems(entry):
                if key == 'secrets':
                    continue
                struct_val.set_field(key, StringValue(value))
            list_val.add(struct_val)

        if formatter is None:
            formatter = Formatter('table', fp)
        formatter.format_output(list_val)
        return StatusCode.SUCCESS

    @lock_file
    def get_vapi_credstore_item(self, server, session_mgr, user, locked_fd=None):  # pylint: disable=R0201
        """
        Get credstore entry for a specific user/server/session manager in credstore file

        :type   server: :class:`str`
        :param  server: vAPI server URL
        :type   session_mgr: :class:`str`
        :param  session_mgr: Session manager
        :type   user: :class:`str`
        :param  user: User name
        :type   locked_fd: :class:`file`
        :param  locked_fd: file object representing credentials store file content.
            Automatically passed through @lock_file decorator

        :rtype:  :class:`dict` of :class:`str`
        :return: Credstore entry
        """
        credstore = {}
        try:
            # open json file in read mode and create a struct value of server/user and session mgr values
            credstore = json.load(locked_fd)
        except ValueError:
            return None

        vapi_entries = credstore[_CREDSTORE].get(_ITEMS, [])
        vapi_entries = [entry for entry in vapi_entries if entry[_TYPE] == _VAPI_CREDS_TYPE]
        result_entries = [entry for entry in vapi_entries
                          if entry.get(_SERVER) == server and entry.get(_SESSION_MGR) == session_mgr]

        result_entry = None

        if user:
            user_entries = [entry for entry in result_entries if entry.get(_USER) == user]
            if user_entries:
                result_entry = user_entries[0]
                if _PASSWORD in result_entry[_SECRETS] and result_entry[_SECRETS][_PASSWORD]:
                    result_entry[_SECRETS][_PASSWORD] = decrypt(user_entries[0].get(_SECRETS).get(_PASSWORD), server + user + session_mgr)
        else:
            if len(result_entries) == 1:  # If there's only one user return the password
                result_entry = result_entries[0]
                if _PASSWORD in result_entry[_SECRETS] and result_entry[_SECRETS][_PASSWORD]:
                    result_entry[_SECRETS][_PASSWORD] = decrypt(result_entries[0].get(_SECRETS).get(_PASSWORD), server + result_entries[0].get(_USER) + session_mgr)
        return result_entry

    @lock_file
    def get_vapi_credstore_items(self, server, locked_fd=None):  # pylint: disable=R0201
        """
        Get credstore entries for a specified server in credstore file

        :type   server: :class:`str`
        :param  server: vAPI server URL
        :type   locked_fd: :class:`file`
        :param  locked_fd: file object representing credentials store file content.
            Automatically passed through @lock_file decorator

        :rtype:  :class:`list`
        :return: Credstore entries
        """
        credstore = {}
        try:
            # open json file in read mode and create a struct value of server/user and session mgr values
            credstore = json.load(locked_fd)
        except ValueError:
            return None

        vapi_entries = credstore[_CREDSTORE].get(_ITEMS, [])
        vapi_entries = [entry for entry in vapi_entries if entry[_TYPE] == _VAPI_CREDS_TYPE]
        result_entries = [entry for entry in vapi_entries
                          if entry.get(_SERVER) == server]

        for entry in result_entries:
            if _PASSWORD in entry[_SECRETS] and entry[_SECRETS][_PASSWORD]:
                entry[_SECRETS][_PASSWORD] = decrypt(entry.get(_SECRETS).get(_PASSWORD), server + entry.get(_USER) + entry.get(_SESSION_MGR))

        return result_entries


class CSPCredentialsStore(CredentialsStore):
    """
    Handles credentials store logic for CSP credentials
    """

    def __init__(self, credstore_path):
        CredentialsStore.__init__(self, credstore_path)

    @lock_file
    def add(self, vmc_address, refresh_token, org_id, user, auth_token=None, session_id=None, locked_fd=None):
        """
        Add a CSP credential store entry to credstore file

        :type   vmc_address: :class:`str`
        :param  vmc_address: VMC URL
        :type   refresh_token: :class:`str`
        :param  refresh_token: Plain text refresh token to be stored
        :type   org_id: :class:`str`
        :param  org_id: Organisation id to store information for
        :type   user: :class:`str`
        :param  user: User name to store information for
        :type   auth_token: :class:`str`
        :param  auth_token: Authentication token to be stored
        :type   session_id: :class:`str`
        :param  session_id: Session id to be stored
        :type   locked_fd: :class:`file`
        :param  locked_fd: file object representing credentials store file content.
            Automatically passed through @lock_file decorator

        :rtype:  :class:`StatusCode`
        :return: Status code
        """
        if refresh_token:
            encrypted_refresh_token = encrypt(refresh_token, vmc_address + user)
            if six.PY3:
                encrypted_refresh_token = encrypted_refresh_token.decode()
            del refresh_token
        else:
            encrypted_refresh_token = None

        found = False

        credstore = None
        entries = []

        try:
            credstore = json.load(locked_fd)
        except ValueError:
            # Likely empty credstore file, ignore error and move on
            credstore = None

        if credstore:
            entries = credstore[_CREDSTORE].get(_ITEMS, [])
            for entry in entries:
                json_vmc_address = entry.get(_VMC_ADDRESS)
                json_user = entry.get(_USER)
                json_org_id = entry.get(_ORG_ID)

                if json_vmc_address == vmc_address and json_user == user and json_org_id == org_id:
                    # update the password
                    entry[_SECRETS][_REFRESH_TOKEN] = encrypted_refresh_token if encrypted_refresh_token is not None else ''
                    if auth_token:
                        entry[_SECRETS][_AUTH_TOKEN] = auth_token
                    if session_id:
                        entry[_SECRETS][_SESSION_ID] = session_id
                    found = True
                    break

        if not found:
            # create new credstore entry
            new_entry = {}
            new_entry[_TYPE] = _CSP_CREDS_TYPE
            new_entry[_VMC_ADDRESS] = vmc_address
            new_entry[_ORG_ID] = org_id
            new_entry[_USER] = user if user is not None else ''
            new_entry[_SECRETS] = {}
            new_entry[_SECRETS][_REFRESH_TOKEN] = encrypted_refresh_token if encrypted_refresh_token is not None else ''
            if auth_token:
                new_entry[_SECRETS][_AUTH_TOKEN] = auth_token
            if session_id:
                new_entry[_SECRETS][_SESSION_ID] = session_id
            entries.append(new_entry)

        if credstore is None:
            credstore = {_CREDSTORE: {_VERSION: self._SUPPORTED_VERSION}}
        if _ITEMS not in credstore:
            credstore[_CREDSTORE][_ITEMS] = []

        credstore[_CREDSTORE][_ITEMS] = entries
        locked_fd.seek(0)
        locked_fd.truncate()
        locked_fd.write(json.dumps(credstore, indent=4) + '\n')
        return StatusCode.SUCCESS

    @lock_file
    def remove(self, vmc_address, user=None, locked_fd=None):
        """
        Remove a CSP credential store entry from credstore file

        :type   vmc_address: :class:`str`
        :param  vmc_address: VMC URL
        :type   user: :class:`str`
        :param  user: User name
        :type   locked_fd: :class:`file`
        :param  locked_fd: file object representing credentials store file content.
            Automatically passed through @lock_file decorator

        :rtype:  :class:`StatusCode`
        :return: Status code
        """
        credstore = {}
        try:
            credstore = json.load(locked_fd)
        except ValueError:
            error_msg = 'Invalid credstore file %s' % self.credstore_path
            handle_error(error_msg)
            return StatusCode.INVALID_ENV

        entries = credstore[_CREDSTORE].get(_ITEMS, [])
        csp_entries = [entry for entry in entries if entry[_TYPE] == _CSP_CREDS_TYPE]
        other_entries = [entry for entry in entries if entry[_TYPE] != _CSP_CREDS_TYPE]

        entry_match = []
        non_match_entries = []
        for entry in csp_entries:
            if user and entry.get(_VMC_ADDRESS) == vmc_address and user == entry[_USER] \
                    or not user and entry.get(_VMC_ADDRESS) == vmc_address:
                entry_match.append(entry)
            else:
                non_match_entries.append(entry)

        if not entry_match:
            err_msg = "Couldn't find credstore entry for VMC address {}.".format(vmc_address)
            handle_error(err_msg)
            return StatusCode.INVALID_COMMAND

        if len(entry_match) > 1:
            msg = ('Found more than one credstore entry for VMC address {}. '
                   'Deleting them all').format(vmc_address)
            logger.info(msg)

        credstore[_CREDSTORE][_ITEMS] = non_match_entries + other_entries
        locked_fd.seek(0)
        locked_fd.truncate()
        locked_fd.write(json.dumps(credstore, indent=4) + '\n')
        return StatusCode.SUCCESS

    @lock_file
    def remove_auth_tokens(self, vmc_address=None, user=None, locked_fd=None):
        """
        Removes auth tokens in credentials store for specified one or none of
        vmc_address and user

        :type   vmc_address: :class:`str`
        :param  vmc_address: vmc address
        :type   user: :class:`str`
        :param  user: user name
        :type   locked_fd: :class:`file`
        :param  locked_fd: file object representing credentials store file content.
            Automatically passed through @lock_file decorator
        """
        credstore = {}
        try:
            credstore = json.load(locked_fd)
        except ValueError:
            error_msg = 'Invalid credstore file %s' % self.credstore_path
            handle_error(error_msg)
            return
        entries = credstore[_CREDSTORE].get(_ITEMS, [])
        vapi_entries = [entry for entry in entries if entry[_TYPE] == _CSP_CREDS_TYPE]
        other_entries = [entry for entry in entries if entry[_TYPE] != _CSP_CREDS_TYPE]

        non_match_entries = []
        match_entries = []
        if not vmc_address:
            match_entries = vapi_entries
        else:
            if user is None:
                for entry in vapi_entries:
                    if entry.get(_VMC_ADDRESS) == vmc_address:
                        match_entries.append(entry)
                    else:
                        non_match_entries.append(entry)
            else:
                for entry in vapi_entries:
                    if entry.get(_VMC_ADDRESS) == vmc_address \
                            and entry.get(_USER) == user:
                        match_entries.append(entry)
                    else:
                        non_match_entries.append(entry)

        for entry in match_entries:
            if _AUTH_TOKEN in entry[_SECRETS]:
                del entry[_SECRETS][_AUTH_TOKEN]
            if _SESSION_ID in entry[_SECRETS]:
                del entry[_SECRETS][_SESSION_ID]

        result_entries = other_entries + match_entries + non_match_entries

        credstore[_CREDSTORE][_ITEMS] = result_entries
        locked_fd.seek(0)
        locked_fd.truncate()
        locked_fd.write(json.dumps(credstore, indent=4) + '\n')

    @lock_file
    def list(self, formatter=None, locked_fd=None, fp=sys.stdout):
        """
        List credential store entries from credstore file

        :type   formatter: :class:`str`
        :param  formatter: Output formatter
        :type   locked_fd: :class:`file`
        :param  locked_fd: file object representing credentials store file content.
            Automatically passed through @lock_file decorator

        :rtype:  :class:`StatusCode`
        :return: Status code
        """
        credstore = {}
        # Open and share lock credstore file
        try:
            credstore = json.load(locked_fd)
        except ValueError as e:
            error_msg = 'Invalid credstore file %s' % self.credstore_path
            handle_error(error_msg, exception=e)
            return StatusCode.INVALID_ENV

        from vmware.vapi.data.value import (StringValue, StructValue, ListValue)

        entries = credstore[_CREDSTORE].get(_ITEMS, [])
        entries = [entry for entry in entries if entry[_TYPE] == _CSP_CREDS_TYPE]

        # create a data value object so that dcli can output result
        list_val = ListValue()
        for entry in entries:
            struct_val = StructValue('credstore')
            for key, value in six.iteritems(entry):
                if key == 'secrets':
                    continue
                struct_val.set_field(key, StringValue(value))
            list_val.add(struct_val)

        if formatter is None:
            formatter = Formatter('table', fp)
        formatter.format_output(list_val)
        return StatusCode.SUCCESS

    @lock_file
    def get_csp_credstore_item(self, vmc_address, org_id=None, user=None, locked_fd=None):  # pylint: disable=R0201
        """
        Get username and password tuple for a specific user/server/session manager
        entry in credstore file

        :type   server: :class:`str`
        :param  server: vAPI server URL
        :type   session_mgr: :class:`str`
        :param  session_mgr: Session manager
        :type   user: :class:`str`
        :param  user: User name
        :type   locked_fd: :class:`file`
        :param  locked_fd: file object representing credentials store file content.
            Automatically passed through @lock_file decorator

        :rtype:  :class:`str`
        :return: Username
        :rtype:  :class:`str`
        :return: Password
        """
        credstore = {}
        try:
            # open json file in read mode and create a struct value of server/user and session mgr values
            credstore = json.load(locked_fd)
        except ValueError:
            return None, None

        csp_entries = credstore[_CREDSTORE].get(_ITEMS, [])
        csp_entries = [entry for entry in csp_entries if entry[_TYPE] == _CSP_CREDS_TYPE]
        result_entries = [entry for entry in csp_entries
                          if entry.get(_VMC_ADDRESS) == vmc_address]

        if org_id:
            result_entries = [entry for entry in result_entries
                              if entry.get(_ORG_ID) == org_id]

        if user:
            result_entries = [entry for entry in result_entries
                              if entry.get(_USER) == user]

        result_entry = None
        if len(result_entries) >= 1:
            if len(result_entries) == 1:
                msg = "Getting refresh token from credentials store for organization id: %s"
            else:
                msg = ("Getting first available refresh token in credentials store. "
                       "It is for organization with id: %s")
            logger.info(msg, result_entries[0].get(_ORG_ID))
            result_entry = result_entries[0]
            result_entry[_SECRETS][_REFRESH_TOKEN] = decrypt(result_entry.get(_SECRETS).get(_REFRESH_TOKEN),
                                                             vmc_address + result_entry.get(_USER))
        return result_entry
