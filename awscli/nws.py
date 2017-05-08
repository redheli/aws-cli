import sys
import argparse
from collections import OrderedDict


HELP_BLURB = (
    "To see help text, you can run:\n"
    "\n"
    "  nws help\n"
    "  nws <command> help\n"
    "  nws <command> <subcommand> help\n"
)
USAGE = (
    "nws [options] <command> <subcommand> [<subcommand> ...] [parameters]\n"
    "%s" % HELP_BLURB
)

class BaseNWSArgument(object):
    def __init__(self, name, help_text='', dest=None, default=None,
                 action=None, required=None, choices=None, nargs=None,
                 cli_type_name=None, group_name=None, positional_arg=False,
                 no_paramfile=False, argument_model=None, synopsis='',
                 const=None):
        self._name = name
        self._help = help_text
        self._dest = dest
        self._default = default
        self._action = action
        self._required = required
        self._nargs = nargs
        self._const = const
        self._cli_type_name = cli_type_name
        self._group_name = group_name
        self._positional_arg = positional_arg
        if choices is None:
            choices = []
        self._choices = choices
        self._synopsis = synopsis

    def add_to_arg_table(self, argument_table):
        argument_table[self.arg_name] = self

    @property
    def arg_name(self):
        if self._positional_arg:
            return self._name
        else:
            return '--' + self._name

    @property
    def documentation(self):
        return self._help

    def add_to_parser(self, parser):
        kwargs = {}
        if self._dest is not None:
            kwargs['dest'] = self._dest
        if self._action is not None:
            kwargs['action'] = self._action
        if self._default is not None:
            kwargs['default'] = self._default
        if self._choices:
            kwargs['choices'] = self._choices
        if self._required is not None:
            kwargs['required'] = self._required
        if self._nargs is not None:
            kwargs['nargs'] = self._nargs
        if self._const is not None:
            kwargs['const'] = self._const
        parser.add_argument(self.arg_name, **kwargs)

    def print_help(self):
        print '       {0}   {1}'.format(self.arg_name, self.documentation)


