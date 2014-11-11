import logging
import os

from jinja2 import Template

from .utils import run_cmd, touch

LOG = logging.getLogger(__name__)


class Framework(object):

    def __init__(self, environment):
        self.admin = environment.admin
        self.guests = environment.guests
        self.endpoints = environment.endpoints
        self.images = environment.images
        self.network = environment.network
        self.router = environment.router

    def populate(self):
        raise NotImplementedError


class Tempest(Framework):

    def __init__(self, environment):
        super(Tempest, self).__init__(environment)
        self.populate_config()
        self.install()

    def populate_config(self):
        LOG.info('Building configuration file')
        template = os.path.join(os.path.dirname(__file__),
                                'files/tempest.conf.example')
        with open(template, 'r') as fp:
            sample = fp.read()
            self.config = Template(sample).render(
                admin=self.admin,
                guests=self.guests,
                endpoints=self.endpoints,
                images=self.images,
                network=self.network,
                router=self.router)

        config_path = touch('/etc/tempest', 'tempest.conf')
        with open(config_path, 'w') as fp:
            fp.write(self.config)

    def install(self):
        LOG.info('Installing Tempest')
        src_dir = '/opt/tempest'
        if os.path.exists(src_dir):
            cmd = ['git fetch --all',
                   'git reset --hard origin/master']
            run_cmd('; '.join(cmd), cwd=src_dir)
        else:
            src_url = 'https://github.com/openstack/tempest.git'
            run_cmd('git clone {0} {1}'.format(src_url, src_dir))

        touch('/var/log/tempest', 'tempest.log')

    def run(self):
        LOG.info('Executing tests')
        cmd = ['testr init',
               'testr run tempest.api.identity',
               'testr run --parallel tempest.api.compute',
               'testr run --parallel tempest.api.image',
               'testr run --parallel tempest.api.network']
        run_cmd('; '.join(cmd), cwd='/opt/tempest')
