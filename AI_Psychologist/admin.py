# AI_Psychologist/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

# Импортируем модели, если нужно зарегистрировать их здесь
# from users.models import User
# from chat.models import Chat, Message
# и т.д.

class MyAdminSite(AdminSite):
    site_header = 'Администрирование AI-Психолога'
    site_title = 'AI-Психолог Admin'
    index_title = 'Панель управления'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # Можно добавить кастомные URL здесь
        ]
        return custom_urls + urls

# Создаем экземпляр кастомной админ-панели
admin_site = MyAdminSite(name='myadmin')

# Регистрируем модели в кастомной админке, если нужно
# admin_site.register(User, UserAdmin)
# admin_site.register(Chat)
# и т.д.

# Также можем кастомизировать стандартную админку
admin.site.site_header = 'Администрирование AI-Психолога'
admin.site.site_title = 'AI-Психолог Admin'
admin.site.index_title = 'Панель управления'