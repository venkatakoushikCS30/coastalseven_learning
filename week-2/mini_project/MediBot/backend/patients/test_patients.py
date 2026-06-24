from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from patients.models import Patient, MedicalRecord, FollowUpReminder, Appointment

User = get_user_model()

class PatientsAPITestCase(APITestCase):
    def setUp(self):
        # Create Doctors
        self.doctor1 = User.objects.create_user(
            username='doctor1', email='doc1@test.com', password='password123', role='DOCTOR',
            specialization='General Practitioner', study='MBBS', available_hours='9 AM - 5 PM'
        )
        self.doctor2 = User.objects.create_user(
            username='doctor2', email='doc2@test.com', password='password123', role='DOCTOR',
            specialization='Dermatologist', study='MD', available_hours='10 AM - 4 PM'
        )
        
        # Create Patient for Doctor 1
        self.patient1 = Patient.objects.create(
            doctor=self.doctor1, name='Alice Smith', age=30, gender='Female'
        )
        
        # Authentication urls & tokens
        self.login_url = reverse('token_obtain_pair')
        self.patient_list_url = reverse('patient-list-create')
        self.record_list_url = reverse('record-list-create')
        
        # Get tokens
        self.token1 = self.get_token('doctor1', 'password123')
        self.token2 = self.get_token('doctor2', 'password123')

    def get_token(self, username, password):
        response = self.client.post(self.login_url, {'username': username, 'password': password})
        return response.data['access']

    def test_doctor_can_only_see_their_patients(self):
        # Doctor 1 queries
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get(self.patient_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Alice Smith')

        # Doctor 2 queries
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        response = self.client.get(self.patient_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_patient(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        data = {
            'name': 'Bob Jones',
            'age': 45,
            'gender': 'Male'
        }
        response = self.client.post(self.patient_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.filter(doctor=self.doctor1).count(), 2)

    def test_create_medical_record_and_auto_followup(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        data = {
            'patient': self.patient1.id,
            'symptoms': 'High fever and body pain for 3 days.',
            'diagnosis': 'Influenza / Viral Infection',
            'prescription': 'Rest and Paracetamol 500mg.',
            'notes': 'Monitor vitals.'
        }
        response = self.client.post(self.record_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that record has a generated summary (mock summary if ollama is off)
        record = MedicalRecord.objects.get(id=response.data['id'])
        self.assertIsNotNone(record.summary)
        
        # Check that follow up was automatically scheduled (mock flow triggers it for 'fever')
        reminders = FollowUpReminder.objects.filter(patient=self.patient1)
        self.assertTrue(reminders.exists())
        self.assertEqual(reminders.first().status, 'PENDING')

    def test_edit_medical_record(self):
        # 1. Create a record first
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        data = {
            'patient': self.patient1.id,
            'symptoms': 'Slight headache.',
            'diagnosis': 'Stress.',
            'prescription': 'Rest.',
            'notes': 'None.'
        }
        res = self.client.post(self.record_list_url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        record_id = res.data['id']
        
        # 2. PATCH to edit it
        detail_url = reverse('record-detail', kwargs={'pk': record_id})
        update_data = {
            'symptoms': 'Severe migraine behind left eye.',
            'diagnosis': 'Acute Migraine Attack',
            'prescription': 'Sumatriptan 50mg.',
            'notes': 'Keep in dark room.'
        }
        patch_res = self.client.patch(detail_url, update_data)
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        
        # 3. Assert values are updated in DB
        record = MedicalRecord.objects.get(id=record_id)
        self.assertEqual(record.symptoms, 'Severe migraine behind left eye.')
        self.assertEqual(record.diagnosis, 'Acute Migraine Attack')
        self.assertEqual(record.prescription, 'Sumatriptan 50mg.')
        self.assertEqual(record.notes, 'Keep in dark room.')

    def test_send_prescription_email(self):
        # 1. Update patient to have an email
        self.patient1.email = 'patient1@test.com'
        self.patient1.save()
        
        # 2. Create medical record
        record = MedicalRecord.objects.create(
            patient=self.patient1,
            symptoms='Fever',
            diagnosis='Cold',
            prescription='Rest',
            notes='Drink water'
        )
        
        # 3. Request send-email
        url = reverse('send-prescription-email', kwargs={'pk': record.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['detail'], 'Prescription successfully emailed to patient1@test.com.')

    def test_send_prescription_email_missing_email(self):
        self.patient1.email = ''
        self.patient1.save()
        
        record = MedicalRecord.objects.create(
            patient=self.patient1,
            symptoms='Fever',
            diagnosis='Cold',
            prescription='Rest',
        )
        
        url = reverse('send-prescription-email', kwargs={'pk': record.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_prescription_email_unauthorized(self):
        self.patient1.email = 'patient1@test.com'
        self.patient1.save()
        record = MedicalRecord.objects.create(
            patient=self.patient1,
            symptoms='Fever',
            diagnosis='Cold',
            prescription='Rest',
        )
        
        url = reverse('send-prescription-email', kwargs={'pk': record.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_text_to_ehr(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('text-to-ehr')
        data = {
            'text': 'Patient has mild fever and cough for 3 days. Diagnose viral infection, suggest paracetamol twice daily.'
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('symptoms', res.data)
        self.assertIn('diagnosis', res.data)
        self.assertIn('prescription', res.data)
        self.assertEqual(res.data['symptoms'], 'Mild fever and cough for 3 days')
        self.assertEqual(res.data['diagnosis'], 'Viral infection')
        self.assertEqual(res.data['prescription'], 'Paracetamol twice daily')

    def test_voice_to_ehr(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('voice-to-ehr')
        
        import tempfile
        import wave
        import struct
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
            temp_name = f.name
            with wave.open(temp_name, 'w') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(44100)
                for _ in range(100):
                    wav.writeframesraw(struct.pack('<h', 0))
                    
        with open(temp_name, 'rb') as f:
            res = self.client.post(url, {'file': f}, format='multipart')
            
        import os
        os.remove(temp_name)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('transcription', res.data)
        self.assertIn('symptoms', res.data)
        self.assertIn('diagnosis', res.data)
        self.assertIn('prescription', res.data)

    def test_incomplete_profile_cannot_perform_operations(self):
        incomplete_doc = User.objects.create_user(
            username='doc_incomplete', email='incomplete@test.com', password='password123', role='DOCTOR'
        )
        token = self.get_token('doc_incomplete', 'password123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.get(self.patient_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        data = {'name': 'Charlie', 'age': 25, 'gender': 'Male'}
        response = self.client.post(self.patient_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AppointmentsAPITestCase(APITestCase):
    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_user(
            username='admin1', email='admin@test.com', password='password123', role='ADMIN'
        )
        
        # Create a doctor user
        self.doctor = User.objects.create_user(
            username='doctor_spec', email='doctor_spec@test.com', password='password123', role='DOCTOR',
            specialization='Neurologist', study='MD', available_hours='10 AM - 2 PM'
        )
        
        # URL routes
        self.login_url = reverse('token_obtain_pair')
        self.request_url = reverse('appointment-request')
        self.admin_list_url = reverse('appointment-admin-list')
        
        # Get tokens
        self.admin_token = self.get_token('admin1', 'password123')
        self.doctor_token = self.get_token('doctor_spec', 'password123')

    def get_token(self, username, password):
        response = self.client.post(self.login_url, {'username': username, 'password': password})
        return response.data['access']

    def test_public_user_can_request_appointment(self):
        data = {
            'patient_name': 'John Doe',
            'patient_email': 'johndoe@test.com',
            'patient_phone': '1234567890',
            'doctor_type': 'Neurologist',
            'notes': 'Prefer afternoon appointment.'
        }
        # No credentials set -> public request
        response = self.client.post(self.request_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)
        
        appt = Appointment.objects.first()
        self.assertEqual(appt.patient_name, 'John Doe')
        self.assertEqual(appt.status, 'PENDING')

    def test_admin_can_view_appointments_doctor_cannot(self):
        Appointment.objects.create(
            patient_name='John Doe', patient_email='johndoe@test.com',
            patient_phone='1234567890', doctor_type='Neurologist'
        )
        
        # Admin can view
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get(self.admin_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Doctor gets empty list (not authorized for admin endpoints)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.doctor_token}')
        response = self.client.get(self.admin_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_admin_can_schedule_and_confirm_appointment(self):
        appt = Appointment.objects.create(
            patient_name='John Doe', patient_email='johndoe@test.com',
            patient_phone='1234567890', doctor_type='Neurologist'
        )
        
        update_url = reverse('appointment-admin-update', kwargs={'pk': appt.id})
        data = {
            'scheduled_date': '2026-06-01',
            'scheduled_day': 'Monday',
            'scheduled_time': '11:00 AM',
            'assigned_doctor': self.doctor.id,
            'status': 'CONFIRMED'
        }
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.patch(update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        appt.refresh_from_db()
        self.assertEqual(appt.status, 'CONFIRMED')
        self.assertEqual(appt.scheduled_day, 'Monday')
        self.assertEqual(appt.assigned_doctor, self.doctor)

    def test_chatbot_form_triggers_only_on_explicit_requests(self):
        chatbot_url = reverse('patient-chatbot')
        
        # Test 1: General inquiry "how to book an appointment" -> should NOT trigger form
        response1 = self.client.post(chatbot_url, {'message': 'How to book an appointment?'})
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertFalse(response1.data['show_appointment_form'])

        # Test 2: Explicit command "book an appointment" -> should trigger form
        response2 = self.client.post(chatbot_url, {'message': 'Book an appointment'})
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertTrue(response2.data['show_appointment_form'])

        # Test 3: Explicit command "i want to schedule appointment" -> should trigger form
        response3 = self.client.post(chatbot_url, {'message': 'i want to schedule appointment'})
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertTrue(response3.data['show_appointment_form'])

    def test_admin_can_clear_chat_history(self):
        from ai_agent.models import ChatHistory
        ChatHistory.objects.create(message="hello", response="hi")
        ChatHistory.objects.create(message="book an appointment", response="filling form")
        
        chat_list_url = reverse('chatbot-history')
        
        # Test 1: Doctor cannot clear
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.doctor_token}')
        response1 = self.client.delete(chat_list_url)
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ChatHistory.objects.count(), 2)
        
        # Test 2: Admin can clear
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response2 = self.client.delete(chat_list_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(ChatHistory.objects.count(), 0)
