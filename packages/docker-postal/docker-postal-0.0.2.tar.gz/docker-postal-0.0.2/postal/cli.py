import sys
import argparse
from . import commands
from postal import settings
from postal.utils import shell


def main():

    # arguments
    help = """Usage: postal [-m mode] launch | up | down | enter [service]
              \nAll unmatched commands are proxied to docker compose"""
    parser = argparse.ArgumentParser(description='A light Docker control tool designed around compose and swarm')
    subparsers = parser.add_subparsers(help=help)

    # commands
    commands.register(subparsers, 'launch', commands.launch)
    commands.register(subparsers, 'enter', commands.enter)
    commands.register(subparsers, 'up', commands.compose, help='[Proxy] Bring docker compose stack up')
    commands.register(subparsers, 'down', commands.compose, help='[Proxy] Bring docker compose stack down')
    commands.register(subparsers, 'logs', commands.compose, help='[Proxy] Show docker logs for service')

    # parse args
    args = parser.parse_args()

    # execute command
    if hasattr(args, 'cmd'):
        sys.exit(args.cmd(args))
    elif len(sys.argv) > 1:
        sys.exit(commands.compose.execute())
    else:
        parser.print_help()
