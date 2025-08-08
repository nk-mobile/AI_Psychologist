from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Chat, Message, ChatFeedback


def delete_chat_with_messages(modeladmin, request, queryset):
    """Кастомное действие: удалить чаты вместе со всеми сообщениями"""
    for chat in queryset:
        # Удаляем все сообщения, связанные с этим чатом
        Message.objects.filter(chat=chat).delete()
        # Удаляем сам чат
        chat.delete()
    modeladmin.message_user(request, f"Удалено {queryset.count()} чатов со всеми сообщениями.")


delete_chat_with_messages.short_description = "Удалить выбранные чаты со всеми сообщениями"


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('c_id', 'user', 'c_title', 'c_created', 'c_closed')
    list_filter = ('c_closed', 'c_created')
    search_fields = ('user__email', 'c_title')
    readonly_fields = ('c_created',)
    actions = [delete_chat_with_messages]  # Добавляем кастомное действие


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'user', 'role', 'text_preview', 'created')
    list_filter = ('role', 'created')
    search_fields = ('chat__c_id', 'user__email', 'text')
    readonly_fields = ('created',)

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    text_preview.short_description = 'Текст (превью)'


@admin.register(ChatFeedback)
class ChatFeedbackAdmin(admin.ModelAdmin):
    list_display = ('f_id', 'chat', 'user', 'rating', 'comment_preview', 'created')
    list_filter = ('rating', 'created')
    search_fields = ('chat__c_id', 'user__email', 'comment')
    readonly_fields = ('created',)

    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if obj.comment and len(obj.comment) > 50 else obj.comment

    comment_preview.short_description = 'Комментарий (превью)'