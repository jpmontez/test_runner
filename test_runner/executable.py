import argh

from .environments import Environment
from .frameworks import Tempest
from .utils import cleanup, Reporter

LOG = Reporter(__name__).setup()


def main(endpoint, username='admin', password='secrete', test_path='api'):
    environment = Environment(username, password, endpoint)

    with cleanup(environment):
        environment.build()
        framework = Tempest(environment, repo_dir='/opt/tempest',
                            test_path=test_path)
        results = framework.run_tests()
        LOG.info('Results: {0}'.format(results))

argh.dispatch_command(main)
