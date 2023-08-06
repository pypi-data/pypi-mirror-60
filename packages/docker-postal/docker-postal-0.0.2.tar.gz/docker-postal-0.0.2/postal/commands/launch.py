from postal import settings
from postal.utils import shell


help = "Rebuild and restart stack"

def arguments(parser):
    pass

def main(args):
    shell(f'docker-compose -p {settings.project} -f {settings.compose} down --remove-orphans')
    shell(f'docker-compose -p {settings.project} -f {settings.compose} build')
    shell(f'docker-compose -p {settings.project} -f {settings.compose} up -d --force-recreate')
