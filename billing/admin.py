from django.contrib import admin
from .models import Tarif, TarifLog, Payment, SessionLog


@admin.register(Tarif)
class TarifAdmin(admin.ModelAdmin):
    list_display = ('t_id', 't_name', 't_type', 't_quatity', 't_price')
    list_filter = ('t_type',)
    search_fields = ('t_name',)


@admin.register(TarifLog)
class TarifLogAdmin(admin.ModelAdmin):
    list_display = (
    'tl_id', 'user', 't_name', 't_type', 't_quatity', 'remaining_quantity', 'tl_status', 'tl_status_pay', 'tl_date')
    list_filter = ('t_type', 'tl_status', 'tl_status_pay', 'tl_date')
    search_fields = ('user__email', 't_name')
    readonly_fields = ('tl_date',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('p_id', 'user', 't_name', 't_type', 'p_amount', 'p_active', 'p_date')
    list_filter = ('t_type', 'p_active', 'p_date')
    search_fields = ('user__email', 't_name', 'payment_id')
    readonly_fields = ('p_date',)


@admin.register(SessionLog)
class SessionLogAdmin(admin.ModelAdmin):
    list_display = ('s_id', 'user', 'tarif_log', 'chat_link', 't_type', 's_quantity', 's_amount', 's_date')
    list_filter = ('t_type', 's_date')
    search_fields = ('user__email', 'tarif_log__t_name')
    readonly_fields = ('s_date',)

    def chat_link(self, obj):
        if obj.c_id:
            from django.urls import reverse
            from django.utils.html import format_html
            url = reverse('admin:chat_chat_change', args=[obj.c_id])
            return format_html('<a href="{}">Чат {}</a>', url, obj.c_id)
        return "N/A"

    chat_link.short_description = 'Связанный чат'