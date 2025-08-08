import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Chat, Message
from .gpt_client import get_gpt_response  # ✅ твой файл GPT


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.chat_id}"

        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
        else:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        user = self.scope["user"]

        # ✅ сохраняем сообщение пользователя
        await self.save_message(user.pk, self.chat_id, message, role="user")

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "user": user.username, "message": message}
        )

        # ✅ получаем ответ бота
        bot_reply = await get_gpt_response([
            {"role": "user", "content": message}
        ])

        # ✅ сохраняем ответ бота
        await self.save_message(None, self.chat_id, bot_reply, role="assistant")

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "user": "Психолог", "message": bot_reply}
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "user": event["user"],
            "message": event["message"]
        }))

    @sync_to_async
    def save_message(self, user_id, chat_id, text, role="user"):
        chat = Chat.objects.get(pk=chat_id)
        if user_id:
            Message.objects.create(chat=chat, user_id=user_id, m_text=text, role=role)
        else:
            Message.objects.create(chat=chat, m_text=text, role="assistant")
