from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt # Лучше передавать токен, но оставим для совместимости
import json
from .models import Chat, Message
import datetime
from billing.views import check_active_tariff

# chat/views.py
from django.contrib import messages  # <-- Импортируем messages
# Импортируем нужные модели из billing
from billing.models import TarifLog

@login_required
def chat_room(request):
    """Основная страница чата с ИИ"""

    # Ищем незакрытый чат пользователя
    chat = Chat.objects.filter(user=request.user, c_closed=False).first()

    # Обработка создания нового чата с темой через POST
    if request.method == "POST" and "new_chat" in request.POST:
        # --- ИЗМЕНЕНО/ДОБАВЛЕНО: Проверка наличия и достаточности средств с учетом срока подписки ---
        active_tariff = TarifLog.objects.filter(
            user=request.user,
            tl_status=True,       # Тариф активен
            tl_status_pay=True    # Тариф оплачен
        ).first()

        is_valid_tariff = False
        if active_tariff:
            if active_tariff.t_type == "mon":
                # Для подписки проверяем срок действия
                # Предполагаем, что t_quatity хранит количество дней
                expiry_date = active_tariff.tl_date + timedelta(days=active_tariff.t_quatity)
                if timezone.now() < expiry_date:
                    # Подписка действует по времени
                    is_valid_tariff = True
                # else: подписка истекла по времени, is_valid_tariff остаётся False
            else:
                # Для других типов тарифов проверяем remaining_quantity
                if active_tariff.remaining_quantity is not None and active_tariff.remaining_quantity > 0:
                    is_valid_tariff = True
                # else: закончились средства, is_valid_tariff остаётся False

        if not is_valid_tariff:
            messages.error(request, "Недостаточно средств или истёк срок подписки. Пополните баланс для создания нового чата.")
            return redirect("chat_room")
        # --- КОНЕЦ ИЗМЕНЕНИЯ/ДОБАВЛЕНИЯ ---

        title = request.POST.get("chat_title", "").strip()
        if not title:
            title = "Новая сессия"

        # Если есть активный чат, закрываем его
        if chat:
            chat.c_closed = True
            chat.save()

        # Создаем новый чат с темой
        # Предполагаем, что чат платный, так как тариф проверен
        chat = Chat.objects.create(
            user=request.user,
            c_title=title,
            c_closed=False,
            is_free_session=False  # Поскольку тариф проверен, это платный чат
        )
        # Перенаправляем, чтобы избежать повторной отправки формы при F5
        return redirect("chat_room")

    # Подготавливаем данные для шаблона
    chat_messages = []
    if chat:
        # Получаем сообщения для существующего чата, отсортированные по времени создания
        messages_queryset = Message.objects.filter(chat=chat).order_by('created')
        # Преобразуем QuerySet в список словарей для передачи в шаблон как JSON
        chat_messages = [
            {
                'user': msg.role,  # 'user' или 'assistant'
                'text': msg.text
            }
            for msg in messages_queryset
        ]

    # Преобразуем список сообщений в JSON строку для передачи в JavaScript
    messages_json = json.dumps(chat_messages)

    return render(request, "chat/chat.html", {
        "chat": chat,
        "messages_json": messages_json
    })


# ... (остальные views остаются без изменений, если они не требуют обновлений) ...

# ... (остальные views остаются без изменений) ...

@login_required
def chat_history(request):
    """История чатов"""
    chats = Chat.objects.filter(user=request.user, c_closed=True).order_by("-c_created")
    chat_id = request.GET.get("chat_id")
    selected_chat = None
    messages = []
    if chat_id:
        selected_chat = get_object_or_404(Chat, pk=chat_id, user=request.user)
        messages = Message.objects.filter(chat=selected_chat).order_by("created")
    return render(request, "chat/chat_history.html", {
        "chats": chats,
        "selected_chat": selected_chat,
        "messages": messages
    })

def check_free_session(chat):
    """Проверка бесплатного лимита"""
    if chat.is_free_session and not chat.free_limit_reached:
        messages_count = chat.messages.count()
        # Используем aware datetime
        duration = (datetime.datetime.now(datetime.timezone.utc) - chat.c_created).total_seconds() // 60
        if messages_count >= 10 or duration >= 5:
            chat.free_limit_reached = True
            chat.c_closed = True
            chat.save()
            return False
    return True


