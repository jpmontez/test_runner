#!/usr/bin/env python
import argparse

from .environments import Environment
from .frameworks import Tempest
from .utils import cleanup

ARGS = argparse.ArgumentParser(description='Tempest runner')
ARGS.add_argument(
    '-u', '--username', required=True,
    help='Administrative username')
ARGS.add_argument(
    '-p', '--password', required=True,
    help='Administrative password')
ARGS.add_argument(
    '-e', '--endpoint', required=True,
    help='Keystone URL endpoint')
ARGS.add_argument(
    '-v', '--verbose', action='count', dest='level',
    default=1, help='Verbose logging (repeat for more verbose)')
ARGS.add_argument(
    '-q', '--quiet', action='store_const', const=0, dest='level',
    default=1, help='Quiet logging (opposite of --verbose)')


def main():
    args = ARGS.parse_args()

    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    logging.basicConfig(level=levels[min(args.level, len(levels)-1)])

    environment = Environment(args.username, args.password, args.endpoint)

    with cleanup(environment):
        environment.build()

    Tempest(environment).populate_config()


if __name__ == '__main__':
    main()
