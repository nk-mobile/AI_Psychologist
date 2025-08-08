import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
# from django.contrib.auth.models import AnonymousUser
from .models import Chat, Message
# from gpt_client import get_gpt_response  # ✅ вынесли GPT в отдельный файл
from .gpt_client import get_gpt_response
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Chat, Message
from billing.views import deduct_tariff_units
import json

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         from django.contrib.auth.models import AnonymousUser  # ✅ импортируем здесь, после инициализации Django
#
#         self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
#         self.room_group_name = f"chat_{self.chat_id}"
#
#         user = self.scope["user"]
#         if not user.is_authenticated or isinstance(user, AnonymousUser):
#             await self.close()
#             return
#
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
#
#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data.get("message", "").strip()
#         user = self.scope["user"]
#
#         if not message:
#             return
#
#         # 1️⃣ Сохраняем сообщение пользователя
#         await self.save_message(user.u_id, self.chat_id, message, role="user")
#
#         # 2️⃣ Отправляем сообщение в чат
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 "type": "chat_message",
#                 "user": user.username,
#                 "message": message
#             }
#         )
#
#         # 3️⃣ Списываем единицы тарифа
#         chat = await self.get_chat()
#         await self.deduct_tariff(user, chat)
#
#         # 4️⃣ Получаем ответ GPT
#         bot_reply = await sync_to_async(get_gpt_response)([
#             {"role": "system", "content": "Ты эмпатичный психолог."},
#             {"role": "user", "content": message}
#         ])
#
#         # 5️⃣ Сохраняем ответ
#         await self.save_message(None, self.chat_id, bot_reply, role="assistant")
#
#         # 6️⃣ Отправляем ответ в чат
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 "type": "chat_message",
#                 "user": "Психолог",
#                 "message": bot_reply
#             }
#         )
#
#     async def deduct_tariff(self, user, chat):
#         """
#         Списывает единицы тарифа
#         """
#         # Получаем количество сообщений в чате
#         message_count = await self.get_message_count()
#
#         # Списываем единицы тарифа
#         await sync_to_async(deduct_tariff_units)(user, chat, message_count)
#
#     @sync_to_async
#     def get_chat(self):
#         return Chat.objects.get(c_id=self.chat_id)
#
#     @sync_to_async
#     def get_message_count(self):
#         return Message.objects.filter(chat_id=self.chat_id).count()
#
#     async def chat_message(self, event):
#         await self.send(text_data=json.dumps({
#             "user": event["user"],
#             "message": event["message"]
#         }))
#
#     @sync_to_async
#     def save_message(self, user_id, chat_id, text, role):
#         chat = Chat.objects.get(c_id=chat_id)
#         Message.objects.create(chat=chat, user_id=user_id, text=text, role=role)
#
#     @sync_to_async
#     def get_bot_reply(self, user_message):
#         return get_gpt_response([{"role": "user", "content": user_message}])

# chat/consumers.py
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from .models import Chat, Message
# # Импортируем обновленную функцию
from billing.views import deduct_tariff_units, check_active_tariff
# # Для асинхронного вызова синхронных функций
from asgiref.sync import sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        # Проверяем, существует ли чат и принадлежит ли он пользователю
        try:
            chat = await sync_to_async(Chat.objects.get)(c_id=self.chat_id, user=self.scope["user"])
            if chat.c_closed:
                await self.close()  # Закрываем соединение, если чат закрыт
                return
        except Chat.DoesNotExist:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()
        user = self.scope["user"]

        if not message:
            return

        # 1️⃣ Сохраняем сообщение пользователя
        await self.save_message(user.u_id, self.chat_id, message, role="user")

        # 2️⃣ Отправляем сообщение пользователя в чат (всем в группе)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "user": user.username,  # Имя пользователя
                "message": message
            }
        )

        # 3️⃣ Списываем единицы тарифа и проверяем, не закончились ли средства
        chat_obj = await sync_to_async(Chat.objects.get)(c_id=self.chat_id)
        # Получаем количество сообщений в чате для передачи в deduct_tariff_units
        # Это нужно только для тарифа "que"
        msg_count = 1  # Считаем текущее сообщение

        success, funds_exhausted = await sync_to_async(deduct_tariff_units)(user, chat_obj, msg_count)

        if not success:
            # Если списание не удалось (например, нет тарифа), можно отправить сообщение об ошибке
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "user": "Система",
                    "message": "Ошибка: не удалось обработать запрос. Обратитесь в поддержку."
                }
            )
            # Закрываем соединение?
            # await self.close()
            return

        # 4️⃣ Если средства закончились, отправляем специальное сообщение и закрываем чат
        if funds_exhausted:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "user": "Система",
                    "message": "Средства закончились. Пополните баланс для продолжения общения."
                }
            )
            # Чат уже закрыт в deduct_tariff_units, но можно отправить сигнал на фронтенд
            # для блокировки поля ввода. Это можно сделать через отдельное сообщение или
            # добавив флаг в предыдущее сообщение. Пока просто отправим сообщение.
            return  # Не продолжаем обработку, не запрашиваем GPT

        # 5️⃣ Получаем ответ GPT (только если средства не закончились)
        # Собираем историю сообщений для контекста
        messages_queryset = await sync_to_async(
            lambda: list(Message.objects.filter(chat=chat_obj).order_by('created')))()
        messages_for_gpt = []
        for msg in messages_queryset:
            role = "assistant" if msg.role == "assistant" else "user"
            messages_for_gpt.append({"role": role, "content": msg.text})

        # Добавляем системный промт (если нужно)
        system_prompt = {"role": "system",
                         "content": "Ты — эмпатичный психолог. Отвечай с пониманием, поддержкой и мягким тоном. Задавай уточняющие вопросы, если нужно. Не давай медицинских диагнозов."}
        messages_for_gpt.insert(0, system_prompt)

        try:
            bot_reply = await self.get_gpt_response(messages_for_gpt)
        except Exception as e:
            print(f"Ошибка при получении ответа от GPT: {e}")
            bot_reply = "Извините, произошла ошибка при обработке вашего запроса. Попробуйте еще раз."

        # 6️⃣ Сохраняем ответ бота
        await self.save_message(None, self.chat_id, bot_reply, role="assistant")

        # 7️⃣ Отправляем ответ бота в чат
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "user": "Психолог",
                "message": bot_reply
            }
        )

    async def chat_message(self, event):
        """
        Отправляет сообщение через WebSocket
        """
        await self.send(text_data=json.dumps({
            "user": event["user"],
            "message": event["message"]
        }))

    @sync_to_async
    def save_message(self, user_id, chat_id, text, role="user"):
        """
        Сохраняет сообщение в базу данных
        """
        chat = Chat.objects.get(c_id=chat_id)
        user = self.scope["user"] if user_id else None
        Message.objects.create(
            chat=chat,
            user=user,
            role=role,
            text=text
        )

    async def get_gpt_response(self, messages):
        """
        Получает ответ от GPT.
        Эта функция должна быть асинхронной или вызываться через sync_to_async.
        Предполагается, что у вас есть функция get_gpt_response в gpt_client.py.
        """
        from .gpt_client import get_gpt_response as sync_get_gpt_response
        # Если get_gpt_response синхронная, оберните ее:
        response = await sync_to_async(sync_get_gpt_response)(messages)
        return response
