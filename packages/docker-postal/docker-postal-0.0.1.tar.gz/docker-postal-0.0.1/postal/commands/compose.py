import sys
from postal import settings
from postal.utils import shell


help = "Proxy a docker compose command"

def arguments(parser):
    pass

def main(args):
    sys.exit(shell(f'docker-compose -p {settings.project} -f {settings.compose} {" ".join(sys.argv[1:])}'))
