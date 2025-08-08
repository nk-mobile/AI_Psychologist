from billing.models import TarifLog

def get_user_tarif_type(user):
    """Возвращаем активный тариф пользователя"""
    active_tarif = TarifLog.objects.filter(u_id=user.id, tl_status=True).order_by("-tl_date").first()
    return active_tarif.t_type if active_tarif else None


def calculate_chat_usage(chat):
    """Вычисляем длительность чата и количество сообщений"""
    from django.utils.timezone import now

    first_msg = chat.messages.order_by("timestamp").first()
    last_msg = chat.messages.order_by("-timestamp").first()

    if not first_msg or not last_msg:
        return 0, 0

    duration = (last_msg.timestamp - first_msg.timestamp).total_seconds() // 60
    messages_count = chat.messages.count()

    return int(duration), messages_count


def calculate_payment(t_type, duration, messages_count):
    """Сколько списать за сессию"""
    if t_type == "mm":  # по минутам
        return duration
    elif t_type == "que":  # по сообщениям
        return messages_count
    elif t_type == "mon":  # подписка — без списания
        return 0
    return 0


def apply_tarif_deduction(user, t_type, duration, messages_count):
    """Списываем из пакета после завершения"""
    tarif = TarifLog.objects.filter(u_id=user.id, tl_status=True, tl_status_pay=True).order_by("-tl_date").first()
    if not tarif:
        return

    if t_type == "mm":
        tarif.tl_quatity = max(0, tarif.t_quatity - duration)
    elif t_type == "que":
        tarif.tl_quatity = max(0, tarif.t_quatity - messages_count)
    # подписка не списывается

    if tarif.tl_quatity <= 0 and t_type != "mon":
        tarif.tl_status = False  # тариф закончился
    tarif.save()
