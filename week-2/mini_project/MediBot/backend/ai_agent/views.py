from rest_framework import views, permissions, status
from rest_framework.response import Response
from .models import ChatHistory
from .services import (
    generate_record_summary, search_medical_records, query_patient_chatbot,
    transcribe_audio_file, extract_ehr_from_text
)
from patients.models import Patient, MedicalRecord, FollowUpReminder
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class AISummaryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        symptoms = request.data.get('symptoms', '')
        diagnosis = request.data.get('diagnosis', '')
        prescription = request.data.get('prescription', '')
        notes = request.data.get('notes', '')
        
        if not symptoms and not diagnosis:
            return Response({"detail": "Symptoms or Diagnosis must be provided to generate a summary."}, 
                            status=status.HTTP_400_BAD_REQUEST)
                            
        summary = generate_record_summary(symptoms, diagnosis, prescription, notes)
        return Response({"summary": summary}, status=status.HTTP_200_OK)

class AISearchView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        query = request.data.get('query', '')
        if not query:
            return Response({"detail": "Search query must be provided."}, 
                            status=status.HTTP_400_BAD_REQUEST)
                            
        doctor_id = request.user.id
        
        # Log to debug.log
        import datetime
        from django.conf import settings
        log_path = os.path.join(settings.BASE_DIR, 'debug.log')
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n--- {datetime.datetime.now()} ---\n")
            f.write(f"Query: {query}, User: {request.user.username} (ID: {doctor_id})\n")
            
        try:
            results = search_medical_records(query, doctor_id)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"Results successfully returned: {len(results)} items\n")
        except Exception as e:
            import traceback
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"Error occurred: {str(e)}\n{traceback.format_exc()}\n")
            results = []
            
        return Response({"results": results}, status=status.HTTP_200_OK)

class PatientChatbotView(views.APIView):
    permission_classes = [permissions.AllowAny] # Chatbot is public-facing

    def post(self, request):
        message = request.data.get('message', '')
        if not message:
            return Response({"detail": "Message must be provided."}, 
                            status=status.HTTP_400_BAD_REQUEST)
                            
        response_text = query_patient_chatbot(message)
        
        # Save to ChatHistory
        ChatHistory.objects.create(message=message, response=response_text)
        
        # Check if patient wants to book an appointment
        lower_msg = message.lower()
        show_form = False
        if any(phrase in lower_msg for phrase in ["book an appointment", "book appointment", "book an appoint", "schedule an appointment", "schedule appointment"]):
            if not any(q in lower_msg for q in ["how to", "how do", "how can", "where do", "what is"]):
                show_form = True
        
        return Response({
            "message": message,
            "response": response_text,
            "show_appointment_form": show_form
        }, status=status.HTTP_200_OK)

class ChatHistoryListView(views.APIView):
    # Only Admin can view chat logs
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'ADMIN':
            return Response({"detail": "Only admins can view chat logs."}, 
                            status=status.HTTP_403_FORBIDDEN)
            
        history = ChatHistory.objects.all().order_by('-timestamp')[:50]
        data = [{
            "id": h.id,
            "message": h.message,
            "response": h.response,
            "timestamp": h.timestamp
        } for h in history]
        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request):
        if request.user.role != 'ADMIN':
            return Response({"detail": "Only admins can clear chat logs."}, 
                            status=status.HTTP_403_FORBIDDEN)
            
        ChatHistory.objects.all().delete()
        return Response({"message": "Chat history logs cleared successfully."}, status=status.HTTP_200_OK)

class AdminAnalyticsView(views.APIView):
    # Admin metrics endpoint
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'ADMIN':
            return Response({"detail": "Only admins can view system analytics."}, 
                            status=status.HTTP_403_FORBIDDEN)
                            
        total_doctors = User.objects.filter(role='DOCTOR').count()
        total_patients = Patient.objects.count()
        total_records = MedicalRecord.objects.count()
        total_chats = ChatHistory.objects.count()
        total_reminders = FollowUpReminder.objects.count()
        pending_reminders = FollowUpReminder.objects.filter(status='PENDING').count()
        
        # Calculate daily consults count (simple grouping)
        import datetime
        today = datetime.date.today()
        recent_consults = []
        for i in range(7):
            d = today - datetime.timedelta(days=i)
            count = MedicalRecord.objects.filter(created_at__date=d).count()
            recent_consults.append({
                "date": d.strftime("%m/%d"),
                "consultations": count
            })
        recent_consults.reverse()

        return Response({
            "total_doctors": total_doctors,
            "total_patients": total_patients,
            "total_records": total_records,
            "total_chats": total_chats,
            "total_reminders": total_reminders,
            "pending_reminders": pending_reminders,
            "consultation_trends": recent_consults
        }, status=status.HTTP_200_OK)

class TextToEHRView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        text = request.data.get('text', '')
        if not text:
            return Response({"detail": "Text content must be provided."}, 
                            status=status.HTTP_400_BAD_REQUEST)
                            
        data = extract_ehr_from_text(text)
        return Response(data, status=status.HTTP_200_OK)

class VoiceToEHRView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if 'file' not in request.FILES:
            return Response({"detail": "Audio file must be uploaded under key 'file'."}, 
                            status=status.HTTP_400_BAD_REQUEST)
                            
        audio_file = request.FILES['file']
        
        # Save temp audio file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name

        try:
            transcribed_text = transcribe_audio_file(temp_path)
            # Remove temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if transcribed_text.startswith("Error:"):
                return Response({"detail": transcribed_text}, status=status.HTTP_400_BAD_REQUEST)
                
            data = extract_ehr_from_text(transcribed_text)
            data['transcription'] = transcribed_text
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return Response({"detail": f"Voice processing failed: {str(e)}"}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
