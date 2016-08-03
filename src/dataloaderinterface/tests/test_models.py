from django.contrib.auth.models import User
from django.test import TestCase

from dataloader.tests.data import data_manager
from dataloaderinterface.tests.test_views import TestAuthentication

models_data = data_manager.test_data['models']['data']


class TestDeviceRegistration(TestCase):
    def create_device_registration(self):
        pass

    def setUp(self):
        self.user = TestAuthentication.create_user()
        self.client.force_login(self.user)

    def test_string_representation(self):
        pass