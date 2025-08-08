# Create your models here.
from django.db import models
from users.models import User

class SessionLog(models.Model):
    s_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usr_session_logs')
    s_date = models.DateTimeField(auto_now_add=True)
    s_status = models.BooleanField(default=False)  # завершена ли сессия
    s_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # сколько списано
    t_type = models.CharField(max_length=20)  # тип тарифа (mm, que, mon)
    duration = models.IntegerField(default=0)  # в минутах
    messages_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Сессия {self.s_id} ({self.user.email})"