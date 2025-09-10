import random
import string

from django.core.mail import send_mail
from django.utils import timezone

from .models import OtpCode


def send_otp_code(email: str) -> None:
    """
    Функция отправки единоразового 6-значного кода на почту.
    Токен доступен 10 минут, после этого направляется новый код.
    """
    try:
        datetime_now = timezone.datetime.now()
        if OtpCode.objects.filter(
            email=email, expired__gt=datetime_now
        ).exists():
            code = OtpCode.objects.filter(
                email=email, expired__gt=datetime_now
            ).first().code
        else:
            code = ''.join(random.choices(string.digits, k=6))
        send_mail(
            subject='Ваш код для получения токена',
            message=f'Ваш код для получения токена: {code}\nОн будет доступен 10 минут.',
            from_email='myemail@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )
        OtpCode.objects.update_or_create(
            email=email,
            defaults={
                'code': code,
                'created_at': datetime_now,
                'expired': datetime_now + timezone.timedelta(minutes=10)
            }
        )
    except Exception as e:
        print(f'Возникла ошибка при отправке:\n{e}')
