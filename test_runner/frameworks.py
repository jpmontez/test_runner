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

    def __init__(self, environment):
        super(Tempest, self).__init__(environment)

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

        with open('tempest.conf', 'w') as fp:
            fp.write(self.config)
