from django.core.urlresolvers import reverse
from django.test import TestCase

from dataloaderinterface.views import *

# Create your tests here.


class TestDevicesListView(TestCase):
    def test_status(self):
        url = reverse('devices_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_rendering(self):
        return True


class TestDeviceDetailView(TestCase):
    def test_status(self):
        url = reverse('device_detail', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestDeviceRegistrationView(TestCase):
    def test_status(self):
        url = reverse('device_registration')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestDeviceUpdateView(TestCase):
    def test_status(self):
        url = reverse('device_update', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
