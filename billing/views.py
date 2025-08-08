# billing/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import logging
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from .models import Tarif, TarifLog, Payment, SessionLog
# Импортируем функцию создания платежа
from .yookassa_client import create_payment

logger = logging.getLogger(__name__)
User = get_user_model()


@login_required
def user_balance(request):
    """Отображение баланса пользователя"""
    # Получаем все активные и оплаченные тарифы пользователя
    active_tariffs = TarifLog.objects.filter(
        user=request.user,
        tl_status=True,
        tl_status_pay=True
    )

    payments = Payment.objects.filter(user=request.user)
    # Получаем session logs пользователя
    sessions = SessionLog.objects.filter(user=request.user)

    # Подготавливаем данные баланса
    balance = {
        "mm": 0,  # Суммарные минуты
        "que": 0,  # Суммарные запросы
        "mon": None  # Дата окончания последней активной подписки
    }

    # Корректный подсчет баланса
    for t in active_tariffs:
        if t.t_type == "mm":
            # Суммируем оставшиеся минуты
            balance["mm"] += max(0, t.remaining_quantity if t.remaining_quantity is not None else 0)
        elif t.t_type == "que":
            # Суммируем оставшиеся запросы
            balance["que"] += max(0, t.remaining_quantity if t.remaining_quantity is not None else 0)
        elif t.t_type == "mon":
            # Для подписки отображаем дату окончания
            # Предполагаем, что t_quatity хранит количество дней
            expiry_date = t.tl_date + timedelta(days=t.t_quatity)
            # Отображаем дату самой "дальней" активной подписки
            if balance["mon"] is None or expiry_date > balance["mon"]:
                balance["mon"] = expiry_date

    return render(request, "billing/balance.html", {
        "balance": balance,
        "payments": payments,
        "sessions": sessions
    })


@login_required
def tariff_list(request):
    """Отображение списка тарифов"""
    tariffs = Tarif.objects.all()
    return render(request, "billing/tariffs.html", {"tariffs": tariffs})


# billing/views.py

@login_required
def buy_tariff(request, tariff_id):
    tariff = get_object_or_404(Tarif, pk=tariff_id)

    if request.method == "POST":
        # Создаем запись в Payment со статусом p_active = False
        payment = Payment.objects.create(
            user=request.user,
            t_name=tariff.t_name,
            t_type=tariff.t_type,
            p_amount=tariff.t_price,
            p_active=False
        )

        # Создаем платеж через ЮKassa
        try:
            yookassa_payment = create_payment(
                tariff.t_price,
                f"Оплата тарифа {tariff.t_name}",
                request.user.u_id,  # Используем u_id для кастомной модели пользователя
                tariff.t_id
            )

            # Сохраняем ID платежа от ЮKassa
            payment.payment_id = yookassa_payment.id
            payment.save()

            # --- ДОБАВЛЕНО: Сохраняем payment_id в сессию ---
            request.session['pending_payment_id'] = yookassa_payment.id
            # --- КОНЕЦ ДОБАВЛЕНИЯ ---

            # Перенаправляем пользователя на страницу оплаты
            return redirect(yookassa_payment.confirmation.confirmation_url)
        except Exception as e:
            logger.error(f"Ошибка при создании платежа: {e}")
            messages.error(request, f"Ошибка при создании платежа: {str(e)[:100]}...")
            payment.delete()  # Удаляем неудачную запись
            return redirect("tariff_list")

    return render(request, "billing/buy_tariff.html", {"tariff": tariff})

# billing/views.py
# ... (импорты остаются без изменений) ...

# billing/views.py

