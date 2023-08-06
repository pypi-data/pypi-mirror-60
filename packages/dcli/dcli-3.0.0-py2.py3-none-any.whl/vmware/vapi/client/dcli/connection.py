"""
CLI connection specific classes and functions
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2018-2020 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import json
import logging
import sys
import uuid
import six
import requests

from com.vmware.vapi.std.errors_client import NotFound
from vmware.vapi.client.dcli.__version__ import __version__ as dcli_version
from vmware.vapi.client.dcli.__version__ import __vapi_runtime_version__ as vapi_version
from vmware.vapi.client.dcli.command import CliCommand
from vmware.vapi.client.dcli.credstore import (
    VapiCredentialsStore, CSPCredentialsStore
)
from vmware.vapi.client.dcli.exceptions import (
    handle_error, extract_error_msg, handle_server_error,
    IntrospectionOperationNotFound, CompletionAuthentication,
    AuthenticationException)
from vmware.vapi.client.dcli.internal_commands.options import Options
from vmware.vapi.client.dcli.metadata.file_metadata_provider import \
    FileMetadataProvider
from vmware.vapi.client.dcli.metadata.service_metadata_provider import \
    ServiceMetadataProvider
from vmware.vapi.client.dcli.namespace import CliNamespace
from vmware.vapi.client.dcli.options import CliOptions
from vmware.vapi.client.dcli.util import (
    StatusCode, calculate_time, SecurityContextManager,
    ServerTypes, get_csp_encoded_tokens, DcliContext,
    prompt_for_credentials, print_top_level_help,
    show_default_options_warning, get_decoded_JWT_token)
from vmware.vapi.core import MethodResult
from vmware.vapi.data.value import StructValue, SecretValue, StringValue
from vmware.vapi.client.lib.formatter import Formatter
from vmware.vapi.core import ApplicationContext
from vmware.vapi.data.serializers.cleanjson import DataValueConverter
from vmware.vapi.lib import connect
from vmware.vapi.lib.constants import (OPID, SHOW_UNRELEASED_APIS)
from vmware.vapi.protocol.client.msg.user_agent_util import init_product_info
from vmware.vapi.security.oauth import create_oauth_security_context
from vmware.vapi.security.session import create_session_security_context
from vmware.vapi.security.sso import (create_saml_bearer_security_context,
                                      SAML_BEARER_SCHEME_ID)
from vmware.vapi.security.user_password import (
    create_user_password_security_context, USER_PASSWORD_SCHEME_ID)

USER_PASS_RETRY_LIMIT = 1

NO_AUTHN_SCHEME = 'com.vmware.vapi.std.security.no_authentication'
SERVER_UNAUTHENTICATED_ERROR = 'com.vmware.vapi.std.errors.unauthenticated'
SERVER_UNAUTHORIZED_ERROR = 'com.vmware.vapi.std.errors.unauthorized'
logger = logging.getLogger(__name__)


class CliConnection(object):  # pylint: disable=R0902
    """
    Class to manage operations related to namespace related commands.
    """
    def __init__(self,
                 server,
                 server_type,
                 org_id=None,
                 sddc_id=None,
                 username=None,
                 password=None,
                 logout=None,
                 skip_server_verification=False,
                 cacert_file=None,
                 credstore_file=None,
                 credstore_add=None,
                 configuration_file=None,
                 show_unreleased_apis=None,
                 use_metamodel_metadata_only=None,
                 more=None,
                 formatter=None,
                 interactive=False):
        self.server = CliConnection.get_dcli_server(server, server_type)
        self.server_type = server_type
        self.org_id = org_id
        self.sddc_id = sddc_id
        self.username = username
        self.password = password
        self.logout = logout
        self.skip_server_verification = skip_server_verification
        self.cacert_file = cacert_file
        self.credstore_file = credstore_file
        self.credstore_add = credstore_add
        self.configuration_file = configuration_file
        self.show_unreleased_apis = show_unreleased_apis
        self.use_metamodel_metadata_only = use_metamodel_metadata_only
        self.more = more
        self.interactive = interactive
        self.formatter = formatter

        self.is_gov_cloud = None
        self.requests_session = None
        self.needs_pre_auth = False
        self.session_id = None
        self.auth_token = None
        self.csp_tokens = None
        self.session_manager = ''
        self.connector = None
        self.auth_connector = None
        self.metadata_provider = None
        self.default_options = None
        self.namespaces = None
        self.namespaces_names = None
        self.commands = None
        self.commands_names = None
        self.dcli_context = None
        self.cli_cmd_instance = None
        self.cli_namespace_instance = None
        self.vapi_credentials_store = None
        self.csp_credentials_store = None

        # set User-Agent information
        user_agent_product_comment = 'i' if self.interactive else None
        init_product_info('DCLI', dcli_version, product_comment=user_agent_product_comment, vapi_version=vapi_version)

        context = self.get_dcli_context()
        try:
            self.default_options = Options(context)
        except ValueError:
            show_default_options_warning(context.configuration_path)

        try:
            self.requests_session = requests.Session()
            self.set_certificates_validation()

            self.vapi_credentials_store = VapiCredentialsStore(self.credstore_file)
            self.csp_credentials_store = CSPCredentialsStore(self.credstore_file)

            if self.server_type in (ServerTypes.NSX,
                                    ServerTypes.VMC):
                self.connector = connect.get_requests_connector(self.requests_session,
                                                                url=self.server,
                                                                msg_protocol='rest')

                self.metadata_provider = \
                    FileMetadataProvider(self.server_type,
                                         self.server,
                                         self.requests_session,
                                         token=self.get_csp_token()[0])
            elif self.server_type == ServerTypes.NSX_ONPREM:
                auth_scheme = USER_PASSWORD_SCHEME_ID
                sec_ctx = self.get_security_context(auth_scheme)

                self.connector = connect.get_requests_connector(self.requests_session,
                                                                url=self.server,
                                                                msg_protocol='rest')

                self.metadata_provider = \
                    FileMetadataProvider(self.server_type,
                                         self.server,
                                         self.requests_session,
                                         creds={'username': sec_ctx['userName'],
                                                'password': sec_ctx['password']})

                if self.credstore_add:
                    self.add_entry_to_credstore(sec_ctx['userName'], sec_ctx['password'])
            elif self.server_type == ServerTypes.VSPHERE:
                self.connector = connect.get_requests_connector(self.requests_session,
                                                                url=self.server)
                self.metadata_provider = ServiceMetadataProvider(self.connector,
                                                                 use_metamodel_only=self.use_metamodel_metadata_only)
            elif self.server_type == ServerTypes.Internal:
                self.metadata_provider = FileMetadataProvider(server_type='internal')
            else:
                self.metadata_provider = None

            if self.server_type == ServerTypes.NSX:
                self.auth_connector = connect.get_requests_connector(self.requests_session,
                                                                     url=CliOptions.DCLI_VMC_SERVER,
                                                                     msg_protocol='rest')
            else:
                self.auth_connector = self.connector

            self.set_application_context()
        except Exception as e:
            error_msg = 'Unable to connect to the server.'
            msg = extract_error_msg(e)
            if msg:
                logger.error('Error: %s', msg)
            logger.exception(e)
            raise Exception(error_msg)

    def set_application_context(self):
        """
        Sets application context for connection's connector
        That is operation id and whether to show unreleased apis
        """
        op_id = str(uuid.uuid4())
        if self.show_unreleased_apis:
            app_ctx = ApplicationContext({OPID: op_id, SHOW_UNRELEASED_APIS: "True"})
        else:
            app_ctx = ApplicationContext({OPID: op_id})
        if self.connector:
            self.connector.set_application_context(app_ctx)
        if self.auth_connector:
            self.auth_connector.set_application_context(app_ctx)

    @staticmethod
    def get_dcli_server(server=None, server_type=None):
        """ Get dcli server """
        from six.moves import urllib
        base_url = 'api'
        if server_type in (ServerTypes.NSX, ServerTypes.NSX_ONPREM, ServerTypes.VMC):
            base_url = ''

        result = server

        if not server:
            result = 'http://localhost/%s' % base_url  # Default server url
        else:
            if server.startswith('http'):
                url = urllib.parse.urlparse(server)
                if not url.scheme or not url.netloc:
                    logger.error('Invalid server url %s. URL must be of format http(s)://ip:port', server)
                    raise Exception('Invalid server url %s. URL must be of format http(s)://ip:port' % server)

                if not url.path or url.path == '/':
                    # If only ip and port are provided append /api
                    result = '%s://%s/%s' % (url.scheme, url.netloc, base_url)
                else:
                    result = server
            else:
                if server_type == ServerTypes.VMC:
                    result = 'http://%s/%s' % (server, base_url)
                else:
                    result = 'https://%s/%s' % (server, base_url)

        if result.endswith('/'):
            result = result[0:len(result) - 1]

        return result

    def get_dcli_context(self):
        """
        Returns dcli context object
        @return: :class:`vmware.vapi.client.dcli.util.DcliContext`
        """
        if self.dcli_context is None:
            self.dcli_context = DcliContext(
                configuration_path=self.configuration_file,
                server=self.server,
                server_type=self.server_type)
        return self.dcli_context

    def set_certificates_validation(self):
        """
        Sets certificates validation options to requests session according to
        users input
        """
        if self.cacert_file:
            self.requests_session.verify = self.cacert_file
        elif self.skip_server_verification:
            self.requests_session.verify = False
        else:
            certs_path = CliOptions.DCLI_CACERTS_BUNDLE
            self.requests_session.verify = certs_path

    def handle_user_and_password_input(self):
        """
        Method to prompt user to enter username, password and
        ask if they want to save credentials in credstore

        :rtype:  :class:`str`, :class:`str`
        :return: username, password
        """
        if self.needs_pre_auth:
            completion_exception = CompletionAuthentication("You need to be already authenticated to autocomplete this command")
            raise completion_exception

        org_id = CliConnection.get_org_id()
        if org_id and org_id in self.csp_tokens:
            if 'default' in self.csp_tokens \
                    and self.csp_tokens['default'] == self.csp_tokens[org_id]:
                del self.csp_tokens['default']
            del self.csp_tokens[org_id]
        self.session_id = None
        self.auth_token = None

        username, password, should_save = prompt_for_credentials(self.server_type,
                                                                 username=self.username,
                                                                 credstore_add=self.credstore_add,
                                                                 org_id=org_id)

        if self.server_type in (ServerTypes.NSX, ServerTypes.VMC):
            # we just need value different than None or empty string in this case
            username = 'dummy'

        if not self.credstore_add:
            self.credstore_add = should_save

        return username, password

    def get_csp_token(self, force=False):
        """
        Retrieve csp token based on org id provided on current command

        :rtype:  :class:`str`
        :return: CSP token
        """
        if self.csp_tokens is None:
            self.csp_tokens = {}

        org_id = CliConnection.get_org_id()
        key = org_id
        if not org_id:
            key = 'default'

        if force or key not in self.csp_tokens:
            tokens_info = self.retrieve_token(org_id=org_id)
            self.csp_tokens[key] = tokens_info['auth_token'], tokens_info['id_token']
            if key == 'default':
                decoded_auth_token = tokens_info["decoded_auth_token"]
                self.csp_tokens[decoded_auth_token["context_name"]] = tokens_info['auth_token'], tokens_info['id_token']

        return self.csp_tokens[key]

    def retrieve_token(self, org_id=None):
        """
        From provided org id retrieves authentication and identity access tokens
        by taking the appropriate refresh token from credentials store
        or prompting for one.

        :type  org_id: :class:`str`
        :param org_id: Organization id to take refresh token for
            (later on exchanged for auth and identity tokens);
            if None, retrieves refresh token from first found org idon credentials store or,
            if none found, prompts for refresh token

        :return: authentication access token for provided org_id, decoded authentication token,
            identity access token for provided org_id, decoded identity token
        :rtype: :class:`str`, :class:`str`, :class:`str`, :class:`str`
        """
        server_url = self.server

        if self.server_type == ServerTypes.NSX:
            if self.org_id is None:
                import re
                # searching for '/orgs/GUID' pattern in NSX URL
                match = re.search('orgs/([0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})', server_url)
                if match is not None:
                    org_id = match.group(1)
                else:
                    error_msg = ("Couldn't fetch organization id from provided NSX address. "
                                 "Are you sure you have provided correct NSX address?")
                    handle_error(error_msg)
                    raise Exception(error_msg)
            else:
                org_id = self.org_id
            server_url = CliOptions.DCLI_VMC_SERVER

        entry = self.csp_credentials_store.get_csp_credstore_item(server_url, org_id=org_id)
        should_save = False
        if not entry or 'refresh_token' not in entry['secrets']:
            _, refresh_token, should_save = prompt_for_credentials(self.server_type, org_id=org_id, is_gov_cloud=self.is_gov_cloud)
        else:
            refresh_token = entry['secrets']['refresh_token']

        auth_token, id_token = get_csp_encoded_tokens(self.requests_session, refresh_token)
        decoded_auth_token = get_decoded_JWT_token(encoded_token=auth_token, session=self.requests_session)
        decoded_id_token = get_decoded_JWT_token(encoded_token=id_token, session=self.requests_session)

        self.username = decoded_auth_token['username']
        self.password = refresh_token

        # Save credentials after we verify they are correct;
        # That is after we get authentication and identity tokens successfully
        if should_save:
            self.add_entry_to_credstore(None, refresh_token, auth_token=auth_token)

        return {
            'auth_token': auth_token,
            'decoded_auth_token': decoded_auth_token,
            'id_token': id_token,
            'decoded_id_token': decoded_id_token
        }

    @staticmethod
    def get_org_id():
        """
        From current entered command returns org id if provided
        Otherwise None is returned

        :rtype:  :class:`str`
        :return: Org id found in the current command
        """
        current_cmd = None
        if '__main__' in sys.modules \
                and hasattr(sys.modules['__main__'], 'cli_main'):
            current_cmd = sys.modules['__main__'].cli_main.current_dcli_command
        elif 'vmware.vapi.client.dcli.cli' in sys.modules:
            current_cmd = sys.modules['vmware.vapi.client.dcli.cli'].cli_main.current_dcli_command
        else:
            logger.info("Module cli which contains CliMain was not found")

        if current_cmd is None:
            return None

        import re
        # searching for '--org GUID' pattern in current command
        match = re.search(r'--org\s([0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})', current_cmd)
        if match is not None:
            return match.group(1)
        return None

    def exchange_auth_token_for_saml_token(self, auth_token, identity_token):
        """
        Exchanges authentication token (together with identity token) for SAML token
        by using VMware's token exchange service

        :type  auth_token: :class:`str`
        :param auth_token: Authentication token
        :type  identity_token: :class:`str`
        :param identity_token: Identity token

        :rtype:  :class:`str`
        :return: SAML token
        """
        if self.cli_cmd_instance is None:
            error_msg = 'Command instance object is None when value was expected'
            handle_error(error_msg)
            raise Exception(error_msg)

        sec_ctx = create_oauth_security_context(auth_token)

        with SecurityContextManager(self.cli_cmd_instance.connector, sec_ctx):
            saml_token_output = \
                self.cli_cmd_instance.call_another_command('com.vmware.vcenter.tokenservice.token_exchange',
                                                           'exchange',
                                                           ['--subject-token-type', 'urn:ietf:params:oauth:token-type:access_token',
                                                            '--subject-token', auth_token,
                                                            '--actor-token-type', 'urn:ietf:params:oauth:token-type:id_token',
                                                            '--actor-token', identity_token,
                                                            '--requested-token-type', 'urn:ietf:params:oauth:token-type:saml2',
                                                            '--grant-type', 'urn:ietf:params:oauth:token-type:saml2'])

        if not saml_token_output:
            error_msg = 'An error occured while trying to exchange auth token for SAML token'
            handle_error(error_msg)
            raise Exception(error_msg)

        encoded_saml_token = saml_token_output.get_field('access_token').value

        import base64
        if six.PY2:
            return base64.decodestring(encoded_saml_token)  # pylint: disable=W1505
        else:
            if not isinstance(encoded_saml_token, bytes):
                encoded_saml_token = bytes(encoded_saml_token, encoding='utf-8')
            return base64.decodebytes(encoded_saml_token).decode()

    def get_security_context(self, auth_scheme):
        """
        Method to get security context

        :type  auth_scheme: :class:`str`
        :param auth_scheme: Authentication scheme to get security context based on

        :rtype:  :class:`vmware.vapi.core.SecurityContext`
        :return: Security context
        """
        user = self.username
        pwd = self.password
        sec_ctx = None

        if self.server_type in (ServerTypes.VMC, ServerTypes.NSX):
            server = CliOptions.DCLI_VMC_SERVER
        else:
            server = self.server

        if pwd is False:
            # No credentials provided on command line; check credstore
            user, pwd = self.get_credentials_from_credentials_store(server, user, pwd)
        if self.is_gov_cloud:
            if self.session_id:
                return None

            auth_token, id_token = self.get_csp_token()
            saml_token = self.exchange_auth_token_for_saml_token(auth_token, id_token)
            sec_ctx = create_saml_bearer_security_context(saml_token)
        elif auth_scheme == USER_PASSWORD_SCHEME_ID:
            if self.server_type in (ServerTypes.VMC, ServerTypes.NSX):
                token = None
                store_token = False
                if not self.interactive:
                    org_id = CliConnection.get_org_id()
                    entry = self.csp_credentials_store.get_csp_credstore_item(server, org_id=org_id)
                    if entry:
                        self.username = entry['user']
                        if 'auth_token' in entry['secrets']:
                            token = entry['secrets']['auth_token']
                        else:
                            store_token = True
                if not token:
                    token = self.get_csp_token()[0]
                if store_token:
                    self.add_entry_to_credstore(None, entry['secrets']['refresh_token'], auth_token=token)
                sec_ctx = create_oauth_security_context(token)
            else:
                # In case user, pwd weren't provided then prompt for both
                if not user:
                    self.username, self.password = self.handle_user_and_password_input()
                    return self.get_security_context(auth_scheme)
                else:
                    self.username = user
                    self.password = pwd
                sec_ctx = create_user_password_security_context(user, pwd)
        elif auth_scheme == SAML_BEARER_SCHEME_ID:  # pylint: disable=too-many-nested-blocks
            token = CliOptions.DCLI_SSO_BEARER_TOKEN

            if not token:
                # Check if user passed STS URL environment variable
                sts_url = CliOptions.STS_URL
                try:
                    try:
                        from vmware.vapi.client.lib import sso
                    except ImportError as e:
                        handle_error('Unable to import SSO libraries', exception=e)
                        sys.exit(StatusCode.INVALID_ENV)

                    auth = sso.SsoAuthenticator(sts_url)

                    # TODO: refactor this authentication code
                    if sts_url:
                        logger.info('Getting SAML bearer token')
                        if not user:
                            self.username, self.password = self.handle_user_and_password_input()

                        token = auth.get_bearer_saml_assertion(self.username,
                                                               self.password,
                                                               delegatable=True)
                    else:
                        # try passthrough authentication
                        logger.info('Using passthrough authentication')
                        token = auth.get_bearer_saml_assertion_gss_api(delegatable=True)
                except Exception as e:
                    msg = extract_error_msg(e)
                    handle_error('Unable to get SAML token for the user. %s' % msg, exception=e)
                    return StatusCode.NOT_AUTHENTICATED
            sec_ctx = create_saml_bearer_security_context(token)

        return sec_ctx

    def get_credentials_from_credentials_store(self, server, user, pwd):
        """
        Get credentials from credentials store. If none found return passed user and password.

        :type  server: :class:`str`
        :param server: Server address
        :type  user: :class:`str`
        :param user: Username
        :type  pwd: :class:`str`
        :param pwd: Password

        :rtype:  :class:`tuple` of :class:`str` and :class:`str`
        :return: user and password credentials taken from credentials store.
        """
        if self.is_gov_cloud:
            logger.info('Trying to read credstore for login GovCloud credentials')
            entry = self.csp_credentials_store.get_csp_credstore_item(server)
            self.username = entry['user'] if entry else None
            if entry and 'refresh_token' in entry['secrets']:
                self.password = entry['secrets']['refresh_token']
            else:
                self.password = None
            if entry and 'session_id' in entry['secrets']:
                self.session_id = entry['secrets']['session_id']
            elif entry and 'auth_token' in entry['secrets']:
                self.auth_token = entry['secrets']['auth_token']
            else:
                self.session_id = None
                self.auth_token = None
        elif self.server_type in (ServerTypes.VSPHERE, ServerTypes.NSX_ONPREM):
            logger.info('Trying to read credstore for login credentials')
            entry = self.vapi_credentials_store.get_vapi_credstore_item(server,
                                                                        self.session_manager,
                                                                        user)
            user = entry['user'] if entry else None
            pwd = entry['secrets']['password'] if entry else None
        return user, pwd

    def authenticate_command(self, service, operation):  # pylint: disable=R0915
        """
        Method to authenticate vAPI command

        :type  service: :class:`str`
        :param service: vAPI service
        :type  operation: :class:`str`
        :param operation: vAPI operation

        :rtype:  :class:`StatusCode`
        :return: Return code of the authentication and whether it is session aware or sessionless
        """
        is_session_aware = False
        curr_auth_scheme = None
        authn_retval = StatusCode.SUCCESS
        auth_schemes = calculate_time(
            lambda: self.metadata_provider.get_authentication_schemes(
                service,
                operation),
            'get authentication schemes time')

        if not auth_schemes:
            return authn_retval, None, None

        sec_ctx = None
        # If authentication is required check if login credentials (username and password) were provided on the command line
        # If login credentials were provided by the user try to use them to execute the command
        # If login credentials were not provided check if the credstore has credentials for the server and session manager
        # If credstore has credentials for the provided server and session manager use them to execute the command
        # If no credentials were present in credstore try to execute the command using passthrough login

        # get curr auth scheme here and get session manager
        if NO_AUTHN_SCHEME in auth_schemes:
            logger.info('Using no authentication scheme')
            return StatusCode.SUCCESS, None, None

        if self.server_type == ServerTypes.VSPHERE and self.is_gov_cloud is None:
            if self.cli_cmd_instance is None:
                error_msg = 'Command instance object is None when value was expected'
                handle_error(error_msg)
                return StatusCode.NOT_AUTHENTICATED, None, None

            try:
                identity_providers_output = \
                    self.cli_cmd_instance.call_another_command('com.vmware.vcenter.identity.providers',
                                                               'list',
                                                               [])
            except IntrospectionOperationNotFound as e:
                error_msg = e.msg
                error_msg += '{}; Thus conducting dcli is not executing against GovCloud instance'
                handle_error(error_msg, print_error=False, log_level='info')
                identity_providers_output = None

            if identity_providers_output:
                for item in identity_providers_output:
                    if item.has_field('oauth2'):
                        self.is_gov_cloud = True
                        break
            self.is_gov_cloud = False

        if USER_PASSWORD_SCHEME_ID in auth_schemes:
            logger.info('Using username/password authentication scheme')
            curr_auth_scheme = USER_PASSWORD_SCHEME_ID
        elif SAML_BEARER_SCHEME_ID in auth_schemes:
            logger.info('Using SAML bearer token authentication scheme')
            curr_auth_scheme = SAML_BEARER_SCHEME_ID
        else:
            handle_error('This command does not support login through username/password')
            return StatusCode.NOT_AUTHENTICATED, None, None

        # pick the first scheme be it session aware or session less
        is_session_aware = curr_auth_scheme and auth_schemes[curr_auth_scheme][0]

        if is_session_aware:
            self.session_manager = auth_schemes[curr_auth_scheme][0]

        user_pass_retry_count = 0
        # breaks when user/pass retry limit reached (for invalid creds) or at script block end(for valid creds)
        while True:  # pylint: disable=too-many-nested-blocks
            if not (is_session_aware and (self.session_id is not None or self.auth_token is not None)):
                sec_ctx = calculate_time(
                    lambda: self.get_security_context(curr_auth_scheme),
                    'get security context time')

            if sec_ctx == StatusCode.NOT_AUTHENTICATED:
                return sec_ctx, None, None

            if is_session_aware:
                user = self.username
                pwd = self.password
                self.password = False

                if not self.session_id and not self.interactive:
                    entry = self.get_entry_from_credentials_store(user)
                    if entry and 'session_id' in entry['secrets']:
                        self.session_id = entry['secrets']['session_id']
                    elif entry and 'auth_token' in entry['secrets']:
                        self.auth_token = entry['secrets']['session_id']

                if self.session_id:
                    sec_ctx = create_session_security_context(self.session_id)
                    break
                elif self.auth_token:
                    sec_ctx = create_oauth_security_context(self.auth_token)
                    break

                try:
                    with SecurityContextManager(self.auth_connector, sec_ctx):
                        logger.info('Doing session login to session manager')
                        authn_retval, result = calculate_time(
                            self.session_login,
                            'session login time')

                    if result and result.success():
                        if isinstance(result.output, StructValue) \
                                and result.output.has_field('access_token') \
                                and isinstance(result.output.get_field('access_token'), (SecretValue, StringValue)):
                            self.auth_token = result.output.get_field('access_token').value
                        elif isinstance(result.output, (SecretValue, StringValue)):
                            self.session_id = result.output.value
                        else:
                            error_msg = "Session login result can not be handled by dcli."
                            handle_error(error_msg)

                        # add credentials/session to credstore
                        # if flag is up or if user is already in credentials store
                        if self.credstore_add or self.user_in_credstore(user):
                            if self.session_id:
                                authn_retval = self.add_entry_to_credstore(user, pwd, session_id=self.session_id)
                            elif self.auth_token:
                                authn_retval = self.add_entry_to_credstore(user, pwd, auth_token=self.auth_token)

                    else:
                        self.username = None
                        raise Exception('Unable to authenticate')

                    # Execute subsequent calls using Session/Token Identifier
                    if self.session_id:
                        sec_ctx = create_session_security_context(self.session_id)
                    elif self.auth_token:
                        sec_ctx = create_oauth_security_context(self.auth_token)

                except Exception as e:
                    if user_pass_retry_count < USER_PASS_RETRY_LIMIT:
                        user_pass_retry_count += 1
                        msg = 'Unable to authenticate user. Please enter the credentials again.'
                        handle_error(msg, log_level='info')
                        continue
                    else:
                        error_str = 'Unable to authenticate user.'
                        if 'result' in locals() and result and result.error is not None:
                            handle_server_error(result.error)
                        else:
                            handle_error(error_str, exception=e)
                        return StatusCode.NOT_AUTHENTICATED, None, None

            break

        return authn_retval, is_session_aware, sec_ctx

    def get_entry_from_credentials_store(self, user):
        """
        Retrieve credentials store entry for specified user if already presented in credentials store.

        :type  user: :class:`str`
        :param user: user name

        :rtype: :class:`str`
        :return: session id
        """
        logger.info("Getting session id from credentials store")
        if self.is_gov_cloud:
            entry = self.csp_credentials_store.get_csp_credstore_item(self.server, user=user)
        else:
            entry = self.vapi_credentials_store.get_vapi_credstore_item(self.server,
                                                                        self.session_manager,
                                                                        user)

        if entry:
            return entry
        return None

    def get_token_from_credentials_store(self, user):
        """
        Retrieves session id for specified user if already presented in credentials store

        :type  user: :class:`str`
        :param user: user name

        :rtype: :class:`str`
        :return: session id
        """
        logger.info("Getting oauth token from credentials store")
        entry = self.vapi_credentials_store.get_vapi_credstore_item(self.server,
                                                                    self.session_manager,
                                                                    user)

        if entry and 'auth_token' in entry['secrets']:
            return entry['secrets']['auth_token']
        return None

    def user_in_credstore(self, user):
        """
        Verifies if certain username is already present in credentials store

        :type  user: :class:`str`
        :param user: user name

        :rtype: :class:`bool`
        :return: True if user presented in credentials store, False otherwise
        """
        if self.is_gov_cloud:
            credstore_item = self.csp_credentials_store.get_csp_credstore_item(self.server)
        else:
            credstore_item = self.vapi_credentials_store.get_vapi_credstore_item(self.server, self.session_manager, user)
        return True if credstore_item else False

    def add_entry_to_credstore(self, user, pwd, session_id=None, auth_token=None):
        """
        Adds given credentials entry to the credstore.

        :param user: username
        :param pwd: password
        :return: Status code of the operation
        """
        if self.server_type in (ServerTypes.VMC, ServerTypes.NSX):
            server = CliOptions.DCLI_VMC_SERVER
            logger.info("Adding credstore entry for provided refresh token and VMC")
            token = self.get_csp_token()[0] if not auth_token else auth_token
            decoded_token = get_decoded_JWT_token(encoded_token=token, session=self.requests_session)
            return self.csp_credentials_store.add(server,
                                                  pwd,
                                                  decoded_token['context_name'],
                                                  decoded_token['username'],
                                                  auth_token=auth_token)
        elif self.is_gov_cloud:
            server = self.server
            logger.info("Adding credstore entry for provided refresh token and VC instance")
            auth_token = self.get_csp_token()[0] if not auth_token else auth_token
            decoded_token = get_decoded_JWT_token(encoded_token=auth_token, session=self.requests_session)
            return self.csp_credentials_store.add(server,
                                                  pwd,
                                                  decoded_token['context_name'],
                                                  decoded_token['username'],
                                                  session_id=session_id)

        logger.info("Adding credstore entry for user '%s'", user)
        return self.vapi_credentials_store.add(self.server,
                                               user,
                                               pwd,
                                               self.session_manager,
                                               session_id=session_id,
                                               auth_token=auth_token)

    def clear_credentials_store_sessions(self):
        """
        Clear credentials store session or auth token information
        """
        if self.server_type in (ServerTypes.VMC, ServerTypes.NSX):
            self.csp_credentials_store.remove_auth_tokens(vmc_address=CliOptions.DCLI_VMC_SERVER)
        else:
            credstore_items = self.vapi_credentials_store.get_vapi_credstore_items(self.server)
            for item in credstore_items:
                self.session_manager = item["session_manager"]
                self.session_logout()
            self.vapi_credentials_store.remove_session_ids(server=self.server)

    def session_login(self):
        """
        Method to login to SessionManager
        """
        logger.info('Doing session login from session manager')
        return self.invoke_session_manager_method('create')

    def session_logout(self):
        """
        Method to logout from a SessionManager login session
        """
        logger.info('Doing session logout from session manager')
        self.invoke_session_manager_method('delete')
        self.session_manager = ''

    def invoke_session_manager_method(self, method_name):
        """
        Method to invoke session manger

        :type  method_name: :class:`str`
        :param method_name: Name of session manager method

        :rtype: :class:`StatusCode`
        :return: Error code
        :rtype: :class:`vmware.vapi.core.MethodResult`
        :return: Method result
        """
        if not self.session_manager:
            return StatusCode.NOT_AUTHENTICATED, None

        ctx = self.auth_connector.new_context()
        sec_ctx = ctx.security_context
        ctx.security_context = None

        # Check if login method exists
        try:
            input_definition = calculate_time(
                lambda: self.metadata_provider.get_command_input_definition(
                    self.session_manager,
                    method_name),
                'get auth command input definition')
        except NotFound as e:
            # XXX remove this code once everyone moves over to create/delete methods
            if method_name == 'create':
                return self.invoke_session_manager_method('login')
            elif method_name == 'delete':
                return self.invoke_session_manager_method('logout')
            elif method_name == 'logout':
                logger.warning("No logout or delete method found")
                return StatusCode.NOT_AUTHENTICATED, None
            # no login method
            handle_error('Invalid login session manager found', exception=e)
            return StatusCode.NOT_AUTHENTICATED, None

        api_provider = self.auth_connector.get_api_provider()

        ctx.security_context = sec_ctx

        # Method call
        logger.debug('Invoking vAPI operation')
        result = api_provider.invoke(self.session_manager,
                                     method_name,
                                     input_definition.new_value(),
                                     ctx)
        return StatusCode.SUCCESS, result

    def get_cmd_instance(self, path, name):
        """
        Method to get CLICommand instance

        :type  path: :class:`str`
        :param path: CLI namespace path
        :type  name: :class:`str`
        :param name: CLI command name

        :rtype: :class:`CliCommand`
        :return: CliCommand instance
        """
        if self.cli_cmd_instance is None or \
                self.cli_cmd_instance.path != path or \
                self.cli_cmd_instance.name != name:
            self.cli_cmd_instance = CliCommand(self,
                                               path,
                                               name)
        return self.cli_cmd_instance

    def get_namespace_instance(self, path, name):
        """
        Method to get CliNamespace instance

        :type  path: :class:`str`
        :param path: CLI namespace path
        :type  name: :class:`str`
        :param name: CLI namespace name

        :rtype: :class:`CliNamespace`
        :return: CliNamespace instance
        """
        if self.cli_namespace_instance is None or \
                self.cli_namespace_instance.path != path or \
                self.cli_namespace_instance.name != name:
            self.cli_namespace_instance = CliNamespace(self.metadata_provider, path, name)
        return self.cli_namespace_instance

    def execute_command(self,  # pylint: disable=dangerous-default-value
                        path,
                        name,
                        args_,
                        fp=sys.stdout,
                        cmd_filter=None,
                        generate_json_input=False,
                        generate_required_json_input=False,
                        json_input=None):
        """
        Main method to call and display result of a dcli command

        :type  path: :class:`str`
        :param path: CLI command path
        :type  name: :class:`str`
        :param name: CLI command name
        :type  args_: :class:`list` of :class:`str`
        :param args_: Command arguments
        :type  fp: :class:`File`
        :param fp: Output file stream
        :type  cmd_filter: :class:`str`
        :param cmd_filter: jmespath string value to filter command output
        :type  generate_json_input: :class:`bool`
        :param generate_json_input: specifies whether to output command's input as json object
        :type  generate_required_json_input: :class:`bool`
        :param generate_required_json_input: specifies whether to output command's input for required fields only as json object
        :type  json_input: :class:`obj`
        :param json_input: json input (converted to python object) to be used as command's input

        :rtype:  :class:`StatusCode`
        :return: Return code
        """
        cli_cmd_instance = self.get_cmd_instance(path, name)

        if cli_cmd_instance.is_a_command():
            if generate_json_input or generate_required_json_input:
                cmd_input = cli_cmd_instance.collect_command_input(args_,
                                                                   json_input=json_input,
                                                                   generate_json_input=True)
                input_dict, field_names = cli_cmd_instance.get_command_input_dict(cmd_input)
                result = MethodResult(
                    output=cli_cmd_instance.build_data_value(input_dict=input_dict,
                                                             field_names=field_names,
                                                             generate_json_input=True,
                                                             required_fields_only=generate_required_json_input))
                cli_cmd_instance.cmd_info.formatter = 'jsonp'

            try:
                if not (generate_json_input or generate_required_json_input):
                    result = self.call_command(cli_cmd_instance,
                                               args_,
                                               json_input=json_input,
                                               cmd_filter=cmd_filter)
            except AuthenticationException as e:
                return e.auth_result

            formatter = cli_cmd_instance.cmd_info.formatter if not self.formatter else self.formatter

            if self.interactive and not self.formatter \
                    and formatter in ['simple', 'xml', 'json', 'html']:
                # if formatter not set explicitly
                formatter += 'c'

            formatter_instance = Formatter(formatter, fp)
            result = calculate_time(lambda: cli_cmd_instance.display_result(result,
                                                                            formatter_instance,
                                                                            self.more),
                                    'display command output time')

            if not self.interactive:
                calculate_time(self.session_logout, 'session logout time')

            return result
        else:
            if not name and not path:
                if self.server:
                    error_msg = 'Unable to execute command from the server.\n'
                    error_msg += 'Is server correctly configured?'
                    handle_error(error_msg)
                else:
                    print_top_level_help(self.interactive, self.server_type)
            else:
                command_name = name if not path else '%s %s' % (path.replace('.', ' '), name)
                handle_error("Unknown command: '%s'" % command_name)
            return StatusCode.INVALID_COMMAND
        return StatusCode.INVALID_COMMAND

    def call_command(self, cli_cmd_instance, args_, json_input=None, cmd_filter=None):
        """
        Executes command by ensuring correct authentication as well.

        :type  cli_cmd_instance: :class:`CliCommand`
        :param cli_cmd_instance: cli command instance object
        :type  args_: :class:`obj`
        :param args_: json input (converted to python object) to be used as command's input
        :type  json_input: :class:`obj`
        :param json_input: json input (converted to python object) to be used as command's input
        :type  cmd_filter: :class:`str`
        :param cmd_filter: jmespath string value to filter command output

        :rtype:  :class:`MethodResult`
        :return: Return command result in data value format
        """
        cmd_info = cli_cmd_instance.cmd_info

        user_pass_retry_count = 0
        # breaks when user/pass retry limit reached (for invalid creds) or at script block end(for valid creds)
        while True:
            auth_result, is_session_aware, sec_ctx = calculate_time(
                lambda: self.authenticate_command(
                    cmd_info.service_id,
                    cmd_info.operation_id),
                'full authentication time')

            # clear credentials from memory fast
            # in case of not session aware operation keep them longer in order to verify correct authentication
            # and store valid credentials in credstore
            # we would need username in session aware operations as well
            # in order to search for it in credentials store
            user = self.username
            if not is_session_aware:
                password = self.password
            else:
                password = False
            self.username = None
            self.password = False

            if auth_result != StatusCode.SUCCESS:
                raise AuthenticationException("Command authentication was not successfull and an exception was thrown.",
                                              auth_result)

            with SecurityContextManager(self.connector, sec_ctx):
                ctx = self.connector.new_context()
                result = calculate_time(lambda:
                                        cli_cmd_instance.execute_command(
                                            ctx,
                                            args_,
                                            json_input=json_input),
                                        'command call to the server time')

            invalid_credentials = False
            if result.error:
                retry_cmd, invalid_credentials, user_pass_retry_count = \
                    self.handle_server_error_output(result.error,
                                                    is_session_aware,
                                                    user_pass_retry_count,
                                                    user)
                if retry_cmd:
                    continue
                break

            if cmd_filter is not None and result.success():
                # filter is list in order to deal with spaces
                # we need to merge it to a single string
                cmd_filter = ' '.join(cmd_filter)

                json_result = DataValueConverter.convert_to_json(result.output)
                try:
                    import jmespath
                    filtered_json_result = jmespath.search(cmd_filter, json.loads(json_result))
                    if filtered_json_result:
                        result._output = DataValueConverter.convert_to_data_value(json.dumps(filtered_json_result))  # pylint: disable=W0212
                    else:
                        result._output = None  # pylint: disable=W0212
                except ImportError:
                    error_msg = 'Unable to import jmespath module; filter functionality disabled!'
                    handle_error(error_msg, prefix_message="Warning: ")
                    result._output = result.output  # pylint: disable=W0212

            break

        if self.credstore_add and not is_session_aware and not invalid_credentials:
            self.add_entry_to_credstore(user, password)
            user = None
            password = False

        return result

    def handle_server_error_output(self, error, is_session_aware, user_pass_retry_count, user):
        """
        Handles server errors and returns boolean based on whether the command should
        be retired based on the error

        :type  error: :class:`vmware.vapi.data.value.ErrorValue`
        :param error: Server error returned
        :type  is_session_aware: :class:`bool`
        :param is_session_aware: is command executed, for which error is returned, session aware
        :type  user_pass_retry_count: :class:`int`
        :param user_pass_retry_count: number of retries done when error occured
        :type  user: :class:`str`
        :param user: user with which error occured

        :rtype:  :class:`bool`, :class:`bool`
        :return: If True command should be executed again, otherwise no,
                 Boolean value of whether credentials are invalid or not
        """
        invalid_credentials = False
        if hasattr(error, 'name') and \
                (error.name in (SERVER_UNAUTHENTICATED_ERROR,
                                SERVER_UNAUTHORIZED_ERROR)) and \
                not is_session_aware and \
                user_pass_retry_count < USER_PASS_RETRY_LIMIT and \
                self.server_type not in (ServerTypes.NSX, ServerTypes.VMC):
            user_pass_retry_count += 1
            msg = 'Unable to authenticate user. Please enter the credentials again.'
            handle_error(msg, log_level='info')
            invalid_credentials = True
            return True, invalid_credentials, user_pass_retry_count
        elif hasattr(error, 'name') \
                and error.name == SERVER_UNAUTHENTICATED_ERROR:
            # if session expires we'll try once to reconnect
            # in case of no success will throw error back
            if user_pass_retry_count < 1:
                user_pass_retry_count += 1
                if self.is_gov_cloud:
                    self.csp_credentials_store.remove_auth_tokens(vmc_address=self.server,
                                                                  user=user)
                    self.session_id = None
                    self.auth_token = None
                elif self.server_type == ServerTypes.VSPHERE:
                    # remove session to instantiate new one on next try
                    self.vapi_credentials_store.remove_session_ids(server=self.server,
                                                                   user=user,
                                                                   session_manager=self.session_manager)
                    self.session_id = None
                    self.auth_token = None
                elif self.server_type in [ServerTypes.VMC, ServerTypes.NSX]:
                    # get new CSP token for next call
                    self.csp_credentials_store.remove_auth_tokens(vmc_address=CliOptions.DCLI_VMC_SERVER,
                                                                  user=user)
                    self.get_csp_token(force=True)
                return True, invalid_credentials, user_pass_retry_count
            else:
                msg = 'Unable to authenticate user.'
                handle_error(msg)
                invalid_credentials = True
            return False, invalid_credentials, user_pass_retry_count
        else:
            if hasattr(error, 'name') and \
                (error.name in (SERVER_UNAUTHENTICATED_ERROR,
                                SERVER_UNAUTHORIZED_ERROR)):
                invalid_credentials = True
            return False, invalid_credentials, user_pass_retry_count

    def get_namespaces(self):
        """
        Returns list of all connection's namespaces

        :rtype:  :class:`list` of :class:`vmware.vapi.client.dcli.metadata.metadata_info.NamespaceInfo`
        :return: List of connection's namespaces
        """
        if not self.namespaces:
            self.namespaces = self.metadata_provider.get_namespaces()
        return self.namespaces

    def get_namespaces_names(self):
        """
        Returns list of all connection's namespaces full names

        :rtype:  :class:`list` of :class:`vmware.vapi.client.dcli.metadata.metadata_info.CommandInfo`
        :return: List of connection's namespaces full names
        """
        if not self.namespaces_names:
            self.namespaces_names = ['{}.{}'.format(ns.path, ns.name) for ns in self.get_namespaces()]
        return self.namespaces_names

    def get_commands(self):
        """
        Returns list of all connection's commands

        :rtype:  :class:`list` of :class:`vmware.vapi.client.dcli.metadata.metadata_info.CommandInfo`
        :return: List of connection's commands
        """
        if not self.commands:
            self.commands = self.metadata_provider.get_commands()
        return self.commands

    def get_commands_names(self):
        """
        Returns list of all connection's commands full names

        :rtype:  :class:`list` of :class:`vmware.vapi.client.dcli.metadata.metadata_info.CommandInfo`
        :return: List of connection's commands full names
        """
        if not self.commands_names:
            self.commands_names = ['{}.{}'.format(cmd.path, cmd.name) for cmd in self.get_commands()]
        return self.commands_names
