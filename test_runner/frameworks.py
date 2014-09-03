import json
import logging
import os
import requests

from jinja2 import Template
from os.path import abspath, dirname, exists, join

from .utils import run_cmd

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

    def __init__(self, environment, repo_dir, test_path):
        super(Tempest, self).__init__(environment)
        self.repo_dir = repo_dir
        self.test_path = test_path
        self.populate_config()

    def populate_config(self):
        LOG.info('Building configuration file')

        template_dir = join(abspath(dirname(__file__)), 'files/')

        with open(join(template_dir, 'tempest.conf.example'), 'r') as fp:
            sample = fp.read()

        self.config = Template(sample).render(
            admin=self.admin,
            guests=self.guests,
            endpoints=self.endpoints,
            images=self.images,
            network=self.network,
            router=self.router)

        with open('/etc/tempest/tempest.conf', 'w') as fp:
            fp.write(self.config)

    def run_tests(self):
        LOG.info('Running Tempest tests')

        tests_dir = join(self.repo_dir, 'tempest/', self.test_path)
        exclude_dir = join(self.repo_dir, 'tempest/api/identity/admin/v3')
        results_file = '/tmp/results.json'

        command = ('python -u `which nosetests` --where={0}'
                   ' --exclude-dir={1}'
                   ' --with-json --json-file={2}')

        run_cmd(command.format(tests_dir, exclude_dir, results_file))

        with open(results_file, 'r') as fp:
            return json.dumps(json.load(fp), sort_keys=True, indent=2,
                              separators=(',', ': '))
