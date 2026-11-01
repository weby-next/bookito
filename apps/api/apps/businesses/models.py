from django.db import models
from django_jalali.db.models import jDateTimeField
from django.conf import settings


class Business(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PUBLISHED = "published", "منتشر‌شده"
        SUSPENDED = "suspended", "تعلیق‌شده"

    # Owner
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="businesses")

    # Basic Information
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    # Business status
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    # Timestamps
    created_at = jDateTimeField(auto_now_add=True)
    updated_at = jDateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name