@login_required
@csrf_exempt  # Лучше передавать CSRF токен через fetch
def close_chat_session(request, chat_id):
    """
    Закрытие чата и расчёт тарифа.
    """
    if request.method != "POST":
        # Возвращаем ошибку, если не POST
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    chat = get_object_or_404(Chat, c_id=chat_id, user=request.user)

    if chat.c_closed:
        # Уже закрыт
        return JsonResponse({"status": "already_closed"})

    chat.c_closed = True
    chat.save()

    # === Расчёт списания (если нужно) ===
    # t_type = get_user_tarif_type(request.user)
    # duration, messages_count = calculate_chat_usage(chat)
    # s_amount = calculate_payment(t_type, duration, messages_count)

    # Запись в session_log
    # SessionLog.objects.create(
    #     user=request.user,
    #     t_type=t_type,
    #     duration=duration,
    #     messages_count=messages_count,
    #     s_status=True,
    #     s_amount=s_amount
    # )

    # Списание из тарифного лога
    # apply_tarif_deduction(request.user, t_type, duration, messages_count)

    return JsonResponse({"status": "ok"})

@login_required
def chat_history(request):
    """История чатов"""
    chats = Chat.objects.filter(user=request.user, c_closed=True).order_by("-c_created")
    chat_id = request.GET.get("chat_id")
    selected_chat = None
    messages = []
    if chat_id:
        selected_chat = get_object_or_404(Chat, pk=chat_id, user=request.user)
        messages = Message.objects.filter(chat=selected_chat).order_by("created")
    return render(request, "chat/chat_history.html", {
        "chats": chats,
        "selected_chat": selected_chat,
        "messages": messages
    })

# @login_required
# def chat_history(request):
#     """История чатов"""
#     chats = Chat.objects.filter(user=request.user, c_closed=True).order_by("-c_created")
#     chat_id = request.GET.get("chat_id")
#     selected_chat = None
#     messages = []
#     if chat_id:
#         selected_chat = get_object_or_404(Chat, pk=chat_id, user=request.user)
#         messages = Message.objects.filter(chat=selected_chat).order_by("created")
#     return render(request, "chat/chat_history.html", {
#         "chats": chats,
#         "selected_chat": selected_chat,
#         "messages": messages
#     })

# def check_free_session(chat):
#     """Проверка бесплатного лимита"""
#     if chat.is_free_session and not chat.free_limit_reached:
#         messages_count = chat.messages.count()
#         duration = (datetime.datetime.now(datetime.timezone.utc) - chat.c_created).seconds // 60
#         if messages_count >= 10 or duration >= 5:
#             chat.free_limit_reached = True
#             chat.c_closed = True
#             chat.save()
#             return False
#     return True


# @login_required
# def close_chat_session(request, chat_id):
#     """Закрытие чата и расчёт тарифа"""
#     chat = get_object_or_404(Chat, id=chat_id, user=request.user)
#
#     if chat.c_closed:
#         return redirect("chat_history")
#
#     chat.c_closed = True
#     chat.save()
#
#     # === Расчёт списания ===
#     t_type = get_user_tarif_type(request.user)
#     duration, messages_count = calculate_chat_usage(chat)
#     s_amount = calculate_payment(t_type, duration, messages_count)
#
#     # Запись в session_log
#     SessionLog.objects.create(
#         user=request.user,
#         t_type=t_type,
#         duration=duration,
#         messages_count=messages_count,
#         s_status=True,
#         s_amount=s_amount
#     )
#
#     # Списание из тарифного лога
#     apply_tarif_deduction(request.user, t_type, duration, messages_count)
#
#     return redirect("chat_history")

def check_free_session(chat):
    """Проверка бесплатного лимита"""
    if chat.is_free_session and not chat.free_limit_reached:
        messages_count = chat.messages.count()
        # Используем aware datetime
        duration = (datetime.datetime.now(datetime.timezone.utc) - chat.c_created).total_seconds() // 60
        if messages_count >= 10 or duration >= 5:
            chat.free_limit_reached = True
            chat.c_closed = True
            chat.save()
            return False
    return True

@login_required
@csrf_exempt # Лучше передавать CSRF токен через fetch
def close_chat_session(request, chat_id):
    """
    Закрытие чата и расчёт тарифа.
    """
    if request.method != "POST":
        # Возвращаем ошибку, если не POST
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    chat = get_object_or_404(Chat, c_id=chat_id, user=request.user)

    if chat.c_closed:
        # Уже закрыт
        return JsonResponse({"status": "already_closed"})

    chat.c_closed = True
    chat.save()

    # === Расчёт списания (если нужно) ===
    # t_type = get_user_tarif_type(request.user)
    # duration, messages_count = calculate_chat_usage(chat)
    # s_amount = calculate_payment(t_type, duration, messages_count)

    # Запись в session_log
    # SessionLog.objects.create(
    #     user=request.user,
    #     t_type=t_type,
    #     duration=duration,
    #     messages_count=messages_count,
    #     s_status=True,
    #     s_amount=s_amount
    # )

    # Списание из тарифного лога
    # apply_tarif_deduction(request.user, t_type, duration, messages_count)

    return JsonResponse({"status": "ok"})

