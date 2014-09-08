#!/usr/bin/env python
import argh

from .environments import Environment
from .frameworks import Tempest
from .utils import cleanup, Reporter

LOG = Reporter(__name__).setup()


def main(username, password, endpoint, repo_dir='/opt/tempest',
         test_path='api'):
    environment = Environment(username, password, endpoint)

    with cleanup(environment):
        environment.build()
        results = Tempest(environment, repo_dir, test_path).run_tests()
        LOG.info('Results: {0}'.format(results))


argh.dispatch_command(main)
