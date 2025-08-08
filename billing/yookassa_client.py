import uuid
from yookassa import Configuration, Payment
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Настройка конфигурации ЮKassa
Configuration.account_id = settings.YOO_KASSA_SHOP_ID
Configuration.secret_key = settings.YOO_KASSA_SECRET_KEY


# def create_payment(amount, description, user_id, tariff_id):
#     """
#     Создание платежа через ЮKassa
#     """
#     logger.info(
#         f"Создание платежа: amount={amount}, description='{description}', user_id={user_id}, tariff_id={tariff_id}")
#
#     try:
#         payment = Payment.create({
#             "amount": {
#                 "value": str(amount),
#                 "currency": "RUB"
#             },
#             "confirmation": {
#                 "type": "redirect",
#                 # Убедитесь, что этот URL доступен из интернета для возврата после оплаты
#                 # Для локальной разработки это может быть проблемой
#                 "return_url": "http://127.0.0.1:8000/billing/payment-success/"
#             },
#             "description": description,
#             "metadata": {
#                 "user_id": str(user_id),  # Преобразуем в строку для надежности
#                 "tariff_id": str(tariff_id)  # Преобразуем в строку для надежности
#             }
#         }, uuid.uuid4())
#
#         logger.info(f"Платеж создан успешно: payment_id={payment.id}")
#         return payment
#     except Exception as e:
#         logger.error(f"Ошибка при создании платежа в ЮKassa: {e}")
#         raise e  # Пробрасываем исключение дальше

# billing/yookassa_client.py

# billing/yookassa_client.py

def create_payment(amount, description, user_u_id, tariff_id):
    """
    Создание платежа через ЮKassa
    """
    logger.info(
        f"Создание платежа: amount={amount}, description='{description}', user_u_id={user_u_id}, tariff_id={tariff_id}")

    try:
        payment = Payment.create({
            "amount": {
                "value": str(amount),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                # Исправлено: убран placeholder, используется простой URL
                "return_url": "http://127.0.0.1:8000/billing/payment-success/"
            },
            "description": description,
            "metadata": {
                "user_id": str(user_u_id),
                "tariff_id": str(tariff_id)
            }
        }, uuid.uuid4())

        logger.info(f"Платеж создан успешно: payment_id={payment.id}")
        return payment
    except Exception as e:
        logger.error(f"Ошибка при создании платежа в ЮKassa: {e}")
        raise e