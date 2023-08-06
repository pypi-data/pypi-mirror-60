import os
import sys
from subprocess import call
from argparse import _SubParsersAction


# call a shell command in subprocess
def shell(command, silent=False):
    if silent:
        with open(os.devnull, 'w') as DEVNULL:
            return call(command, shell=True, stdout=DEVNULL, stderr=DEVNULL) == 0
    else:
        return call(command, shell=True) == 0

# return true if no subparsers match but there is a positional argument
def proxy(parser):
    if not parser._subparsers or not parser._subparsers._actions: return True
    subparsers = next(i for i in parser._subparsers._actions if isinstance(i, _SubParsersAction))
    choices = list(subparsers.choices.keys())
    if len(sys.argv) > 1 and sys.argv and sys.argv[1] not in choices and sys.argv[1] not in ['-h', '--help']:
        print(sys.argv[1])
        return True
