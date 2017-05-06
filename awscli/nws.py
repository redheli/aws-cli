import sys
import argparse

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
    def __init__(self, name, documentation, action=None):
        self._name = name
        self._documentation = documentation
        self._action = action

    def add_to_arg_table(self, argument_table):
        argument_table[self.arg_name] = self

    @property
    def arg_name(self):
        return '--' + self._name

    @property
    def documentation(self):
        return self._documentation

    def add_to_parser(self, parser):
        parser.add_argument(self.arg_name,
                            help=self.documentation,
                            action=self._action)


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
    @property
    def name(self):
        # Subclasses must implement a name.
        raise NotImplementedError("name")

class NWSDownloadCommand1(NWSCommand):
    def __call__(self, args, parsed_globals):
        print 'NWSDownloadCommand1'
        print args
        print parsed_globals

class NWSDownloadCommand2(NWSCommand):
    def __call__(self, args, parsed_globals):
        print 'NWSDownloadCommand2'
        print args
        print parsed_globals

class NWSArgParser(argparse.ArgumentParser):
    def __init__(self):
        super(NWSArgParser, self).__init__(
            # add_help=False,
            # usage=USAGE
            )
        self._build()

    def _build(self):
        # global arguments
        argument_table = {}
        # example: add one global arg
        arg1 = BaseNWSArgument(name='debug',documentation='print debug info',action='store_true')
        arg1.add_to_arg_table(argument_table)

        for argument_name in argument_table:
            argument = argument_table[argument_name]
            argument.add_to_parser(self)

        command_table = {'cmd1': NWSDownloadCommand1(), 'cmd2': NWSDownloadCommand2() }

        self.add_argument('command', action=CommandAction,
                               command_table=command_table)

        parsed_args = self.parse_args()
        print parsed_args

        try:
            # Because _handle_top_level_args emits events, it's possible
            # that exceptions can be raised, which should have the same
            # general exception handling logic as calling into the
            # command table.  This is why it's in the try/except clause.
            # self._handle_top_level_args(parsed_args)
            # self._emit_session_event()
            aa = command_table[parsed_args.command]('remaining', parsed_args)
        except Exception as e:
            # sys.stderr.write("usage: %s\n" % USAGE)
            sys.stderr.write(str(e))
            sys.stderr.write("\n")
            return 255

def main(args=None):
    nws_arg_parser = NWSArgParser()
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