import io
from django.http import HttpResponse
from django.views import View
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Patient, MedicalRecord, FollowUpReminder, Appointment
from .serializers import PatientSerializer, MedicalRecordSerializer, FollowUpReminderSerializer, AppointmentSerializer


class IsProfileCompleted(permissions.BasePermission):
    message = "Please complete your profile details (specialization, credentials, and available hours) before performing clinical operations."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.role == 'ADMIN':
            return True
        if user.role == 'DOCTOR':
            if not user.specialization or not user.study or not user.available_hours:
                return False
        return True


class PatientListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfileCompleted]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Patient.objects.all().order_by('-created_at')
        return Patient.objects.filter(doctor=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user)

class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfileCompleted]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Patient.objects.all()
        return Patient.objects.filter(doctor=user)

class MedicalRecordListCreateView(generics.ListCreateAPIView):
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfileCompleted]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return MedicalRecord.objects.all().order_by('-created_at')
        return MedicalRecord.objects.filter(patient__doctor=user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        # Ensure patient belongs to doctor
        patient_id = request.data.get('patient')
        try:
            patient = Patient.objects.get(id=patient_id)
            if request.user.role != 'ADMIN' and patient.doctor != request.user:
                return Response({"detail": "You do not have permission to add records for this patient."}, 
                                status=status.HTTP_403_FORBIDDEN)
        except Patient.DoesNotExist:
            return Response({"detail": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # We will trigger background processing in AI agent after creation
        # (e.g. embed the record, check for follow-up reminders etc.)
        record = serializer.instance
        try:
            from ai_agent.services import handle_new_record_created
            handle_new_record_created(record)
        except Exception as e:
            # Don't fail the HTTP request if RAG indexing fails, but log it
            print("Error triggering AI hooks:", str(e))

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class MedicalRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfileCompleted]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return MedicalRecord.objects.all()
        return MedicalRecord.objects.filter(patient__doctor=user)

    def perform_update(self, serializer):
        serializer.save()
        record = serializer.instance
        try:
            from ai_agent.services import handle_new_record_created
            # This triggers re-generation of summary if needed and updates vector store index
            handle_new_record_created(record)
        except Exception as e:
            print("Error updating AI index:", str(e))

class FollowUpReminderListView(generics.ListAPIView):
    serializer_class = FollowUpReminderSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfileCompleted]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return FollowUpReminder.objects.all().order_by('scheduled_date')
        return FollowUpReminder.objects.filter(patient__doctor=user).order_by('scheduled_date')

class FollowUpReminderUpdateView(generics.UpdateAPIView):
    queryset = FollowUpReminder.objects.all()
    serializer_class = FollowUpReminderSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfileCompleted]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return FollowUpReminder.objects.all()
        return FollowUpReminder.objects.filter(patient__doctor=user)


