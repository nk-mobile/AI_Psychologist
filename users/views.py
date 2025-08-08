from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
# Исправлено: добавлен TemplateView
from django.views.generic import View, FormView, TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login
# from django.views import View # Удалено, так как уже импортировано выше

# Импортируем модель TarifLog из billing для HomeView
from billing.models import TarifLog

from .models import User
from .forms import (
    RegisterForm,
    LoginForm,
    PasswordResetRequestForm,
    PasswordResetConfirmForm,
    # RegisterForm, # Удалено дублирование
)

# ✅ Регистрация (ТОЛЬКО через модальное окно)
class RegisterView(View):
    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # пока не подтвердит email
            user.save()
            self.send_activation_email(user, request)
            messages.info(request, "📩 На ваш email отправлена ссылка для активации аккаунта.")
        else:
            messages.error(request, "❌ Ошибка при регистрации. Проверьте введенные данные.")
        return redirect("home")  # всегда остаемся на главной

    def send_activation_email(self, user, request):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = request.build_absolute_uri(
            reverse("verify_email", kwargs={"uidb64": uid, "token": token})
        )

        subject = "Подтверждение регистрации"
        message = (
            f"Здравствуйте, {user.username}!\n\n"
            f"Для активации аккаунта перейдите по ссылке:\n{activation_link}\n\n"
            "Если вы не регистрировались, просто проигнорируйте это письмо."
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


# ✅ Подтверждение email (также возвращает на главную)
class VerifyEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "✅ Аккаунт успешно активирован! Теперь вы можете войти.")
        else:
            messages.error(request, "❌ Ссылка активации недействительна или устарела.")

        return redirect("home")

class LoginView(View):
    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"✅ Добро пожаловать, {user.username}!")
            else:
                messages.error(request, "❌ Аккаунт не активирован.")
        else:
            messages.error(request, "❌ Неверный email или пароль.")

        return redirect("/")

# ✅ Логаут
@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "✅ Вы вышли из системы.")
        return redirect("home")  # или на главную

    def post(self, request):
        logout(request)
        messages.info(request, "✅ Вы вышли из системы.")
        return redirect("home")


# ✅ Запрос на сброс пароля
class PasswordResetRequestView(FormView):
    template_name = "users/password_reset_request.html"
    form_class = PasswordResetRequestForm

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(self.request, "❌ Пользователь с таким email не найден.")
            return redirect("password_reset")

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = self.request.build_absolute_uri(
            reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
        )

        subject = "Сброс пароля"
        message = (
            f"Здравствуйте, {user.username}!\n\n"
            f"Для сброса пароля перейдите по ссылке:\n{reset_link}\n\n"
            "Если вы не запрашивали сброс, проигнорируйте это письмо."
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        messages.info(self.request, "📩 Ссылка для сброса пароля отправлена на ваш email.")
        return redirect("login")


# ✅ Сброс пароля
class PasswordResetConfirmView(FormView):
    template_name = "users/password_reset_confirm.html"
    form_class = PasswordResetConfirmForm

    def dispatch(self, request, *args, **kwargs):
        self.uidb64 = kwargs.get("uidb64")
        self.token = kwargs.get("token")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            uid = force_str(urlsafe_base64_decode(self.uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, self.token):
            password = form.cleaned_data["new_password1"]
            user.set_password(password)
            user.save()
            messages.success(self.request, "✅ Пароль успешно изменён. Войдите снова.")
            return redirect("login")
        else:
            messages.error(self.request, "❌ Ссылка для сброса пароля недействительна.")
            return redirect("password_reset")

# ... (весь ваш существующий код в users/views.py) ...

# Новое представление для главной страницы
class HomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['user'] уже доступен благодаря auth middleware, если пользователь аутентифицирован

        # Если пользователь аутентифицирован, проверяем его баланс
        if self.request.user.is_authenticated:
            # Ищем активный и оплаченный тариф
            active_tariff = TarifLog.objects.filter(
                user=self.request.user,
                tl_status=True,
                tl_status_pay=True
            ).first()

            # Добавляем информацию о тарифе в контекст
            context['active_tariff'] = active_tariff
            # Можно добавить флаг для удобства в шаблоне
            context['has_sufficient_funds'] = (
                active_tariff is not None and
                active_tariff.remaining_quantity is not None and
                active_tariff.remaining_quantity > 0
            )

        return context