import os
import getpass
from postal.settings import project, compose
from postal.utils import shell


help = "Enter a container (using enter script if availiable./)"

def arguments(parser):
    parser.add_argument('container', type=str, help='container to enter')

def main(args):
    user = getpass.getuser()
    uid = os.geteuid()
    container = args.container
    bashable = shell(f'docker-compose -p {project} -f {compose} exec {container} bash -c ls', silent=True)
    if bashable:
        return shell(f'docker-compose -p {project} -f {compose} exec {container} bash /enter.sh {user} {uid}')
    return shell(f'docker-compose -p {project} -f {compose} exec {container} sh')
