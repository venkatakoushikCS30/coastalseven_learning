from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class UserRoleTestCase(TestCase):
    def test_create_doctor(self):
        doctor = User.objects.create_user(
            username='dr_test',
            email='dr@test.com',
            password='testpassword',
            role='DOCTOR'
        )
        self.assertEqual(doctor.role, 'DOCTOR')
        self.assertFalse(doctor.is_staff)

    def test_create_admin(self):
        admin = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='testpassword',
            role='ADMIN'
        )
        self.assertEqual(admin.role, 'ADMIN')
        self.assertTrue(admin.is_superuser)


class AuthAPITestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth_register')
        self.login_url = reverse('token_obtain_pair')
        self.doctor_data = {
            'username': 'dr_john',
            'email': 'john@test.com',
            'password': 'password123',
            'role': 'DOCTOR',
            'first_name': 'John',
            'last_name': 'Doe'
        }

    def test_register_doctor(self):
        response = self.client.post(self.register_url, self.doctor_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], 'dr_john')
        self.assertEqual(response.data['user']['role'], 'DOCTOR')

    def test_login_doctor(self):
        # Register first
        self.client.post(self.register_url, self.doctor_data)
        
        # Try login
        login_data = {
            'username': 'dr_john',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['role'], 'DOCTOR')
        self.assertEqual(response.data['first_name'], 'John')

    def test_get_profile_unauthenticated(self):
        profile_url = reverse('user-profile')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_authenticated(self):
        self.client.post(self.register_url, self.doctor_data)
        login_data = {
            'username': 'dr_john',
            'password': 'password123'
        }
        login_response = self.client.post(self.login_url, login_data)
        access_token = login_response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_url = reverse('user-profile')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'dr_john')
        self.assertEqual(response.data['specialization'], '')
        self.assertEqual(response.data['study'], '')
        self.assertEqual(response.data['available_hours'], '')

    def test_update_profile_authenticated(self):
        self.client.post(self.register_url, self.doctor_data)
        login_data = {
            'username': 'dr_john',
            'password': 'password123'
        }
        login_response = self.client.post(self.login_url, login_data)
        access_token = login_response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_url = reverse('user-profile')
        update_data = {
            'specialization': 'Neurologist',
            'study': 'MBBS, FRCS',
            'available_hours': '10:00 AM - 6:00 PM'
        }
        response = self.client.put(profile_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['specialization'], 'Neurologist')
        self.assertEqual(response.data['study'], 'MBBS, FRCS')
        self.assertEqual(response.data['available_hours'], '10:00 AM - 6:00 PM')
