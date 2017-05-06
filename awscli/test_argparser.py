import argparse


## This function takes the 'extra' attribute from global namespace and re-parses it to create separate namespaces for all other chained commands.
def parse_extra(parser, namespace):
    namespaces = []
    extra = namespace.extra
    while extra:
        n = parser.parse_args(extra)
        extra = n.extra
        namespaces.append(n)

    return namespaces

def main(args=None):
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-e", "--eee",
                        help="Path to ee")


    subparsers = argparser.add_subparsers(help='sub-command help', dest='subparser_name')

    parser_a = subparsers.add_parser('command_a', help="command_a help")
    ## Setup options for parser_a
    parser_a.add_argument("-f", "--fff",
                        help="Path to tarfiles folder. The folder shall has sample_group.json file")

    parser_b = subparsers.add_parser('command_b', help="command_a help")
    ## Setup options for parser_a
    parser_b.add_argument("-f", "--fff",
                          help="Path to s")


    ## Add nargs="*" for zero or more other commands
    argparser.add_argument('extra', nargs="*", help='Other commands')

    ## Do similar stuff for other sub-parsers

    namespace = argparser.parse_args()
    print namespace
    extra_namespaces = parse_extra(argparser, namespace)
    print extra_namespaces

if __name__ == '__main__':
    main()