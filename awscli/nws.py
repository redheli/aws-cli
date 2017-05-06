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

class NWSArgParser(argparse.ArgumentParser):
    def __init__(self):
        super(NWSArgParser, self).__init__(
            add_help=False,
            usage=USAGE)
        self._build()

    def _build(self):
        command_table = {'cmd1': 'asdf', 'cmd2': 'asdfasdf'}

        self.add_argument('command', action=CommandAction,
                               command_table=command_table)

        namespace = self.parse_args()
        print namespace

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