def generate_prescription_pdf_data(record):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        name='TitleStyle',
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#4f46e5'),
        spaceAfter=5
    )
    subtitle_style = ParagraphStyle(
        name='SubTitleStyle',
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=15
    )
    h2_style = ParagraphStyle(
        name='H2Style',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=6
    )
    normal_style = ParagraphStyle(
        name='NormalCustom',
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#334155'),
        leading=14
    )
    rx_style = ParagraphStyle(
        name='RxStyle',
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#6366f1'),
        spaceAfter=10
    )

    # Header Clinic Branding
    story.append(Paragraph("MediAssist Clinic & Hospital", title_style))
    story.append(Paragraph("123 Health Care Boulevard, Medical District • Phone: +1 (555) 100-2000 • verify@mediassist.com", subtitle_style))
    story.append(Spacer(1, 10))

    # Two Column block for Doctor & Patient details
    doc_fullname = f"Dr. {record.patient.doctor.first_name} {record.patient.doctor.last_name}" if record.patient.doctor.first_name else record.patient.doctor.username
    specialty = record.patient.doctor.specialization or "General Practitioner"
    study = f" ({record.patient.doctor.study})" if record.patient.doctor.study else ""
    doctor_details = f"""
    <b>DOCTOR DETAILS</b><br/>
    Name: {doc_fullname}{study}<br/>
    Specialty: {specialty}<br/>
    License No: LIC-99228-MD
    """
    patient_details = f"""
    <b>PATIENT DETAILS</b><br/>
    Name: {record.patient.name}<br/>
    Age / Gender: {record.patient.age} / {record.patient.gender}<br/>
    Date: {record.created_at.strftime('%Y-%m-%d')}
    """
    
    details_data = [
        [Paragraph(doctor_details, normal_style), Paragraph(patient_details, normal_style)]
    ]
    
    details_table = Table(details_data, colWidths=[250, 250])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('PADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 15))

    # Diagnosis and symptoms
    story.append(Paragraph("Chief Complaints / Presented Symptoms", h2_style))
    story.append(Paragraph(record.symptoms, normal_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Clinical Diagnosis", h2_style))
    story.append(Paragraph(f"<b>{record.diagnosis}</b>", normal_style))
    story.append(Spacer(1, 15))

    # Rx Prescription details
    story.append(Paragraph("Rx", rx_style))
    rx_lines = [line.strip() for line in record.prescription.split('\n') if line.strip()]
    rx_html = "<br/>".join([f"• {line}" for line in rx_lines])
    story.append(Paragraph(rx_html, normal_style))
    story.append(Spacer(1, 15))

    if record.notes:
        story.append(Paragraph("Special Advice / Notes", h2_style))
        story.append(Paragraph(record.notes, normal_style))
        story.append(Spacer(1, 20))

    # Divider before footer
    story.append(Spacer(1, 15))

    # Footer: Signatures and QR Code
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=http://localhost:8000/api/records/verify/{record.id}/"
    
    sig_text = """
    <br/><br/>
    ___________________________<br/>
    <b>Authorized Signature</b><br/>
    MediAssist Medical Board
    """
    
    verification_text = f"""
    <b>PRESCRIPTION VERIFICATION</b><br/>
    Scan the QR code to verify the authenticity of this document or visit:<br/>
    <u>http://localhost:8000/api/records/verify/{record.id}/</u>
    """
    
    try:
        qr_img = Image(qr_url, width=70, height=70)
    except Exception:
        qr_img = Paragraph("[QR CODE PLACEHOLDER]", normal_style)

    footer_data = [
        [qr_img, Paragraph(verification_text, normal_style), Paragraph(sig_text, normal_style)]
    ]
    
    footer_table = Table(footer_data, colWidths=[80, 210, 210])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(footer_table)

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


class PrescriptionPDFView(generics.views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsProfileCompleted]

    def get(self, request, pk):
        try:
            record = MedicalRecord.objects.get(pk=pk)
            # Permission check: Doctor must own the patient profile
            if request.user.role != 'ADMIN' and record.patient.doctor != request.user:
                return Response({"detail": "You do not have permission to view this prescription."}, 
                                status=status.HTTP_403_FORBIDDEN)
        except MedicalRecord.DoesNotExist:
            return Response({"detail": "Medical record not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            pdf_data = generate_prescription_pdf_data(record)
        except ImportError:
            return Response({"detail": "ReportLab library not installed on server."}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"detail": f"Failed to generate PDF: {str(e)}"}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="prescription_{record.id}.pdf"'
        response.write(pdf_data)
        return response


class SendPrescriptionEmailView(generics.views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsProfileCompleted]

    def post(self, request, pk):
        from django.core.mail import EmailMessage
        from django.conf import settings

        try:
            record = MedicalRecord.objects.get(pk=pk)
            # Permission check: Doctor must own the patient profile
            if request.user.role != 'ADMIN' and record.patient.doctor != request.user:
                return Response({"detail": "You do not have permission to access this record."}, 
                                status=status.HTTP_403_FORBIDDEN)
        except MedicalRecord.DoesNotExist:
            return Response({"detail": "Medical record not found."}, status=status.HTTP_404_NOT_FOUND)

        patient = record.patient
        if not patient.email:
            return Response({"detail": "Patient does not have an email address configured. Please edit their profile first."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        doc_fullname = f"Dr. {patient.doctor.first_name} {patient.doctor.last_name}" if patient.doctor.first_name else patient.doctor.username
        subject = f"Prescription Confirmed: Consultation #{record.id} - MediAssist Clinic"
        
        body = f"""Hello {patient.name},
        
Please find the clinical prescription and consultation summary from your visit with {doc_fullname} at MediAssist Clinic below.

Consultation Details:
------------------------------------------
Date: {record.created_at.strftime('%Y-%m-%d')}
Symptoms: {record.symptoms}
Diagnosis: {record.diagnosis}
------------------------------------------

Prescribed Medications (Rx):
------------------------------------------
{record.prescription}
------------------------------------------

Additional Advice / Notes:
{record.notes or 'None'}

Digital Verification:
You can verify this clinical record online by scanning the QR code in the attached PDF or visiting:
http://localhost:8000/api/records/verify/{record.id}/

Thank you,
MediAssist Clinic & Hospital
Phone: +1 (555) 100-2000
"""

        try:
            email_msg = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[patient.email],
            )
            
            # Try to attach PDF prescription
            try:
                pdf_data = generate_prescription_pdf_data(record)
                email_msg.attach(f"prescription_{record.id}.pdf", pdf_data, "application/pdf")
            except (ImportError, Exception) as pdf_err:
                print(f"Warning: Could not attach PDF prescription: {str(pdf_err)}")
                
            email_msg.send(fail_silently=False)
            return Response({"detail": f"Prescription successfully emailed to {patient.email}."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PrescriptionVerifyView(generics.views.View):
    def get(self, request, pk):
        try:
            record = MedicalRecord.objects.get(pk=pk)
            doc_fullname = f"Dr. {record.patient.doctor.first_name} {record.patient.doctor.last_name}" if record.patient.doctor.first_name else record.patient.doctor.username
            patient = record.patient
        except MedicalRecord.DoesNotExist:
            return HttpResponse("<h3>Prescription not found or invalid verification ID.</h3>", status=404)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Prescription Verification | MediAssist AI</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    background-color: #05070c;
                    color: #f8fafc;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    margin: 0;
                    padding: 1.5rem;
                }}
                .verify-card {{
                    background: rgba(15, 23, 42, 0.6);
                    backdrop-filter: blur(16px);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 1.5rem;
                    padding: 2.5rem;
                    max-width: 550px;
                    width: 100%;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.8);
                }}
                .badge {{
                    background-color: rgba(16, 185, 129, 0.1);
                    border: 1px solid rgba(16, 185, 129, 0.3);
                    color: #34d399;
                    font-size: 0.75rem;
                    font-weight: 700;
                    padding: 0.5rem 1rem;
                    border-radius: 9999px;
                    display: inline-flex;
                    align-items: center;
                    gap: 0.5rem;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    margin-bottom: 1.5rem;
                }}
                .badge-dot {{
                    width: 8px;
                    height: 8px;
                    background-color: #34d399;
                    border-radius: 50%;
                    display: inline-block;
                }}
                h1 {{
                    font-size: 1.5rem;
                    font-weight: 800;
                    margin: 0 0 0.5rem 0;
                    background: linear-gradient(135deg, #a5b4fc 0%, #818cf8 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                .subtitle {{
                    color: #94a3b8;
                    font-size: 0.85rem;
                    margin-bottom: 2rem;
                }}
                .section {{
                    border-top: 1px solid rgba(255, 255, 255, 0.05);
                    padding-top: 1.25rem;
                    margin-top: 1.25rem;
                }}
                .section-title {{
                    font-size: 0.7rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    color: #64748b;
                    letter-spacing: 0.05em;
                    margin-bottom: 0.5rem;
                }}
                .grid-2 {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 1rem;
                }}
                .data-label {{
                    color: #94a3b8;
                    font-size: 0.8rem;
                }}
                .data-val {{
                    color: #f1f5f9;
                    font-size: 0.9rem;
                    font-weight: 600;
                    margin-top: 0.2rem;
                }}
                .rx-list {{
                    background: rgba(0, 0, 0, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.03);
                    border-radius: 0.75rem;
                    padding: 1rem;
                    font-size: 0.85rem;
                    line-height: 1.6;
                    color: #cbd5e1;
                    white-space: pre-line;
                }}
            </style>
        </head>
        <body>
            <div class="verify-card">
                <div class="badge">
                    <span class="badge-dot"></span>
                    Verified Authentic
                </div>
                <h1>MediAssist Clinical Record</h1>
                <p class="subtitle">EHR ID: #MED-{record.id} • Digital Verification Portal</p>
                
                <div class="section grid-2">
                    <div>
                        <div class="section-title">Patient Profile</div>
                        <div class="data-val">{patient.name}</div>
                        <div class="data-label">Age: {patient.age} • Gender: {patient.gender}</div>
                    </div>
                    <div>
                        <div class="section-title">Prescribing Doctor</div>
                        <div class="data-val">{doc_fullname}</div>
                        <div class="data-label">{record.patient.doctor.specialization or 'Specialist'} • License: Active</div>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">Diagnosis</div>
                    <div class="data-val" style="color: #818cf8; font-size: 1rem;">{record.diagnosis}</div>
                </div>

                <div class="section">
                    <div class="section-title">Medications (Rx)</div>
                    <div class="rx-list">{record.prescription}</div>
                </div>

                <div class="section" style="text-align: center; color: #64748b; font-size: 0.75rem; margin-top: 2rem;">
                    Generated on {record.created_at.strftime('%B %d, %Y at %H:%M UTC')}<br/>
                    MediAssist AI Verification System
                </div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html_content)


class AppointmentRequestView(generics.CreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.AllowAny]


class AppointmentAdminListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != 'ADMIN':
            return Appointment.objects.none()
        return Appointment.objects.all().order_by('-created_at')


class AppointmentAdminUpdateView(generics.UpdateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != 'ADMIN':
            return Appointment.objects.none()
        return Appointment.objects.all()

    def perform_update(self, serializer):
        from django.core.mail import send_mail
        from django.conf import settings
        original_status = self.get_object().status
        serializer.save()
        updated_appointment = serializer.instance
        
        if original_status != 'CONFIRMED' and updated_appointment.status == 'CONFIRMED':
            self.send_confirmation_email(updated_appointment)

    def send_confirmation_email(self, appointment):
        from django.core.mail import send_mail
        from django.conf import settings
        doctor_name = "Assigned Specialist"
        if appointment.assigned_doctor:
            doctor_name = f"Dr. {appointment.assigned_doctor.first_name} {appointment.assigned_doctor.last_name}".strip()
            if not doctor_name:
                doctor_name = f"Dr. {appointment.assigned_doctor.username}"
        
        subject = f"Appointment Confirmed: MediAssist Clinic"
        body = f"""Hello {appointment.patient_name},

Your appointment request has been scheduled and confirmed!

Details of your appointment:
------------------------------------------
Specialty/Department: {appointment.doctor_type}
Assigned Doctor: {doctor_name}
Date: {appointment.scheduled_date}
Day: {appointment.scheduled_day}
Time: {appointment.scheduled_time}
------------------------------------------

Clinic Address:
123 Health Care Boulevard, Medical District
Phone: +1 (555) 100-2000

Please arrive 10 minutes prior to your scheduled time. If you need to cancel or reschedule, please contact us at least 24 hours in advance.

Thank you,
MediAssist Clinic Administration Team
"""
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[appointment.patient_email],
                fail_silently=False,
            )
            print(f"Appointment confirmation email successfully sent to {appointment.patient_email}.")
        except Exception as e:
            print("Failed to send appointment confirmation email:", str(e))
