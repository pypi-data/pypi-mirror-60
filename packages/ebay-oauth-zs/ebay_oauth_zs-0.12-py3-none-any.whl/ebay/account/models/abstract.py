from django.db import models

from model_utils import Choices

from zonesmart.data.enums import AllCountryCodeEnum


class AbstractPhone(models.Model):
    PHONE_TYPE_CHOICES = Choices(
        ("MOBILE", "Мобильный"), ("LAND_LINE", "Стационарный"),
    )
    countryCode = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        choices=AllCountryCodeEnum,
        verbose_name="Страна",
    )
    number = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Номер телефона"
    )
    phoneType = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=PHONE_TYPE_CHOICES,
        verbose_name="Тип телефона",
    )


class AbstractContact(models.Model):
    firstName = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Имя"
    )
    lastName = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Фамилия"
    )
