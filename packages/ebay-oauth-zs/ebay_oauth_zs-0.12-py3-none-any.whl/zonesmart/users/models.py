from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import Q
from django.utils.timezone import now


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Поле "E-mail" является обязательным для заполнения')
        email = self.normalize_email(email)
        user = User(
            email=email,
            is_staff=is_staff,
            is_superuser=is_superuser,
            date_joined=now(),
            **extra_fields,
        )
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(Q(email=username) | Q(phone=username))


class User(AbstractUser):
    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    email = models.EmailField(unique=True, verbose_name="E-mail")
    phone = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Мобильный номер",
    )

    username = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Юзернейм"
    )
    first_name = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="Фамилия"
    )

    ready = models.BooleanField(
        default=False, verbose_name="Профиль достаточно заполнен"
    )
    paid = models.BooleanField(default=False, verbose_name="Доступ оплачен")
    access_until = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.email}"
