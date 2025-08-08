from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def send_activation_email(user, request):
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
