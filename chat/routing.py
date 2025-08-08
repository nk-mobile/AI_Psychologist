from django.urls import re_path
# from .consumers import ChatConsumer
from . import consumers

websocket_urlpatterns = [
    # re_path(r"ws/chat/(?P<chat_id>\d+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/chat/(?P<chat_id>\d+)/$", consumers.ChatConsumer.as_asgi()),
]