class CommandAction(argparse.Action):
    """Custom action for CLI command arguments

    Allows the choices for the argument to be mutable. The choices
    are dynamically retrieved from the keys of the referenced command
    table
    """
    def __init__(self, option_strings, dest, command_table, **kwargs):
        self.command_table = command_table
        super(CommandAction, self).__init__(
            option_strings, dest, choices=self.choices, **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

    @property
    def choices(self):
        return list(self.command_table.keys())

    @choices.setter
    def choices(self, val):
        # argparse.Action will always try to set this value upon
        # instantiation, but this value should be dynamically
        # generated from the command table keys. So make this a
        # NOOP if argparse.Action tries to set this value.
        pass

class NWSCommand(object):
    NAME=''
    DESCRIPTION = ''
    # If your command has arguments, you can specify them here.  This is
    # somewhat of an implementation detail, but this is a list of dicts
    # where the dicts match the kwargs of the CustomArgument's __init__.
    # For example, if I want to add a '--argument-one' and an
    # '--argument-two' command, I'd say:
    #
    # ARG_TABLE = [
    #     {'name': 'argument-one', 'help_text': 'This argument does foo bar.',
    #      'action': 'store', 'required': False, 'cli_type_name': 'string',},
    #     {'name': 'argument-two', 'help_text': 'This argument does some other thing.',
    #      'action': 'store', 'choices': ['a', 'b', 'c']},
    # ]
    #
    # A `schema` parameter option is available to accept a custom JSON
    # structure as input. See the file `awscli/schema.py` for more info.
    ARG_TABLE = []

    # If you want the command to have subcommands, you can provide a list of
    # dicts.  We use a list here because we want to allow a user to provide
    # the order they want to use for subcommands.
    # SUBCOMMANDS = [
    #     {'name': 'subcommand1', 'command_class': SubcommandClass},
    #     {'name': 'subcommand2', 'command_class': SubcommandClass2},
    # ]
    # The command_class must subclass from ``BasicCommand``.
    SUBCOMMANDS = []

    # If you want to provide some hand written examples, you can do
    # so here.
    EXAMPLES = ''

    def __init__(self):
        self._arg_table = None
        self._subcommand_table = None

    def __call__(self, args, parsed_globals):
        print 'NWSCommand call'
        parser = NWSArgParser(command_table=self.subcommand_table,
                              argument_table=self.arg_table, version_string='v0.1')

        parsed_args, remaining = parser.parse_known_args(args)

        try:
            if hasattr(parsed_args, 'help'):
                self._display_help(parsed_args, parsed_globals)
            elif getattr(parsed_args, 'command', None) is None:
                # No subcommand was specified so call the main
                # function for this top level command.
                if remaining:
                    raise ValueError("Unknown options: %s" % ','.join(remaining))
                return self._run_main(parsed_args, parsed_globals)
            else:
                return self.subcommand_table[parsed_args.command](remaining,
                                                                  parsed_globals)
        except Exception as e:
            sys.stderr.write(str(e))
            sys.stderr.write("\n")
            return 255

    def _run_main(self, parsed_args, parsed_globals):
        print 'NWSCommand _run_main'

    def _display_help(self, parsed_args, parsed_globals):
        # help_command = self.create_help_command()
        # help_command(parsed_args, parsed_globals)
        print '_display_help'
        print 'NAME'
        print '       {}\n'.format(self.NAME)
        print 'DESCRIPTION'
        print '       {}\n'.format(self.DESCRIPTION)
        print 'SUBCOMMANDS'
        for subcommand in self.SUBCOMMANDS:
            subcommand_name = subcommand['name']
            subcommand_class = subcommand['command_class']
            print '       {0}   {1}\n'.format(subcommand_class.NAME, subcommand_class.DESCRIPTION)
        if len(self.SUBCOMMANDS) is 0:
            print ''

        print 'ARGUMENTS'
        arg_table = self.arg_table
        for argument_name in arg_table:
            argument_class = arg_table[argument_name]
            argument_class.print_help()
        print ''
        print 'EXAMPLES'
        print '       {0}'.format(self.EXAMPLES)


    @property
    def name(self):
        # Subclasses must implement a name.
        raise NotImplementedError("name")

    @property
    def arg_table(self):
        if self._arg_table is None:
            self._arg_table = self._build_arg_table()
        return self._arg_table

    @property
    def subcommand_table(self):
        if self._subcommand_table is None:
            self._subcommand_table = self._build_subcommand_table()
        return self._subcommand_table

    def _build_arg_table(self):
        arg_table = OrderedDict()
        print '_build_arg_table'
        print self.ARG_TABLE
        for arg_data in self.ARG_TABLE:
            # print arg_data['name']
            arg1 = BaseNWSArgument(**arg_data)
            arg1.add_to_arg_table(arg_table)
        return arg_table

    def _build_subcommand_table(self):
        subcommand_table = OrderedDict()
        for subcommand in self.SUBCOMMANDS:
            subcommand_name = subcommand['name']
            subcommand_class = subcommand['command_class']
            subcommand_table[subcommand_name] = subcommand_class()
        return subcommand_table


#######################  Command 1
class  LSCommand(NWSCommand):
    NAME = 'LS'
    DESCRIPTION = 'List all the things in the world.'
    ARG_TABLE = [
        {'name': 'ls-arg-one', 'positional_arg': False, 'help_text': 'This is ls argument.',
         'action': 'store_true', },
    ]

    def _run_main(self, parsed_args, parsed_globals):
        print 'LSCommand ls subcommand'

class NWSDownloadCommand1(NWSCommand):
    print 'NWSDownloadCommand1'
    NAME = 'CMD1'
    DESCRIPTION = 'This is command one.\n     It is main command.'
    SUBCOMMANDS = [
        {'name': 'ls', 'command_class': LSCommand},
    ]
    ARG_TABLE = [
        {'name': 'argument-one',  'positional_arg': False, 'help_text': 'This argument does foo bar.',
         'action': 'store_true', },
        {'name': 'argument-two',  'positional_arg': False,'help_text': 'This argument does some other thing.',
         'action': 'store', 'default':'abc','choices': ['a', 'b', 'c']},
    ]
    EXAMPLES = 'nws cmd1 ls'

    def _run_main(self, parsed_args, parsed_globals):
        print 'NWSDownloadCommand1 _run_main'
        if parsed_args.command is None:
            raise ValueError("usage: nws [options] <command> <subcommand> "
                             "[parameters]\nnws: error: too few arguments")

#######################  Command 2
class  CPCommand(NWSCommand):
    NAME = 'CP'
    DESCRIPTION = 'This is cp command.'
    def __call__(self, parsed_args, parsed_globals):
        print 'cmd2 cp subcommand'

class NWSDownloadCommand2(NWSCommand):
    print 'NWSDownloadCommand2'
    NAME = 'CMD2'
    DESCRIPTION = 'This is command2.'
    SUBCOMMANDS = [
        {'name': 'cp', 'command_class': CPCommand},
    ]
    ARG_TABLE = [
        {'name': 'argument-one2', 'positional_arg': True, 'help_text': 'This argument does foo bar.',
         'action': 'store',  'cli_type_name': 'string', },
        {'name': 'argument-two2', 'positional_arg': True, 'help_text': 'This argument does some other thing.',
         'action': 'store', 'choices': ['a', 'b', 'c']},
    ]

class NWSArgParser(argparse.ArgumentParser):
    def __init__(self, command_table, version_string,
                argument_table, prog=None):
        super(NWSArgParser, self).__init__(
            # add_help=False,
            # usage=USAGE
            )
        self._build(command_table, version_string, argument_table)

    def parse_known_args(self, args, namespace=None):
        # print 'parse_known_args'
        # print args
        if len(args) == 1 and args[0] == 'help':
            namespace = argparse.Namespace()
            namespace.help = 'help'
            return namespace, []
        else:
            return super(NWSArgParser, self).parse_known_args(args, namespace)
        # print parsed
        # print remaining
        # terminal_encoding = getattr(sys.stdin, 'encoding', 'utf-8')
        # if terminal_encoding is None:
        #     # In some cases, sys.stdin won't have an encoding set,
        #     # (e.g if it's set to a StringIO).  In this case we just
        #     # default to utf-8.
        #     terminal_encoding = 'utf-8'
        # for arg, value in vars(parsed).items():
        #     if isinstance(value, six.binary_type):
        #         setattr(parsed, arg, value.decode(terminal_encoding))
        #     elif isinstance(value, list):
        #         encoded = []
        #         for v in value:
        #             if isinstance(v, six.binary_type):
        #                 encoded.append(v.decode(terminal_encoding))
        #             else:
        #                 encoded.append(v)
        #         setattr(parsed, arg, encoded)
        # return parsed, remaining

    def _build(self, command_table, version_string, argument_table):
        for argument_name in argument_table:
            argument = argument_table[argument_name]
            argument.add_to_parser(self)

        self.add_argument('command', action=CommandAction,
                               command_table=command_table, nargs='?')

        # parsed_args = self.parse_args()
        # print parsed_args





def main(args=None):
    if args is None:
        args = sys.argv[1:]
    # global arguments
    argument_table = {}
    # example: add one global arg
    arg1 = BaseNWSArgument(name='debug', help_text='print debug info', action='store_true')
    arg1.add_to_arg_table(argument_table)

    command_table = {'cmd1': NWSDownloadCommand1(), 'cmd2': NWSDownloadCommand2()}

    parser = NWSArgParser(command_table=command_table, argument_table=argument_table,version_string='v0.1')

    parsed_args, remaining = parser.parse_known_args(args)

    try:
        # Because _handle_top_level_args emits events, it's possible
        # that exceptions can be raised, which should have the same
        # general exception handling logic as calling into the
        # command table.  This is why it's in the try/except clause.
        # self._handle_top_level_args(parsed_args)
        # self._emit_session_event()
        aa = command_table[parsed_args.command](remaining, parsed_args)
    except Exception as e:
        # sys.stderr.write("usage: %s\n" % USAGE)
        sys.stderr.write(str(e))
        sys.stderr.write("\n")
        return 255

    # argparser = argparse.ArgumentParser()
    #
    # command_table = {'cmd1':'asdf','cmd2':'asdfasdf'}
    #
    # argparser.add_argument('command',action=CommandAction,
    #                   command_table=command_table)



    # argparser.add_argument("-e", "--eee",
    #                     help="Path to ee")
    #
    #
    # subparsers = argparser.add_subparsers(help='sub-command help', dest='subparser_name')
    #
    # parser_a = subparsers.add_parser('command_a', help="command_a help")
    # ## Setup options for parser_a
    # parser_a.add_argument("-f", "--fff",
    #                     help="Path to tarfiles folder. The folder shall has sample_group.json file")
    #
    # parser_b = subparsers.add_parser('command_b', help="command_a help")
    # ## Setup options for parser_a
    # parser_b.add_argument("-f", "--fff",
    #                       help="Path to s")
    #
    #
    # ## Add nargs="*" for zero or more other commands
    # argparser.add_argument('extra', nargs="*", help='Other commands')
    #
    # ## Do similar stuff for other sub-parsers

    # namespace = argparser.parse_args()
    # print namespace
    #

    # extra_namespaces = parse_extra(argparser, namespace)
    # print extra_namespaces

if __name__ == '__main__':
    main()