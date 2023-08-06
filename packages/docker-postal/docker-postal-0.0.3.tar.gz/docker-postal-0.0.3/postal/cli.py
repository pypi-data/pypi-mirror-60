import sys
from argparse import ArgumentParser
from . import commands
from .utils import proxy

def main():

    # arguments
    help = """*All unmatched commands are proxied to docker compose with configured compose file selected*"""
    description = 'A light Docker control tool designed around compose and swarm'
    parser = ArgumentParser(description=description)
    subparsers = parser.add_subparsers(help=help)

    # commands
    commands.register(subparsers, 'launch', commands.launch)
    commands.register(subparsers, 'enter', commands.enter)
    commands.register(subparsers, 'up', commands.compose, help='[Proxy] Bring docker compose stack up')
    commands.register(subparsers, 'down', commands.compose, help='[Proxy] Bring docker compose stack down')
    commands.register(subparsers, 'logs', commands.compose, help='[Proxy] Show docker logs for service')
    commands.register(subparsers, 'help', commands.compose, help='[Proxy] Show docker compose help')

    # proxy
    if proxy(parser): sys.exit(commands.compose.main())

    # parse args
    args = parser.parse_args()

    # execute command
    if hasattr(args, 'cmd'):
        sys.exit(args.cmd(args))
    else:
        parser.print_help()
