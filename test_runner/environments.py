import logging
import re
import sys

from glanceclient.v1.client import Client as glance_client
from keystoneclient.v2_0.client import Client as keystone_client
from neutronclient.v2_0.client import Client as neutron_client
from novaclient.v1_1 import client as nova_client

from .utils import rand_name

LOG = logging.getLogger(__name__)

CIRROS_URL='http://download.cirros-cloud.net/0.3.3/cirros-0.3.3-x86_64-disk.img'


class Environment(object):

    def __init__(self, username, password, auth_url):
        self.keystone = keystone_client(
            username=username,
            password=password,
            tenant_name=username,
            auth_url=auth_url)

        self.endpoints = self.keystone.service_catalog.get_endpoints()
        self.token = self.keystone.auth_ref['token']['id']

        self.glance = glance_client(
            endpoint=self.endpoints['image'][0]['internalURL'],
            token=self.token)

        self.neutron = neutron_client(
            username=username,
            password=password,
            tenant_name=username,
            auth_url=auth_url,
            endpoint_type='internalURL')

        self.nova = nova_client.Client(
            username=username,
            api_key=password,
            project_id=username,
            auth_url=auth_url,
            endpoint_type='internalURL')

        self.images = []
        self.network = {}
        self.router = {}
        self.users = {}
        self.admin = {'username': username, 'password': password}

    def build(self):
        self.create_guests()
        self.get_images()
        self.get_network()
        self.get_router()

    def destroy(self):
        LOG.info('Destroying environment')
        if self.guests: map(self.keystone.users.delete, self.guests)
        if self.tenant: self.keystone.tenants.delete(self.tenant)
        if self.role: self.keystone.roles.delete(self.role)
        if.self.images: map(self.glance.images.delete, self.images)

    def create_guests(self, password='secrete'):
        LOG.info('Creating guest users')
        self.tenant = self.keystone.tenants.create(rand_name('guest'))

        try:
            self.role = self.keystone.roles.create('Member')
        except Exception as exc:
            LOG.info('Member role already exists')

        self.guests = []
        for _ in range(2):
            user = self.keystone.users.create(name=rand_name('guest'),
                                              password=password,
                                              tenant_id=self.tenant.id)
            user.password = password
            user.tenant_name = self.tenant.name
            self.guests.append(user)

    def get_images(self):
        LOG.info('Fetching image metadata')
        try:
            filters = {'name': 'cirros'}
            image = next(self.glance.images.list(filters=filters))
            self.images = [image, image]
        except StopIteration:
            image = self.glance.images.create(
                name='cirros',
                disk_format='qcow2',
                container_format='bare',
                location=CIRROS_URL,
                is_public='True')
            self.images = [image, image]

    @staticmethod
    def _find_resource(resources, name):
        return next(resource for resource in resources
                    if name in resource['name'])

    def get_network(self):
        LOG.info('Fetching networks')
        networks = self.neutron.list_networks()['networks']
        self.network = self._find_resource(networks, 'private')

    def get_router(self):
        LOG.info('Fetching routers')
        routers = self.neutron.list_routers()['routers']
        self.router = self._find_resource(routers, 'public-private')
