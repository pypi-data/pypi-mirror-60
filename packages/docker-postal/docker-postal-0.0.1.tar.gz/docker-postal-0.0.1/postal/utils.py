import os
from subprocess import call


def shell(command, silent=False):
    if silent:
        with open(os.devnull, 'w') as DEVNULL:
            return call(command, shell=True, stdout=DEVNULL, stderr=DEVNULL) == 0
    else:
        return call(command, shell=True) == 0
