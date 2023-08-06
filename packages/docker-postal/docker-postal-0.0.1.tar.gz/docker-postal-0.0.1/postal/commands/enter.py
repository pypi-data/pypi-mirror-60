import sys
from postal import settings
from postal.utils import shell


help = "Enter a container (using enter script if availiable./)"

def arguments(parser):
    parser.add_argument('container', type=str, help='container to enter')

def main(args):
    ctr = args.container
    bashable = shell(f'docker-compose -p {settings.project} -f {settings.compose} exec {ctr} bash -c ls', silent=True)
    if bashable:
        return shell(f'docker-compose -p {settings.project} -f {settings.compose} exec {ctr} bash /enter.sh $USER $UID')
    return shell(f'docker-compose -p {settings.project} -f {settings.compose} exec {ctr} sh')
