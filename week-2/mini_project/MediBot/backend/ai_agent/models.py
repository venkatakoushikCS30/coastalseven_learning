from django.db import models

class ChatHistory(models.Model):
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat at {self.timestamp.strftime('%Y-%m-%d %H:%M')}: {self.message[:30]}..."
