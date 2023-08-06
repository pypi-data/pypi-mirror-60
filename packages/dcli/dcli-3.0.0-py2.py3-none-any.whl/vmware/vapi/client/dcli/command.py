#!/usr/bin/env python
"""
CLI command
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'VMware, Inc.'
__copyright__ = 'Copyright (c) 2015-2020 VMware, Inc.  All rights reserved. '
__license__ = 'SPDX-License-Identifier: MIT'
__docformat__ = 'epytext en'

import copy
import sys
import logging
import json
import six

try:
    have_pyprompt = True
    from prompt_toolkit import prompt  # pylint: disable=W0611
except ImportError:
    have_pyprompt = False

from com.vmware.vapi.std.errors_client import NotFound
from vmware.vapi.client.dcli.options import ArgumentInfo, ArgumentChoice
from vmware.vapi.client.dcli.util import (
    CliHelper, CliArgParser, CliHelpFormatter, StatusCode,
    BoolAction, BoolAppendAction,
    is_field_union_tag, is_field_union_case, get_metadata_field_info,
    union_case_matches_union_tag_value, ServerTypes, print_dcli_text,
    html_escape)
from vmware.vapi.client.dcli.exceptions import (
    handle_error, ParsingExit, handle_server_error, ParsingError,
    extract_error_msg, CliArgumentException, IntrospectionOperationNotFound,
    CompletionAuthentication)
from vmware.vapi.data.definition import (
    DynamicStructDefinition, StructDefinition)
from vmware.vapi.data.serializers.cleanjson import DataValueConverter
from vmware.vapi.data.type import Type
from vmware.vapi.data.value import (
    StructValue, StringValue, IntegerValue, DoubleValue, SecretValue,
    BooleanValue, BlobValue, OptionalValue, ListValue)
from vmware.vapi.lib.constants import MAP_ENTRY
from vmware.vapi.lib.rest import OperationRestMetadata
from vmware.vapi.provider.filter import ApiProviderFilter

try:
    import argparse
except ImportError as e:
    print_dcli_text('<ansired>Error: No argparse module present quitting.</ansired>', file=sys.stderr)
    sys.exit(StatusCode.INVALID_ENV)


data_type_dict = {
    int: 'int',
    str: 'string',
    bool: 'bool',
    float: 'double'
}

logger = logging.getLogger(__name__)


class CliCommand(object):
    """
    Class to manage operations related to actual commands.
    """
    def __init__(self, connection,
                 path=None, name=None):
        self.server_type = connection.server_type
        self.connector = connection.connector
        self.last_api_provider = None
        self.api_provider = None
        self.metadata_provider = connection.metadata_provider
        self.path = path
        self.name = name
        self.secret_map = None
        self.cmd_info = None
        self.operation_info = None
        self.default_options = connection.default_options
        self.connection = connection

        if self.connector:
            self.api_provider = self.connector.get_api_provider()
            self.retrieve_api_provider()

        self.is_cmd = True

        try:
            self.cmd_info = self.metadata_provider.get_command_info(path, name)
        except NotFound:
            self.is_cmd = False

    def retrieve_api_provider(self):
        """
        Traverses through chain of providers to get actual API Provider
        instead of API Provider Filter
        """
        if isinstance(self.api_provider, ApiProviderFilter):
            # Get the API Provider (last provider in the chain)
            self.last_api_provider = self.api_provider.get_api_provider()
        else:
            self.last_api_provider = self.api_provider
        if self.server_type in (ServerTypes.NSX, ServerTypes.NSX_ONPREM, ServerTypes.VMC):
            # Set to use REST Native format instead of vAPI REST
            self.last_api_provider.set_rest_format(False)

    def prompt_for_secret_fields(self, args):
        """
        Method to prompt for secret fields

        :type  args: :class:`argparse.Namespace`
        :param args: Parsed input command arguments object
        """
        for key, prompt_msg in six.iteritems(self.secret_map):
            option_val = getattr(args, key)

            # Only prompt for secret options if they are passed on command line
            # without value. If secret option is not passed on command line
            # option_val will be None. If secret option is passed but no value
            # given option_val will be False. If option is passed along with
            # value then option_val will contain the value.
            # We only need to prompt for cases where option_val is False.
            # For list of secrets any of the input option values can be False
            # for which we need to prompt the user.
            if option_val is False:
                secret_val = CliCommand.prompt_for_secret(prompt_msg)
                setattr(args, key, secret_val)
            elif isinstance(option_val, list) and False in option_val:
                secret_val = []
                for val in option_val:
                    if val is False:
                        tmp_val = CliCommand.prompt_for_secret(prompt_msg)
                        secret_val.append(tmp_val)
                    else:
                        secret_val.append(val)
                setattr(args, key, secret_val)

    @staticmethod
    def prompt_for_secret(prompt_msg):
        """
        Provide non-echo prompt for secret fields

        :type  prompt_msg: :class:`str`
        :param prompt_msg: Prompt for secret input

        :rtype:  :class:`str`
        :return: Secret value
        """
        try:
            if have_pyprompt:
                secret = prompt(prompt_msg, is_password=True)
            else:
                import getpass
                secret = getpass.getpass(str(prompt_msg))
            return secret
        except (EOFError, KeyboardInterrupt):
            pass

        # XXX change to return
        sys.exit(StatusCode.INVALID_ARGUMENT)

    def is_a_command(self):
        """
        Return if the command is of command type

        :rtype:  :class:`bool`
        :return: True if its a command else False
        """
        return self.is_cmd

    def get_input_arg_info(self, arg, add_dynamic_struct_option=False):
        """
        Get the list ArgumentInfo objects for all command input options

        :type  arg: :class:`vmware.vapi.metadata.cli.command.OptionInfo`
        :param arg: CLI command option info structure
        :type  add_dynamic_struct_option: :bool:
        :param add_dynamic_struct_option: Flag to add dynamic struct option

        :rtype:  :class:`ArgumentInfo`
        :return: ArgumentInfo object containing struct field details
        """
        if add_dynamic_struct_option:
            # For older metadata versions with dynamicstruct input
            display_name = '--%s' % (arg.field_name.split('.')[0].replace('_', '-'))
            generic_type = 'optional'
        else:
            display_name = '--%s' % (arg.long_option)
            generic_type = arg.generic

        short_name = '-%s' % (arg.short_option) if arg.short_option else None
        description = arg.description
        arg_type = arg.type

        arg_action = 'append' if self.is_generic_list(generic_type) else 'store'

        type_ = CliCommand.convert_vapi_to_python_type(arg_type)

        if type_ == bool:
            type_ = str
            arg_action = BoolAppendAction if self.is_generic_list(generic_type) else BoolAction

        arg_desc = ''

        if generic_type == 'list':
            data_type_str = 'list of '
        elif generic_type == 'list_optional':
            data_type_str = 'list of optional '
        elif generic_type == 'optional_list':
            data_type_str = 'optional list of '
        elif generic_type == 'optional':
            data_type_str = ''
        else:
            arg_desc = 'required:'
            data_type_str = ''

        arg_nargs = None

        if arg_type == 'secret':
            arg_nargs = '?'
            data_type_str = '%ssecret ' % data_type_str

        if arg_type in ['complex', 'complex-hasfieldsof', 'dynamicstructure']:
            data_type_str = '(%sjson input)' % (data_type_str)
            tmp_desc = '%s %s' % (description, data_type_str)
            type_ = str
        elif arg_type == 'binary':
            type_ = argparse.FileType('rb')
            data_type_str = '(%s file input)' % (data_type_str)
            tmp_desc = '%s %s' % (description, data_type_str)
        else:
            data_type_str = '(%s%s)' % (data_type_str,
                                        data_type_dict.get(CliCommand.convert_vapi_to_python_type(arg_type), 'string'))
            tmp_desc = '%s %s' % (description, data_type_str)
        option_default_value = self.get_input_arg_default_value(arg)

        if arg_desc and option_default_value is None:
            arg_desc = '%s %s' % (arg_desc, tmp_desc)
        else:
            arg_desc = tmp_desc

        arg_info = ArgumentInfo()
        arg_info.short_name = short_name
        arg_info.name = display_name
        arg_info.arg_action = arg_action
        arg_info.description = arg_desc
        arg_info.required = generic_type not in ('optional', 'optional_list', 'list_optional')
        arg_info.nargs = arg_nargs
        arg_info.depends_on = arg.depends_on
        arg_info.is_discriminator = arg.is_discriminator

        if option_default_value is not None:
            arg_info.default = option_default_value
            arg_info.required = False

        arg_info.choices = arg.choices

        if arg_type == 'secret':
            tmp_name = display_name.lstrip('--')
            self.secret_map[tmp_name.replace('-', '_')] = '%s: ' % tmp_name
            arg_info.const = False
        else:
            # XXX need to handle blob and opaque
            arg_info.type_ = type_

        if self.cmd_info.service_id == 'env.style.color.theme' \
                and self.cmd_info.operation_id == 'set' \
                and arg.field_name == 'theme':
            arg_info.choices = []
            for item in ['bw', 'monokai', 'paraiso-dark', 'autumn']:
                arg_info.choices.append(ArgumentChoice(item, item, ''))

        return arg_info

    @staticmethod
    def convert_vapi_to_python_type(type_str):
        """
        Convert the vapi type name to python type name

        :type  type_str: :class:`str`
        :param type_str: vAPI type name

        :rtype:  :class:`type`
        :return: Python type name
        """
        return {'long': int,
                'boolean': bool,
                'double': float}.get(type_str, six.text_type)

    def get_input_arg_default_value(self, arg):
        """
        Gets default value for given argument from env profiles options

        :type  arg: :class:`vmware.vapi.metadata.cli.command.OptionInfo`
        :param arg: CLI command option info structure

        :rtype:  :class:`str`
        :return: default value for argument
        """
        # set default value from default options in configuration if present
        module = CliHelper.get_module_name(self.server_type)
        if not self.default_options:
            return None
        return self.default_options.try_get(arg.long_option, module=module)

    @classmethod
    def is_generic_list(cls, generic_type):
        """
        Checks whether given generic_type is represention of list or optional list or list of optionals

        :type  arg: :class:`str`
        :param generic_type: generict type to be checked

        :rtype:  :class:`boolean`
        :return: boolean indicating whether generic_type is represention of list or optional list
        """
        return generic_type in ('list', 'optional_list', 'list_optional')

    def get_parser_arguments(self, command=None):
        """
        Method to get vAPI command argument details struct list for a specific command
        If command is provided parameters are retreived based on given input as well

        :type  command: :class:`str`
        :param command: command string; used when discriminator field is present

        :rtype:  :class:`list` of :class:`ArgumentInfo`
        :return: List of ArgumentInfo object containing struct field details
        """
        input_arg_details = []
        retval = StatusCode.SUCCESS
        self.secret_map = {}

        all_options = self.cmd_info.options

        self.handle_discriminator(all_options, command)

        # sorting args by field_name to ensure correct order for
        # @HasFieldsOf options
        sorted_options = sorted(self.cmd_info.options, key=lambda x: x.field_name)

        for arg in sorted_options:  # pylint: disable=too-many-nested-blocks
            if arg.type in ['map', 'opaque', 'void']:
                error_msg = '%s input type not supported' % arg.type.title()
                handle_error(error_msg, print_error=False)
                raise CliArgumentException(error_msg, StatusCode.INVALID_COMMAND)

            # Needed for compatibility with older version of CLI metadata
            # for dynamic struct inputs
            # For struct and dynamic struct inputs
            if arg.field_name.find('.') != -1 or arg.type == 'dynamicstructure':
                if self.cmd_info.input_definition:
                    if self.cmd_info.input_definition.get_field(arg.field_name.split('.')[0]).type == Type.LIST:
                        error_msg = 'List of structure type not supported'
                        handle_error(error_msg)
                        raise CliArgumentException(error_msg, StatusCode.INVALID_COMMAND)
                    elif arg.field_name.find('.') != -1:
                        field_name = arg.field_name.split('.')[0]
                        field_input_def = self.cmd_info.input_definition.get_field(field_name)
                        if isinstance(field_input_def, DynamicStructDefinition):
                            # For HasFieldsOf case add extra argument for purely
                            # dynamic structure json input
                            arg_info = self.get_input_arg_info(arg, True)

                            # Check if argument is already in the list
                            has_arg = [arg_detail for arg_detail in input_arg_details
                                       if input_arg_details and arg_detail.name == arg_info.name]

                            # If the argument doesn't exist add it to list
                            if not has_arg:
                                input_arg_details.append(arg_info)

            arg_info = self.get_input_arg_info(arg)
            input_arg_details.append(arg_info)

        return retval, input_arg_details

    def handle_discriminator(self, all_options, command):
        """
        Finds discriminator options in command.
        For each option updates rest of the options accordingly with dependency information

        :type  all_options: :class:`list` of :class:`ArgumentInfo`
        :param all_options: list of accumulated ArgumentInfo options up to the moment of calling method
        :type  command: :class:`str`
        :param command: command call string used to deduce additional options by given discriminator value
        """
        # handling descriminator options
        operation = None
        for arg in [arg for arg in self.cmd_info.options if arg.type == 'complex-hasfieldsof']:
            discriminator_option = None
            discriminable_field = None
            try:
                if not operation:
                    operation = self.metadata_provider.get_operation_info(self.cmd_info.service_id, self.cmd_info.operation_id)
            except NotFound:
                operation = None

            if operation:
                struct_name, discriminable_field = self.get_struct_name(arg.field_name,
                                                                        operation.params)

            # if field is not annotated with DynamicContract - continue
            if not struct_name \
                    or not discriminable_field \
                    or not discriminable_field.dynamic_contract_service:
                continue

            struct_info = self.metadata_provider.get_structure_info(struct_name)
            for field in struct_info.fields:
                if field.is_discriminator:
                    discriminator_option = [option
                                            for option
                                            in self.cmd_info.options
                                            if option.field_name == '{}.{}'.format(arg.field_name, field.name)]
                    discriminator_option[0].is_discriminator = True
                    break

            if not discriminator_option or not discriminable_field:
                continue

            discriminator_options = []
            self.handle_discriminator_options(discriminator_option[0], arg, discriminable_field, discriminator_options, command)
            # we need to renew duplicate options
            for d_option in discriminator_options:
                in_all_options = False
                for idx, a_option in enumerate(all_options):
                    if d_option.long_option == a_option.long_option:
                        all_options[idx] = d_option
                        in_all_options = True
                        break
                if not in_all_options:
                    all_options.append(d_option)

    def handle_discriminator_options(self, discriminator_option, cli_discriminable_arg, discriminable_field, all_options, command):
        """
        Finds discriminator option and sets it's dependent options accordingly

        :type  discriminator_option: :class:`str`
        :param discriminator_option: discriminator's long option value
        :type  cli_discriminable_arg: :class:`ArgumentInfo`
        :param cli_discriminable_arg: cli argument info representing discriminator's parent structure cli option.
            That is the option with 'complex-hasfieldsof' generic value.
        :type  discriminable_field: :class:`FieldInfo`
        :param discriminable_field: field info of the field to which discriminator belongs to.
            Field must be annotated with @HasFieldOf annotation.
        :type  all_options: :class:`list` of :class:`ArgumentInfo`
        :param all_options: list of accumulated ArgumentInfo options up to the moment of calling method
        :type  command: :class:`str`
        :param command: command call string used to deduce additional options by given discriminator value
        """
        # getting discriminator options
        list_options_output = self.call_another_command(discriminable_field.dynamic_contract_service,
                                                        'list',
                                                        [])
        for struct_val in list_options_output:
            field_name = discriminator_option.field_name.split('.')[-1]
            choice_value = struct_val.get_field(field_name).value
            choice_name = struct_val.get_field('name').value if struct_val.has_field('name') else choice_value
            choice_description = struct_val.get_field('description').value if struct_val.has_field('description') else ''
            option = ArgumentChoice(choice_value, choice_name, choice_description)
            if option not in discriminator_option.choices:
                discriminator_option.choices.append(option)

        # filling in dependency information
        discriminator_long_option = '--{}'.format(discriminator_option.long_option)
        for option in self.cmd_info.options:
            if option.field_name.startswith(discriminator_option.field_name[:discriminator_option.field_name.rfind('.')]) \
                    and discriminator_option.field_name != option.field_name \
                    and option.depends_on is None:
                option.depends_on = {discriminator_long_option: []}

        args_values = CliHelper.get_args_values(command) if command else None
        selected_struct = None
        if args_values \
                and discriminator_long_option in args_values \
                and args_values[discriminator_long_option] in [option.value for option in discriminator_option.choices]:
            get_type_command_output = self.call_another_command(discriminable_field.dynamic_contract_service,
                                                                'get',
                                                                [discriminator_long_option, args_values[discriminator_long_option]])
            field_name = '{}_type'.format(discriminable_field.has_fields_of_struct_name.split('.')[-1])
            selected_struct = get_type_command_output.get_field(field_name).value

            structure = self.metadata_provider.get_structure_info(selected_struct)
            discriminator_additional_options = []
            self.metadata_provider.get_options_from_field_infos(structure.fields,
                                                                cli_discriminable_arg.field_name,
                                                                cli_discriminable_arg.long_option,
                                                                cli_discriminable_arg.generic == 'optional',
                                                                [],
                                                                discriminator_additional_options)
            self.metadata_provider.handle_options_long_names(discriminator_additional_options)
            for idx, option in enumerate(discriminator_additional_options):
                if '--{}'.format(option.long_option) == discriminator_long_option:
                    discriminator_additional_options[idx] = discriminator_option
                    continue

                if not option.depends_on:
                    option.depends_on = {discriminator_long_option: []}

                if args_values[discriminator_long_option] not in option.depends_on[discriminator_long_option]:
                    option.depends_on[discriminator_long_option].append(args_values[discriminator_long_option])
            all_options.extend(discriminator_additional_options)

    def call_another_command(self, path, name, args):
        """
        Calls a command different from the one handled by current instance

        :type  path: :class:`str`
        :param path: command's dcli path
        :type  name: :class:`str`
        :param name: command's dcli name
        :type  args: :class:`list` of :class:`str`
        :param args: command's arguments as list of strings

        :rtype:  :class:`vmware.vapi.data.value.DataValue`
        :return: DataValue corresponding to the input type
        """
        path = path.replace('_', '')
        name = name.replace('_', '')
        tmp_connection = copy.deepcopy(self.connection)
        cli_cmd_instance = tmp_connection.get_cmd_instance(path, name)

        if cli_cmd_instance.is_a_command():
            try:
                result = tmp_connection.call_command(cli_cmd_instance,
                                                     args)
            except CompletionAuthentication as e:
                e.connection = self.connection
                e.path = cli_cmd_instance.cmd_info.service_id
                e.name = cli_cmd_instance.cmd_info.operation_id
                raise e
        else:
            handle_error("Could not find command '{}' in service '{}'".format(name, path.replace(' ', '.')),
                         print_error=False)
            return None
        if result is not None and result.success():
            return result.output
        else:
            handle_error("There was an error while executing command '{} {}'".format(path, name),
                         print_error=False)
        return None

    def add_parser_argument(self, parser, json_input=None, generate_json_input=False, command=None):
        """
        Method to add vAPI command arguments to the CliArgParser object

        :type  parser: :class:`CliArgParser`
        :param parser: CliArgParser object
        :type  generate_json_input: :class:`bool`
        :param generate_json_input: specifies whether user wants to output command's input as json object
        :type  json_input: :class:`obj`
        :param json_input: json input (converted to python object) to be used as command's input
        :type  command: :class:`str`
        :param command: command string; used when discriminator field is present

        :rtype:  :class:`StatusCode`
        :return: Status code
        """
        group = parser.add_argument_group('Input Arguments')
        retval, input_args = self.get_parser_arguments(command=command)
        if retval == StatusCode.SUCCESS:
            group.add_argument('-h',
                               '--help',
                               action='help',
                               help='show this help message and exit')
            for arg in input_args:
                kwargs = {
                    'action': arg.arg_action,
                    'const': arg.const,
                    'nargs': arg.nargs,
                    'required': arg.required if json_input is None and not generate_json_input else False,
                    'help': arg.description,
                }

                if arg.default is not None:
                    kwargs['default'] = arg.default

                if arg.const is not False:
                    kwargs['type'] = arg.type_
                    kwargs['choices'] = [choice.value for choice in arg.choices] if arg.choices else None

                # Make all list inputs optional as VMODL2 required lists can be empty
                if arg.arg_action == 'append':
                    kwargs['required'] = False
                    # If its a required list input set a default value as empty list
                    if arg.required:
                        kwargs['default'] = []

                if arg.short_name:
                    group.add_argument(arg.short_name, arg.name, **kwargs)
                else:
                    group.add_argument(arg.name, **kwargs)

        return retval

    @staticmethod
    def get_data_value(data_type, value):
        """
        Method to convert data type and value to DataValue object

        :type  data_type: :class:`str`
        :param data_type: Data type of the parameter
        :type  value: :class:`type`
        :param value: Value of the parameter

        :rtype:  :class:`vmware.vapi.data.value.DataValue`
        :return: DataValue corresponding to the input type
        """
        if data_type == 'boolean':
            return BooleanValue(value)
        elif data_type == 'double':
            return DoubleValue(value)
        elif data_type == 'long':
            return IntegerValue(value)
        elif data_type == 'secret':
            return SecretValue(value)
        elif data_type == 'binary':
            return BlobValue(value)
        return StringValue(value)

    def get_command_parser(self, json_input=None, generate_json_input=False, command=None):
        """
        Get the command parser for vAPI command

        :type  generate_json_input: :class:`bool`
        :param generate_json_input: specifies whether user wants to output command's input as json object
        :type  json_input: :class:`obj`
        :param json_input: json input (converted to python object) to be used as command's input
        :type  command: :class:`str`
        :param command: command string; used when discriminator field is present

        :rtype:  :class:`StatusCode`
        :return: Status code
        :rtype:  :class:`CliArgParser`
        :return: CLI argument parser
        """
        cmd_name = '%s %s' % (' '.join(self.cmd_info.identity.path.split('.')),
                              self.cmd_info.identity.name)
        parser = CliArgParser(prog=cmd_name,
                              description=self.cmd_info.description,
                              formatter_class=CliHelpFormatter,
                              add_help=False)

        retval = self.add_parser_argument(parser, json_input=json_input, generate_json_input=generate_json_input, command=command)
        return retval, parser

    @staticmethod
    def get_json_input(json_value):
        """
        Method to get JSON input from command line

        :type   json_value: :class:`str`
        :param  json_value: JSON input value or file name

        :rtype:  :class:`str`
        :return: Parsed JSON value as string
        """
        value = ''
        if json_value.lstrip()[0] in ['{', '[']:
            try:
                value = json.loads(json_value)
            except ValueError as e:
                raise Exception('Invalid json value provided. %s' % str(e))
        else:  # Else expect a json input file
            with open(json_value, 'r') as fp:
                value = json.load(fp)
        return value

    def get_command_input_dict(self, cmd_input):
        """
        From argparse input prepare a hierarchical dictionary-like input.

        :type  cmd_input: :class:`argparse.Namespace`
        :param cmd_input: Command input dict
        :rtype:  :class:`dict` of command input, :class:`list` of all field names for a command
        :return: Hierarchical command input, List of all field names for a command
        """
        # create a map of option name to option info
        option_map = {}
        for option in self.cmd_info.options:
            option_map[option.long_option.replace('-', '_')] = option

        input_tuple_list = []  # tuple of field name and value provided on the command line
        field_names = []  # list of all field names defined for a command
        # process json input with priority
        # so it can be later on overriden by hasfieldsof options
        json_input_options = {k: v
                              for k, v
                              in six.iteritems(cmd_input.__dict__)
                              if option_map[k].type in ('dynamicstructure',
                                                        'complex-hasfieldsof',
                                                        'complex')}
        for k, v in six.iteritems(json_input_options):
            if v is not None and not (isinstance(v, list) and not v):
                input_tuple_list.append((option_map[k].field_name, CliCommand.get_json_input(v)))
            field_names.append(option_map[k].field_name)

        # process all other values
        non_json_input_options = {k: v
                                  for k, v
                                  in six.iteritems(cmd_input.__dict__)
                                  if option_map[k].type not in ('dynamicstructure',
                                                                'complex-hasfieldsof',
                                                                'complex')}
        for k, v in six.iteritems(non_json_input_options):
            if v is not None and not (isinstance(v, list) and not v):
                input_tuple_list.append((option_map[k].field_name, v))
            field_names.append(option_map[k].field_name)

        # construct dictionary from given input based on field names
        input_dict = {}
        self._get_input_dict(input_tuple_list, input_dict)

        return input_dict, field_names

    def _get_input_dict(self, input_tuple_list, input_dict):
        """
        Method to convert a command input tuple into nested input dictionary

        :type   input_tuple_list: :class:`list` of :class:`tuple`
        :param  input_tuple_list: Input command options tuple
        :type   input_dict: :class:`dict`
        :param  input_dict: Nested input dictionary
        """
        for key, val in input_tuple_list:
            parts = key.split('.', 1)
            if len(parts) > 1:
                branch = input_dict.setdefault(parts[0], {})
                self._get_input_dict([(parts[1], val)], branch)
            else:
                input_dict[parts[0]] = val

    def build_data_value(self, input_dict=None, field_names=None, generate_json_input=False, required_fields_only=False):
        """
        Builds a command data value based on command's data definition and provided input dictionary.

        If no input_dict is provided it sets default values based
        on the types of the data value parameters.


        """
        input_value = self.cmd_info.input_definition.new_value()

        for field_name in self.cmd_info.input_definition.get_field_names():
            field_def = self.cmd_info.input_definition.get_field(field_name)

            data_value = None
            if isinstance(field_def, StructDefinition) \
                    and field_name not in input_dict:
                input_field_value = {}
            elif field_name not in input_dict:
                input_field_value = None
            else:
                input_field_value = input_dict[field_name]

            data_value = self._build_data_value(field_name,
                                                field_def,
                                                input_dict_value=input_field_value,
                                                field_names=field_names,
                                                generate_json_input=generate_json_input,
                                                required_fields_only=required_fields_only)

            if data_value:
                input_value.set_field(field_name, data_value)

        return input_value

    def _build_data_value(self, field_name, data_def, input_dict_value=None, field_names=None, generate_json_input=False, required_fields_only=False):
        """
        Converts a native python value to data value
        using the provided data definition

        :type  field_name: :class:`string`
        :param field_name: name of the field representing the data value object
        :type  data_def: :class:`vmware.vapi.data.definition.DataDefinition`
        :param data_def: data definition of the field
        :type  input_dict_value: :class:`dict`
        :param input_dict_value: Python input value in hierarchical dictionary format
        :type  field_names: :class:`list` of :class:`string`
        :param field_names: List of all the field names for the command
        :rtype: :class:`vmware.vapi.data.value.DataValue`
        :return: Data value
        """
        def is_map(data_def):
            """Check if provided data definition is a map."""
            if data_def.type == Type.LIST \
                    and data_def.element_type.type == Type.STRUCTURE \
                    and data_def.element_type.name == MAP_ENTRY:
                return True
            return False

        def is_old_format_map(input_obj):
            """Check if provided object is an input of the old map format."""
            if not isinstance(input_obj, list):
                return False

            for element in input_obj:
                if set(element.keys()) != set(['key', 'value']):
                    return False
            return True

        def is_new_format_map(input_obj):
            """Check if provided object is an input of the new map format."""
            return not is_old_format_map(input_obj)

        def handle_missing_required_field(field):
            """Raise error that a required field is missing"""
            option = [option for option in self.cmd_info.options if option.field_name == field]
            option_name = '--{}'.format(option[0].long_option) if option else field
            error_msg = "Required option {} is missing.".format(option_name)
            raise Exception(error_msg)

        output_val = None
        if data_def.type == Type.OPTIONAL:
            if required_fields_only and input_dict_value is None:
                return None

            output_val = data_def.new_value()
            if input_dict_value is not None:
                output_val.value = self._build_data_value(field_name,
                                                          data_def.element_type,
                                                          input_dict_value=input_dict_value,
                                                          field_names=field_names,
                                                          generate_json_input=generate_json_input,
                                                          required_fields_only=required_fields_only)
            elif generate_json_input:
                output_val.value = self._build_data_value(field_name,
                                                          data_def.element_type,
                                                          generate_json_input=generate_json_input,
                                                          required_fields_only=required_fields_only)
        elif data_def.type == Type.LIST:
            output_val = data_def.new_value()
            # map handling
            if input_dict_value:
                if is_map(data_def):
                    if is_new_format_map(input_dict_value):
                        new_input_dict_value = []
                        for key, value in six.iteritems(input_dict_value):
                            new_input_dict_value.append({'key': key, 'value': value})
                        input_dict_value = new_input_dict_value

                for element in input_dict_value:
                    output_val.add(self._build_data_value(field_name,
                                                          data_def.element_type,
                                                          input_dict_value=element,
                                                          field_names=field_names,
                                                          generate_json_input=generate_json_input,
                                                          required_fields_only=required_fields_only))
            elif generate_json_input:
                if required_fields_only and data_def.element_type.type == Type.OPTIONAL:
                    return data_def.new_value()
                if is_map(data_def):
                    values_def = data_def.element_type.get_field('value')
                    output_val = StructDefinition(MAP_ENTRY, [("", values_def)]).new_value()
                    output_val.set_field("", self._build_data_value("",
                                                                    values_def,
                                                                    generate_json_input=generate_json_input,
                                                                    required_fields_only=required_fields_only))
                else:
                    output_val.add(self._build_data_value(field_name,
                                                          data_def.element_type,
                                                          generate_json_input=generate_json_input,
                                                          required_fields_only=required_fields_only))

        elif data_def.type in (Type.STRUCTURE, Type.ERROR):
            output_val = data_def.new_value()
            for field in data_def.get_field_names():
                field_def = data_def.get_field(field)

                if generate_json_input:
                    value = None
                    if input_dict_value is not None:
                        value = input_dict_value.get(field)
                    if required_fields_only \
                            and (field_def.type == Type.OPTIONAL
                                 or (field_def.type == Type.LIST
                                     and field_def.element_type.type == Type.OPTIONAL)) \
                            and value is None:
                        continue
                    output_val.set_field(field,
                                         self._build_data_value('{}.{}'.format(field_name, field),
                                                                field_def,
                                                                input_dict_value=value,
                                                                generate_json_input=generate_json_input,
                                                                required_fields_only=required_fields_only))
                elif input_dict_value is not None:
                    value = input_dict_value.get(field)
                    output_val.set_field(field,
                                         self._build_data_value('{}.{}'.format(field_name, field),
                                                                field_def,
                                                                input_dict_value=value,
                                                                field_names=field_names,
                                                                generate_json_input=generate_json_input,
                                                                required_fields_only=required_fields_only))
                elif input_dict_value is None:
                    handle_missing_required_field('{}.{}'.format(field_name, field))
        elif data_def.type == Type.DYNAMIC_STRUCTURE:
            if input_dict_value is not None:
                output_val = DataValueConverter.convert_to_data_value(json.dumps(input_dict_value))

                # we now have data value with emtpy struct names
                # fill struct names from @HasFieldsOf annotation if provided
                self.fill_has_fields_of_info(field_name,
                                             output_val,
                                             field_names)
            elif generate_json_input:
                struct_name, _ = self.get_struct_name(field_name, self.get_operation_info().params)
                struct_def = None
                if struct_name:
                    struct_def = self.metadata_provider.get_structure_input_definition(struct_name)
                if struct_def:
                    output_val = self._build_data_value(field_name,
                                                        struct_def,
                                                        generate_json_input=generate_json_input,
                                                        required_fields_only=required_fields_only)
                else:
                    output_val = StructValue()
            elif input_dict_value is None:
                handle_missing_required_field(field_name)
        elif data_def.type == Type.VOID:
            output_val = data_def.new_value()
        elif data_def.type == Type.BLOB:
            if input_dict_value:
                # For Binary input user passes a file with binary data
                # on command line. And argparse gives us a file object
                input_dict_value.seek(0)
                blob_value = input_dict_value.read()
                output_val = data_def.new_value(blob_value)
            elif generate_json_input:
                output_val = data_def.new.new_value()
            elif input_dict_value is None:
                handle_missing_required_field(field_name)
        elif data_def.type == Type.OPAQUE:
            raise Exception('Unsupported input type OPAQUE')
        # Primitive type Integer/Double/String/Boolean/Secret
        else:
            if input_dict_value is not None:
                output_val = data_def.new_value(input_dict_value)
            elif generate_json_input:
                output_val = data_def.new_value()
            elif input_dict_value is None:
                handle_missing_required_field(field_name)
        return output_val

    def get_struct_name(self, field_name, metamodel_fields):
        """
        For given collection of fields and field name retrieves structure name,
        if any, for the structure which field_name is part of and is annotatated
        with @HasFieldsOf

        :type  field_name: :class:`string`
        :param field_name: name of the field representing a structure
        :type  metamodel_fields: :class:`list` of :class:`vmware.vapi.client.dcli.metadata.metadata_info.FieldInfo`
        :param metamodel_fields: List of fields to search for structure annotated with @HasFieldsOf
        :rtype: :class:`string`
        :return: tuple of path of strucutre annotated with @HasFieldsOf or empty string otherwise
            and the @HasFieldsOf annotated field itself
        """
        field_name_parts = field_name.split('.')
        for field in metamodel_fields:
            if field.name != field_name_parts[0]:
                continue

            # if there's a dot in the field name it means there's nested structure
            # we need to find it's name
            if len(field_name_parts) > 1:
                # traverse through generics if present to get user defined structure type
                struct_type = field.type
                while struct_type.category == 'GENERIC':
                    struct_type = struct_type.generic_instantiation.element_type

                if struct_type.category != 'USER_DEFINED' \
                        or struct_type.user_defined_type.resource_type == 'com.vmware.vapi.enumeration':
                    return '', None

                try:
                    struct = self.metadata_provider.get_structure_info(struct_type.user_defined_type.resource_id)
                except NotFound:
                    return '', None

                return self.get_struct_name('.'.join(field_name_parts[1:]), struct.fields)

            # if there's no dot in the field name it means we've
            # reached structure of interest; return its name
            if field.has_fields_of_struct_name:
                return field.has_fields_of_struct_name, field
            return '', None

    def fill_has_fields_of_info(self, field_name, data_value, field_names):
        """
        For given data value of dynamic structure fills in structure names
        information for fields which are annotated with @HasFieldsOf

        :type  field_name: :class:`string`
        :param field_name: name of the field representing the data value object
        :type  data_value: :class:`vmware.vapi.data.value.DataValue`
        :param data_value: Data value object to update
        :type  field_names: :class:`list` of :class:`string`
        :param field_names: List of all the field names for the command
        """
        if isinstance(data_value, OptionalValue):
            self.fill_has_fields_of_info(field_name, data_value.value, field_names)
        elif isinstance(data_value, ListValue):
            for element in data_value:
                self.fill_has_fields_of_info(field_name, element, field_names)
        elif isinstance(data_value, StructValue):
            if not [True for list_field_name in field_names if '%s.' % field_name in list_field_name]:
                return None

            # we're dealing with has fields of structure
            # find structure name
            try:
                struct_name, _ = self.get_struct_name(field_name, self.get_operation_info().params)
            except NotFound:
                struct_name = ''
            data_value.name = struct_name

            for field in data_value.get_fields():
                self.fill_has_fields_of_info('{}.{}'.format(field_name, field[0]), field[1], field_names)
        return None

    def get_operation_info(self):
        """
        Gets operation info for the command.
        Ensures this information is gathered only once

        :rtype:  :class:`vmware.vapi.client.dcli.metadata.metadat_info.OperationInfo`
        :return: OperationInfo object for command
        """
        if not self.operation_info:
            self.operation_info = \
                self.metadata_provider.get_operation_info(
                    self.cmd_info.service_id,
                    self.cmd_info.operation_id)

        return self.operation_info

    def collect_command_input(self, args_, json_input=None, generate_json_input=False):
        """
        Collects command dictionary like input by using argparse parser

        :type  args_: :class:`list` of :class:`str`
        :param args_: Command input as list of strings
        :type  generate_json_input: :class:`bool`
        :param generate_json_input: specifies whether user wants to output command's input as json object
        :type  json_input: :class:`obj`
        :param json_input: json input (converted to python object) to be used as command's input

        :rtype:  :class:`list` of input argument options
        :return: Parsed command's input
        """
        partial_command = ' '.join(args_)
        retval, cmd_parser = self.get_command_parser(json_input=json_input, generate_json_input=generate_json_input, command=partial_command)

        if retval != StatusCode.SUCCESS:
            error_msg = 'An error occured while trying to get command parser'
            raise CliArgumentException(error_msg, retval)

        # add command inputs to new argument parser
        cmd_input = None
        try:
            if json_input or generate_json_input:
                cmd_input = cmd_parser.parse_known_args(args_)[0]
            else:
                cmd_input = cmd_parser.parse_args(args_)
        except ParsingError as e:
            if cmd_input is not None and not cmd_input.help:
                print_dcli_text(html_escape(cmd_parser.print_help()))
            msg = extract_error_msg(e)
            if msg:
                handle_error('Failed while retrieving CLI command details: %s' % msg)
            raise CliArgumentException(msg, StatusCode.INVALID_ARGUMENT, print_error=False)
        except ParsingExit as e:
            if cmd_input and not cmd_input.help:
                print_dcli_text(html_escape(cmd_parser.print_help()))
            msg = extract_error_msg(e)
            if msg:
                handle_error(msg, exception=e)
            raise CliArgumentException(msg, StatusCode.INVALID_ARGUMENT, print_error=False)

        self.prompt_for_secret_fields(cmd_input)

        return cmd_input

    def execute_command(self, ctx, args_, json_input=None):
        """
        Method to execute vAPI operations

        :type  ctx: :class:`vmware.vapi.core.ExecutionContext`
        :param ctx: Execution context for this method
        :type  args_: :class:`list` of :class:`str`
        :param args_: Command input as list of strings
        :type  json_input: :class:`obj`
        :param json_input: json input (converted to python object) to be used as command's input

        :rtype:  :class:`vmware.vapi.core.MethodResult`
        :return: MethodResult for the vAPI operation
        """
        cmd_input = self.collect_command_input(args_, json_input=json_input)
        input_dict, field_names = self.get_command_input_dict(cmd_input)

        if json_input:
            json_input.update(input_dict)
            input_dict = json_input

        if self.cmd_info.input_definition is None:
            error_msg = 'Unable to find operation %s' % (
                self.cmd_info.identity.name)
            error_msg += ' in service %s' % (self.cmd_info.identity.path)
            logger.error(error_msg)
            raise IntrospectionOperationNotFound(error_msg)
        else:
            input_value = self.build_data_value(input_dict=input_dict,
                                                field_names=field_names)
        logger.info('Invoking vAPI operation %s for service %s',
                    self.cmd_info.operation_id, self.cmd_info.service_id)

        if self.server_type in (ServerTypes.NSX, ServerTypes.VMC, ServerTypes.NSX_ONPREM):
            rest_metadata = self.get_rest_metadata()
            self.last_api_provider.add_rest_metadata(self.cmd_info.service_id,
                                                     self.cmd_info.operation_id,
                                                     rest_metadata)

        return self.api_provider.invoke(self.cmd_info.service_id,
                                        self.cmd_info.operation_id,
                                        input_value,
                                        ctx)

    def get_rest_metadata(self):
        """
        Collects operation specific rest metadata, if any, for execution of
        dcli command

        :rtype :class:`vmware.vapi.lib.rest.OperationRestMetadata`
        :return: OperationRestMetadata object with needed rest metadata for
            executing command
        """
        return OperationRestMetadata(
            http_method=self.cmd_info.rest_info.http_method,
            url_template=self.cmd_info.rest_info.url_template,
            request_body_parameter=self.cmd_info.rest_info.request_body_field,
            path_variables=self.cmd_info.rest_info.path_variable_map,
            query_parameters=self.cmd_info.rest_info.request_param_map
        )

    def display_result(self, output, out_formatter, more):
        """
        Print the vAPI operation result

        :type  output: :class:`vmware.vapi.core.MethodResult`
        :param output: MethodResult for vAPI operation
        :type  out_formatter: :class:`vmware.vapi.client.lib.Formatter`
        :param out_formatter: Output formatter

        :rtype:  :class:`StatusCode`
        :return: Method status
        """
        output_structures_metadata = self.collect_output_structures_metadata()

        if output.success():
            result = output.output

            out_formatter.apply_structure_filter_visitor(
                self.formatter_apply_structure_filter_visitor)
            out_formatter.structure_element_visit(
                self.formatter_structure_element_visit)
            out_formatter.format_output(
                result,
                more=more,
                metamodel_struct_list=output_structures_metadata)

        if output.error is not None:
            handle_server_error(output.error)
            if self.server_type in (ServerTypes.NSX, ServerTypes.VMC):
                out_formatter.format_output(
                    output.error.get_field('data'),
                    more=more,
                    metamodel_struct_list=output_structures_metadata)
                return StatusCode.INVALID_COMMAND
            return StatusCode.INVALID_COMMAND

        return StatusCode.SUCCESS

    def collect_output_structures_metadata(self):
        """
        Collects metadata info for command's output structure types

        :rtype: :class:`list` of
                :class:`vmware.vapi.client.dcli.metadata.metadata_info.StructureInfo`
        :return: List of output structures metadata information
        """
        result = []
        if self.is_cmd:
            for output_info in self.cmd_info.output_field_list:
                if output_info.structure_id != MAP_ENTRY:
                    try:
                        result.append(self.metadata_provider.get_structure_info(
                            output_info.structure_id))
                    except NotFound as e:
                        err_msg = ('No metamodel information found '
                                   'for structure {}').format(output_info.structure_id)
                        handle_error(err_msg, print_error=False, exception=e)
        return result

    @classmethod
    def formatter_apply_structure_filter_visitor(cls, struct,
                                                 metadata_struct_info):
        """
        Determines whether a formatter should check whether to print a
        structure field or not.
        Function returns True if there are union tags in the structure,
        False otherwise

        :param struct: data value definition of the structure
        :type struct: :class:`vmware.vapi.data.value.StructValue`
        :param metadata_struct_info: metamodel info of the structure
        :type metadata_struct_info:
           :class:`vmware.vapi.client.dcli.metadata.metadata_info.StructureInfo`
        :return: Whether the structure should be check further for whether to
        print its fields by the formatter, collected structure union tags if any are presented
        :rtype: :class:`bool`, :class: class:`list` of :class:`tuple`
        """
        struct_union_tags = \
            [field for field in struct.get_fields() if
             is_field_union_tag(field[0], metadata_struct_info)]

        result = True if struct_union_tags else False

        return result, struct_union_tags

    @classmethod
    def formatter_structure_element_visit(cls, field_name, struct,
                                          metadata_struct_info, struct_union_tags):  # pylint: disable=W0613
        """
        Determines whether a structure field should be printed by the formatter.
        Field gets skiped if it is a union case not active based on the union
        tag it is associated to.

        :param field_name: the strucutre field name
        :type field_name: :class:`str`
        :param struct: data value definition of the structure
        :type struct: :class:`vmware.vapi.data.value.StructValue`
        :param metadata_struct_info: metamodel info of the structure
        :type metadata_struct_info:
           :class:`vmware.vapi.client.dcli.metadata.metadata_info.StructureInfo`
        :param struct_union_tags: union tags collected by formatter_apply_structure_filter_visitor method
        :type struct_union_tags: :class: class:`list` of :class:`tuple`
        :return: Whether the field should be printed by the formatter
        :rtype: :class:`bool`
        """
        field_value = struct.get_field(field_name)

        if not metadata_struct_info \
            or not (is_field_union_tag(field_name, metadata_struct_info)
                    or is_field_union_case(field_name, metadata_struct_info)):
            return True
        elif is_field_union_tag(field_name, metadata_struct_info) \
            and (isinstance(field_value, OptionalValue)
                 and field_value.value is None):
            return False
        elif is_field_union_tag(field_name, metadata_struct_info):
            return True

        union_case = get_metadata_field_info(field_name, metadata_struct_info)
        if union_case and \
                union_case_matches_union_tag_value(union_case,
                                                   struct_union_tags):
            return True
        return False
