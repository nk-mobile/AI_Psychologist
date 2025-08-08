from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_room, name="chat_room"),  # ✅ основная страница чата
    path("history/", views.chat_history, name="chat_history"),
    path("close/<int:chat_id>/", views.close_chat_session, name="close_chat_session"),
]
