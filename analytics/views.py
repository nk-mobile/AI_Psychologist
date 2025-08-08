# analytics/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
# Импортируем Sum и Avg напрямую
from django.db.models import Count, Avg, Sum
from users.models import User
from chat.models import Chat, Message
from analysis.models import ImgTest
from billing.models import Payment, Tarif, TarifLog


def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def analytics_dashboard(request):
    # Статистика пользователей
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()

    # Статистика чатов
    total_chats = Chat.objects.count()
    closed_chats = Chat.objects.filter(c_closed=True).count()

    # Статистика сообщений
    total_messages = Message.objects.count()

    # Статистика анализов
    total_analyses = ImgTest.objects.count()

    # Статистика оплат
    total_payments = Payment.objects.count()
    # Используем Sum напрямую, без префикса models.
    total_payment_amount = Payment.objects.aggregate(
        total=Sum('p_amount')
    )['total'] or 0

    # Средняя длительность чатов (по количеству сообщений)
    # Используем Avg напрямую, без префикса models.
    avg_messages_per_chat = Chat.objects.annotate(
        msg_count=Count('messages')
    ).aggregate(avg=Avg('msg_count'))['avg']

    # Популярность платных планов
    popular_tariffs = TarifLog.objects.values(
        't_name'
    ).annotate(
        count=Count('t_name')
    ).order_by('-count')

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_chats': total_chats,
        'closed_chats': closed_chats,
        'total_messages': total_messages,
        'total_analyses': total_analyses,
        'total_payments': total_payments,
        'total_payment_amount': total_payment_amount,
        'avg_messages_per_chat': round(avg_messages_per_chat or 0, 2),
        'popular_tariffs': popular_tariffs,
    }

    return render(request, 'analytics/dashboard.html', context)

# ... (остальные views, если есть) ...