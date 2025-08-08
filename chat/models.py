from django.db import models
# from django.contrib.auth.models import User
from django.conf import settings
from asgiref.sync import sync_to_async

class Chat(models.Model):
    c_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_chat')
    c_title = models.CharField(max_length=255, default="Новая сессия")
    c_created = models.DateTimeField(auto_now_add=True)
    c_date = models.DateTimeField(null=True)
    c_closed = models.BooleanField(default=False)
    is_free_session = models.BooleanField(default=False)
    free_limit_reached = models.BooleanField(default=False)

    def __str__(self):
        return f"Чат {self.c_id} ({self.user.username})"


class Message(models.Model):
    m_id = models.AutoField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[("user", "Пользователь"), ("assistant", "ИИ")])
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.text[:30]}"


class ChatFeedback(models.Model):
    f_id = models.AutoField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, blank=True)  # 1-5
    comment = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
