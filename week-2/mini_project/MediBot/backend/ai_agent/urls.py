from django.urls import path
from .views import (
    AISummaryView, AISearchView, PatientChatbotView, 
    ChatHistoryListView, AdminAnalyticsView,
    TextToEHRView, VoiceToEHRView
)

urlpatterns = [
    path('ai/summary/', AISummaryView.as_view(), name='ai-summary'),
    path('ai/search/', AISearchView.as_view(), name='ai-search'),
    path('chatbot/', PatientChatbotView.as_view(), name='patient-chatbot'),
    path('chatbot/history/', ChatHistoryListView.as_view(), name='chatbot-history'),
    path('admin/analytics/', AdminAnalyticsView.as_view(), name='admin-analytics'),
    path('ai/text-to-ehr/', TextToEHRView.as_view(), name='text-to-ehr'),
    path('ai/voice-to-ehr/', VoiceToEHRView.as_view(), name='voice-to-ehr'),
]
