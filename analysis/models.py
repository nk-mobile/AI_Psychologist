# Create your models here.
from django.db import models
# from django.contrib.auth.models import User
from django.conf import settings

class ImgTest(models.Model):
    i_id = models.AutoField(primary_key=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    i_path = models.CharField(max_length=255, default="")  # путь к файлу на диске
    i_state = models.CharField(max_length=100)  # эмоция
    i_comment = models.CharField(max_length=500)  # отчёт (до 5 строк)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} — {self.i_state}"
