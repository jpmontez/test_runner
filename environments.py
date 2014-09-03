import logging
import re
import sys

from keystoneclient.v2_0.client import Client as keystone_client
from neutronclient.v2_0.client import Client as neutron_client
from novaclient.v1_1 import client as nova_client

from .utils import rand_name

LOG = logging.getLogger(__name__)


class Environment(object):

    def __init__(self, username, password, endpoint):
        self.keystone = keystone_client(
            username=username,
            password=password,
            tenant_name=username,
            auth_url=endpoint)

        self.neutron = neutron_client(
            username=username,
            password=password,
            tenant_name=username,
            auth_url=endpoint)

        self.nova = nova_client.Client(
            username=username,
            api_key=password,
            project_id=username,
            auth_url=endpoint)

        self.endpoints = {}
        self.images = []
        self.network = {}
        self.router = {}
        self.users = {}
        self.admin = {'username': username, 'password': password}

    def build(self):
        self.create_guests()
        self.get_endpoints()
        self.get_images()
        self.get_networking()

    def destroy(self):
        LOG.info('Destroying environment')
        if self.guests: map(self.keystone.users.delete, self.guests)
        if self.tenant: self.keystone.tenants.delete(self.tenant)
        if self.network: self.neutron.delete_network(self.network['id'])
        if self.router: self.neutron.delete_router(self.router['id'])

    def create_guests(self, password='secrete'):
        LOG.info('Creating guest users')
        self.tenant = self.keystone.tenants.create(rand_name('guest'))
        self.guests = []
        for _ in range(2):
            user = self.keystone.users.create(name=rand_name('guest'),
                                              password=password,
                                              tenant_id=self.tenant.id)
            user.password = password
            user.tenant_name = self.tenant.name
            self.guests.append(user)

    def get_endpoints(self):
        LOG.info('Fetching endpoints')
        self.endpoints = self.keystone.service_catalog.get_endpoints()

    def get_images(self):
        LOG.info('Fetching image metadata')
        try:
            self.images = [self.nova.images.list().pop() for _ in range(2)]
        except StopIteration as exc:
            raise StopIteration('Insufficient number of images')

    def get_networking(self):
        LOG.info('Fetching networks')

        def _find_resource(resources, name):
            return next(resource for resource in resources
                        if name in resource['name'])

        networks = self.neutron.list_networks()['networks']
        routers = self.neutron.list_routers()['routers']

        self.network = _find_resource(networks, 'private')
        self.router = _find_resource(routers, 'public-private')
