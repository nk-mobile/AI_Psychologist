from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


# Настройка отображения пользователей в админке
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'u_id', 'date_joined', 'is_active')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined', 'last_login')

    # Указываем поля для отображения в форме редактирования
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Персональная информация', {'fields': ('telegram_id',)}),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    # Поля для формы создания нового пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_active', 'is_staff')}
         ),
    )

    ordering = ('email',)  # Сортировка по email


admin.site.register(User, CustomUserAdmin)