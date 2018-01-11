from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from dataloaderinterface.forms import UserRegistrationForm
from dataloaderinterface.views import *

# Create your tests here.


class TestAuthentication(TestCase):
    @staticmethod
    def get_test_user_data():
        return {
            'username': 'preparetodie', 'password1': 'test_password', 'password2': 'test_password',
            'first_name': 'Inigo', 'last_name': 'Montoya'
        }

    @staticmethod
    def create_user():
        user_data = TestAuthentication.get_test_user_data()
        del user_data['password1']
        del user_data['password2']
        return User.objects.get_or_create(**user_data)[0]

    def setUp(self):
        pass

    def test_valid_registration_form(self):
        form = UserRegistrationForm(data=self.get_test_user_data())
        self.assertTrue(form.is_valid())

    def test_empty_registration_form(self):
        form = UserRegistrationForm(data={})
        self.assertFalse(form.is_valid())

    def test_nonmatching_passwords_registration_form(self):
        data = self.get_test_user_data()
        data['password1'] = '.'
        data['password2'] = '-'
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_registration_view(self):
        redirect_location = reverse('home')
        url = reverse('user_registration')
        response = self.client.post(url, self.get_test_user_data(), follow=True)
        self.assertRedirects(response, expected_url=redirect_location)
        self.assertTrue(User.objects.filter(username=self.get_test_user_data()['username']).exists())

    def test_empty_registration_view(self):
        redirect_location = reverse('home')
        url = reverse('user_registration')
        response = self.client.post(url, {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_logout(self):
        url = reverse('logout')
        user = self.create_user()
        self.client.force_login(user)
        response = self.client.get(url)
        redirect_location = reverse('home')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertRedirects(response, expected_url=redirect_location)

    def tearDown(self):
        user = User.objects.filter(username='preparetodie')
        if user.exists():
            user.delete()


class TestDevicesListView(TestCase):
    def setUp(self):
        self.user = TestAuthentication.create_user()
        self.client.force_login(self.user)

    def test_status(self):
        url = reverse('devices_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_rendering(self):
        pass

    def tearDown(self):
        self.user.delete()


class TestDeviceDetailView(TestCase):
    def setUp(self):
        self.user = TestAuthentication.create_user()
        self.client.force_login(self.user)

    def test_status(self):
        url = reverse('device_detail', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.user.delete()


# class TestDeviceRegistrationView(TestCase):
#     def setUp(self):
#         self.user = TestAuthentication.create_user()
#         self.client.force_login(self.user)
#
#     def test_status(self):
#         url = reverse('device_registration')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#
#     def tearDown(self):
#         self.user.delete()


class TestDeviceUpdateView(TestCase):
    def setUp(self):
        self.user = TestAuthentication.create_user()
        self.client.force_login(self.user)

    def test_status(self):
        url = reverse('device_update', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.user.delete()
