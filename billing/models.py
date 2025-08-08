# Create your models here.
from django.db import models
# from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

class Tarif(models.Model):
    TARIFF_TYPES = [
        ("mm", "Пакет минут"),
        ("que", "Пакет запросов"),
        ("mon", "Подписка на месяц"),
    ]
    t_id = models.AutoField(primary_key=True)
    t_name = models.CharField(max_length=100)
    t_type = models.CharField(max_length=20, choices=TARIFF_TYPES)
    t_quatity = models.IntegerField()  # минуты/сообщения/дней
    t_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.t_name} ({self.t_price} руб.)"

class TarifLog(models.Model):
    tl_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='billing_tarif_logs')
    tl_date = models.DateTimeField(default=timezone.now)
    t_name = models.CharField(max_length=100)
    t_type = models.CharField(max_length=20)
    t_quatity = models.IntegerField()  # Исходное количество единиц
    tl_status = models.BooleanField(default=False)  # активен тариф или нет
    tl_status_pay = models.BooleanField(default=False)  # оплачен ли
    # --- ДОБАВЛЕНО/ИСПРАВЛЕНО: Поле для отслеживания оставшегося количества ---
    # remaining_quantity = models.IntegerField(null=True, blank=True)
    # Или лучше с дефолтным значением:
    remaining_quantity = models.IntegerField(default=0)
    # --- КОНЕЦ ДОБАВЛЕНИЯ ---

    # def save(self, *args, **kwargs):
    #     # --- ДОБАВЛЕНО/ИСПРАВЛЕНО: Установка remaining_quantity при создании ---
    #     if not self.pk:  # Если это новый объект
    #         # Убедимся, что t_quatity не None
    #         if self.t_quatity is not None:
    #             self.remaining_quantity = self.t_quatity
    #         else:
    #             self.remaining_quantity = 0 # Или какое-то другое значение по умолчанию
    #     super().save(*args, **kwargs)
    # # --- КОНЕЦ ДОБАВЛЕНИЯ ---
    def save(self, *args, **kwargs):
        # При создании новой записи устанавливаем remaining_quantity равным t_quatity
        if not self.pk:  # Если это новый объект
            self.remaining_quantity = self.t_quatity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Tariff Log {self.tl_id} for {self.user.username} ({self.t_name})"

class Payment(models.Model):
    p_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='billing_payments')
    p_date = models.DateTimeField(default=timezone.now)
    t_name = models.CharField(max_length=100)
    t_type = models.CharField(max_length=20)
    p_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Новое поле для статуса оплаты
    p_active = models.BooleanField(default=False)
    # --- ДОБАВЛЕНО: Поле для хранения ID платежа от ЮKassa ---
    payment_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    # ----------------------------------------------------------
    def __str__(self):
        return f"Payment {self.p_id} for {self.user.username} ({self.t_name})"

class SessionLog(models.Model):
    s_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='billing_session_logs')
    # Связь с TarifLog для отслеживания списаний
    tarif_log = models.ForeignKey(TarifLog, on_delete=models.CASCADE, null=True, blank=True)
    s_date = models.DateTimeField(default=timezone.now)
    s_status = models.BooleanField(default=False)  # завершена ли сессия
    s_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # списанные рубли
    t_type = models.CharField(max_length=20, null=True, blank=True)  # тип тарифа ("mm", "que", "mon")
    # Количество списанных единиц (минут/сообщений)
    s_quantity = models.IntegerField(default=0)
    # c_id = models.IntegerField(null=False) # <-- Альтернатива, но хуже
    c_id = models.IntegerField(null=True, blank=True)  # Разрешаем NULL и пустые значения

    def __str__(self):
        return f"SessionLog {self.s_id} for {self.user.username}"