#!/usr/bin/env python
import argh

from .environments import Environment
from .frameworks import Tempest
from .utils import cleanup, Reporter

LOG = Reporter(__name__).setup()


def main(username, password, endpoint):
    environment = Environment(username, password, endpoint)

    with cleanup(environment):
        environment.build()

    Tempest(environment).populate_config()

argh.dispatch_command(main)
