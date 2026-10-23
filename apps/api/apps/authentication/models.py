from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from django_jalali.db.models import jDateTimeField
from .validators import *
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractBaseUser, PermissionsMixin):
    email = models.CharField(max_length=350, validators=[email_validator], unique=True)
    # Basic data
    phone_number = models.CharField(max_length=11, validators=[phone_validator], null=True, blank=True)
    first_name = models.CharField(max_length=70, null=True, blank=True)
    last_name = models.CharField(max_length=70,null=True, blank=True)
    national_code = models.CharField(max_length=10, validators=[nationalCode_validator], null=True, blank=True)
    birth_date = models.CharField(max_length=10, validators=[date_validator], null=True, blank=True)
    CHOICES_GENDER = [
        ("female", "زن"),
        ("male", "مرد"),
    ]
    gender = models.CharField(max_length=6, choices=CHOICES_GENDER, null=True, blank=True)


    # ------------------------------------------------------------

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = jDateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email