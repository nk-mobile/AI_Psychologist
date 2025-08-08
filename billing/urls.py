from django.urls import path
from . import views

urlpatterns = [
    path("tariffs/", views.tariff_list, name="tariff_list"),
    path("buy/<int:tariff_id>/", views.buy_tariff, name="buy_tariff"),
    path("payment-success/", views.payment_success, name="payment_success"), # Убедитесь, что это есть

    path("balance/", views.user_balance, name="user_balance"),
    # path("tariffs/", views.tariff_list, name="tariff_list"),
    # path("buy/<int:tariff_id>/", views.buy_tariff, name="buy_tariff"),
    path("profile/", views.edit_profile, name="edit_profile"),        # ✅ Редактирование профиля
    path("change-password/", views.change_password, name="change_password"),  # ✅ Смена пароля
]
