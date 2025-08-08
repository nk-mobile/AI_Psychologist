from django.contrib import admin
from .models import ImgTest


@admin.register(ImgTest)
class ImgTestAdmin(admin.ModelAdmin):
    list_display = ('i_id', 'user', 'i_state', 'i_comment_preview', 'created_at')
    list_filter = ('created_at', 'i_state')
    search_fields = ('user__email', 'i_state', 'i_comment')
    readonly_fields = ('created_at', 'i_path')

    def i_comment_preview(self, obj):
        return obj.i_comment[:50] + '...' if len(obj.i_comment) > 50 else obj.i_comment

    i_comment_preview.short_description = 'Отчет (превью)'