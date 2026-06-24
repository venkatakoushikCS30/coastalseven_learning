from rest_framework import serializers
from .models import Patient, MedicalRecord, FollowUpReminder, Appointment

class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = '__all__'

class FollowUpReminderSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    
    class Meta:
        model = FollowUpReminder
        fields = '__all__'

class PatientSerializer(serializers.ModelSerializer):
    records = MedicalRecordSerializer(many=True, read_only=True)
    reminders = FollowUpReminderSerializer(many=True, read_only=True)
    doctor_name = serializers.CharField(source='doctor.username', read_only=True)

    class Meta:
        model = Patient
        fields = ('id', 'doctor', 'doctor_name', 'name', 'age', 'gender', 'email', 'created_at', 'records', 'reminders')
        read_only_fields = ('doctor',)

class AppointmentSerializer(serializers.ModelSerializer):
    assigned_doctor_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'

    def get_assigned_doctor_name(self, obj):
        if obj.assigned_doctor:
            full_name = f"Dr. {obj.assigned_doctor.first_name} {obj.assigned_doctor.last_name}".strip()
            return full_name if full_name else f"Dr. {obj.assigned_doctor.username}"
        return None
