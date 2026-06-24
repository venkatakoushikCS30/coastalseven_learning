from django.urls import path
from .views import (
    PatientListCreateView, PatientDetailView,
    MedicalRecordListCreateView, MedicalRecordDetailView,
    FollowUpReminderListView, FollowUpReminderUpdateView,
    PrescriptionPDFView, PrescriptionVerifyView, SendPrescriptionEmailView,
    AppointmentRequestView, AppointmentAdminListView, AppointmentAdminUpdateView
)

urlpatterns = [
    path('patients/', PatientListCreateView.as_view(), name='patient-list-create'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),
    path('records/', MedicalRecordListCreateView.as_view(), name='record-list-create'),
    path('records/<int:pk>/', MedicalRecordDetailView.as_view(), name='record-detail'),
    path('reminders/', FollowUpReminderListView.as_view(), name='reminder-list'),
    path('reminders/<int:pk>/', FollowUpReminderUpdateView.as_view(), name='reminder-update'),
    path('records/<int:pk>/pdf/', PrescriptionPDFView.as_view(), name='prescription-pdf'),
    path('records/<int:pk>/send-email/', SendPrescriptionEmailView.as_view(), name='send-prescription-email'),
    path('records/verify/<int:pk>/', PrescriptionVerifyView.as_view(), name='prescription-verify'),
    path('appointments/request/', AppointmentRequestView.as_view(), name='appointment-request'),
    path('appointments/', AppointmentAdminListView.as_view(), name='appointment-admin-list'),
    path('appointments/<int:pk>/', AppointmentAdminUpdateView.as_view(), name='appointment-admin-update'),
]
