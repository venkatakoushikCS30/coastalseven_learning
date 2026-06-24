import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from patients.models import Patient, MedicalRecord, FollowUpReminder

User = get_user_model()

def seed():
    print("Seeding database...")
    
    # 1. Create Admin
    if not User.objects.filter(username="admin").exists():
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@mediassist.com",
            password="adminpass",
            role="ADMIN",
            first_name="System",
            last_name="Administrator"
        )
        print("Admin user created: admin / adminpass")
    else:
        print("Admin user already exists.")
        
    # 2. Create Doctor
    if not User.objects.filter(username="doctor1").exists():
        doctor = User.objects.create_user(
            username="doctor1",
            email="doctor1@mediassist.com",
            password="doctorpass",
            role="DOCTOR",
            first_name="John",
            last_name="Doe"
        )
        print("Doctor user created: doctor1 / doctorpass")
    else:
        doctor = User.objects.get(username="doctor1")
        print("Doctor user already exists.")

    # 3. Create Sample Patient & Record
    if not Patient.objects.filter(name="Alice Smith").exists():
        patient = Patient.objects.create(
            doctor=doctor,
            name="Alice Smith",
            age=34,
            gender="Female"
        )
        print(f"Sample patient created: {patient.name}")

        record = MedicalRecord.objects.create(
            patient=patient,
            symptoms="High fever (101.5 F), persistent dry cough, sore throat, and body aches for 2 days. Feeling fatigued.",
            diagnosis="Acute Viral Fever & Mild Respiratory Infection",
            prescription="Paracetamol 650mg - 1 tablet three times a day after meals for 3 days.\nCough Syrup - 10ml twice a day for 5 days.\nRest and hydration (3L water daily).",
            notes="Patient reports no history of asthma or drug allergies. Advised to stay isolated for 3 days.",
            summary="Patient presenting with high fever, dry cough, and sore throat for 2 days. Diagnosed with acute viral fever. Prescribed Paracetamol and Cough Syrup, with instructions for rest and hydration."
        )
        print(f"Sample medical record created for {patient.name}")
        
        # Manually trigger RAG indexing for seeded record if ChromaDB is available
        try:
            from ai_agent.services import index_medical_record
            index_medical_record(record)
        except Exception as e:
            print("Could not index seeded record in ChromaDB:", str(e))
    else:
        print("Sample patient Alice Smith already exists.")

    print("Seeding complete successfully!")

if __name__ == "__main__":
    seed()
