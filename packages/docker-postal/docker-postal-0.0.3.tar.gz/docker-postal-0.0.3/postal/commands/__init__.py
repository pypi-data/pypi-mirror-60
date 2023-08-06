from . import launch
from . import enter
from . import compose


def register(subparsers, name, command, help=None):
    parser = subparsers.add_parser(name, help=help or command.help)
    parser.set_defaults(cmd=command.main)
    command.arguments(parser)
