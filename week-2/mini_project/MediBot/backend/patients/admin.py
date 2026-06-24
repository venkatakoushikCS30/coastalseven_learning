from django.contrib import admin
from .models import Patient, MedicalRecord, FollowUpReminder, Appointment

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'age', 'gender', 'email', 'doctor', 'created_at')
    list_filter = ('gender', 'doctor', 'created_at')
    search_fields = ('name', 'email')

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'diagnosis', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('patient__name', 'diagnosis', 'symptoms', 'prescription')

@admin.register(FollowUpReminder)
class FollowUpReminderAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'scheduled_date', 'status', 'created_at')
    list_filter = ('status', 'scheduled_date', 'created_at')
    search_fields = ('patient__name', 'reason')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_name', 'patient_email', 'doctor_type', 'assigned_doctor', 'scheduled_date', 'status')
    list_filter = ('status', 'doctor_type', 'scheduled_date', 'created_at')
    search_fields = ('patient_name', 'patient_email', 'patient_phone')
