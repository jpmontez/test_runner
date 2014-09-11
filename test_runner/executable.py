#!/usr/bin/env python
import argh

from .environments import Environment
from .frameworks import Tempest
from .utils import cleanup, Reporter

LOG = Reporter(__name__).setup()


def main(username='admin', password='secrete',
         endpoint='http://localhost:5000/v2.0'):

    environment = Environment(username, password, endpoint)

    with cleanup(environment):
        environment.build()
        Tempest(environment).populate_config()

argh.dispatch_command(main)