@login_required
def payment_success(request):
    """
    Обработчик успешной оплаты
    """
    import logging
    logger = logging.getLogger(__name__)

    # --- ИЗМЕНЕНО: Получаем payment_id из сессии ---
    # yookassa_payment_id = request.GET.get('payment_id') # Удалить эту строку
    yookassa_payment_id = request.session.get('pending_payment_id')
    # --- КОНЕЦ ИЗМЕНЕНИЯ ---

    logger.info(f"payment_success called for user {request.user.u_id}. Payment ID from session: {yookassa_payment_id}")

    if not yookassa_payment_id:
        logger.error("Payment ID not found in session")
        messages.error(request,
                       "Не удалось получить информацию о платеже (ID отсутствует в сессии). Возможно, страница была обновлена или сессия истекла.")
        return redirect("tariff_list")

    try:
        # Находим платеж в нашей системе
        logger.info(f"Looking for payment with payment_id={yookassa_payment_id} and user_id={request.user.u_id}")
        # --- ИСПРАВЛЕНО: Используем правильное имя поля ---
        payment = get_object_or_404(Payment, payment_id=yookassa_payment_id, user=request.user)
        # --- КОНЕЦ ИСПРАВЛЕНИЯ ---
        logger.info(f"Found payment: p_id={payment.p_id}, p_active={payment.p_active}")

        # Проверяем, не была ли запись уже создана
        if not payment.p_active:
            logger.info("Payment is not active, activating...")
            # Помечаем платеж как активный
            payment.p_active = True
            payment.save()
            logger.info("Payment marked as active")

            # Создаем запись в TarifLog
            logger.info(f"Looking for tariff with name: {payment.t_name}")
            tariff = get_object_or_404(Tarif, t_name=payment.t_name)
            logger.info(f"Found tariff: t_id={tariff.t_id}, t_quatity={tariff.t_quatity}")

            # --- ИСПРАВЛЕНО: Создание записи в TarifLog ---
            tariff_log_entry = TarifLog.objects.create(
                user=request.user,
                t_name=payment.t_name,
                t_type=payment.t_type,
                t_quatity=tariff.t_quatity,  # Используем правильное имя поля
                tl_status=True,
                tl_status_pay=True
                # remaining_quantity будет автоматически установлено в методе save()
            )
            logger.info(f"Created TarifLog entry: tl_id={tariff_log_entry.tl_id}")
            # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

            messages.success(request, f"Тариф '{payment.t_name}' успешно оплачен и активирован!")
            logger.info(f"Success message set for tariff '{payment.t_name}'")
        else:
            logger.info("Payment is already active")
            messages.info(request, f"Тариф '{payment.t_name}' уже был активирован.")

        # --- ДОБАВЛЕНО: Удаляем payment_id из сессии после использования ---
        try:
            del request.session['pending_payment_id']
        except KeyError:
            pass
        # --- КОНЕЦ ДОБАВЛЕНИЯ ---

    except Payment.DoesNotExist:
        logger.error(
            f"Payment.DoesNotExist: No payment found with payment_id={yookassa_payment_id} for user {request.user.u_id}")
        messages.error(request, "Платеж не найден в системе.")
        return redirect("tariff_list")
    except Tarif.DoesNotExist:
        logger.error(f"Tarif.DoesNotExist: No tariff found with name={payment.t_name}")
        messages.error(request, f"Тариф '{payment.t_name}' не найден в системе.")
        return redirect("tariff_list")
    except Exception as e:
        logger.error(
            f"Unexpected error in payment_success for user {request.user.u_id}, payment_id {yookassa_payment_id}: {e}",
            exc_info=True)
        messages.error(request, f"Произошла ошибка при обработке платежа: {str(e)[:100]}...")
        return redirect("tariff_list")

    logger.info("Redirecting to user_balance")
    return redirect("user_balance")

# ... (остальные функции остаются без изменений) ...

# --- Функции для работы с профилем пользователя ---
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django import forms
from users.models import User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "telegram_id"]


@login_required
def edit_profile(request):
    """Редактирование профиля"""
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Профиль обновлён.")
            return redirect("user_balance")
        else:
            messages.error(request, "❌ Ошибка при обновлении профиля.")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "billing/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    """Смена пароля"""
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # чтобы не разлогинило
            messages.success(request, "✅ Пароль успешно изменён.")
            return redirect("user_balance")
        else:
            messages.error(request, "❌ Исправьте ошибки ниже.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "billing/change_password.html", {"form": form})


# --- Функции для проверки тарифов (используются в других приложениях) ---
def check_active_tariff(user):
    """
    Проверяет наличие активного тарифа у пользователя
    """
    active_tariff = TarifLog.objects.filter(
        user=user,
        tl_status=True,
        tl_status_pay=True
    ).first()

    return active_tariff


def deduct_tariff_units(user, chat, message_count=1):
    """
    Списывает единицы тарифа при отправке сообщения.
    Возвращает кортеж (успешно_списано: bool, средства_закончились: bool)
    """
    active_tariff = check_active_tariff(user)
    if not active_tariff:
        print(f"Нет активного тарифа для пользователя {user.username}")
        return False, False

    # Проверка и инициализация remaining_quantity
    if active_tariff.remaining_quantity is None:
        active_tariff.remaining_quantity = active_tariff.t_quatity if active_tariff.t_quatity is not None else 0
        active_tariff.save()

    # Рассчитываем количество потраченных единиц
    if active_tariff.t_type == "mm":
        from django.utils import timezone
        duration = (timezone.now() - chat.c_created).total_seconds() / 60
        quantity = int(duration)
        if duration > quantity:
            quantity += 1
    elif active_tariff.t_type == "que":
        quantity = message_count
    elif active_tariff.t_type == "mon":
        quantity = 0
    else:
        quantity = 0

    # Создаем запись в SessionLog
    SessionLog.objects.create(
        user=user,
        tarif_log=active_tariff,
        c_id=chat.c_id,
        t_type=active_tariff.t_type,
        s_quantity=quantity,
        s_amount=0
    )

    # Обновляем оставшееся количество единиц
    funds_exhausted = False
    if active_tariff.t_type != "mon" and active_tariff.remaining_quantity is not None:
        active_tariff.remaining_quantity -= quantity
        # Проверим границы
        if active_tariff.remaining_quantity < 0:
            active_tariff.remaining_quantity = 0
        # Проверим, закончился ли тариф
        if active_tariff.remaining_quantity <= 0:
            active_tariff.tl_status = False
            funds_exhausted = True  # Флаг, что средства закончились
        active_tariff.save()

    # Если средства закончились, закрываем чат
    if funds_exhausted:
        chat.c_closed = True
        chat.save()

    return True, funds_exhausted  # Возвращаем успех и флаг исчерпания средств