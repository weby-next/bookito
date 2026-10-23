from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission

admin.site.register(Permission)


@admin.register(User)
class UserAdmin(UserAdmin):
    # هنگام ویرایش user 
    fieldsets = (
        (None, {'fields': ('email', 'phone_number', 'password', 'first_name', 'last_name', 'national_code', 'birth_date', 'gender')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', )}),
    )

    # هنگام ساخت user جدید
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'password1', 'password2', 'first_name', 'last_name', 'national_code', 'birth_date', 'gender'),
        }),
    )

    list_display = ['id', 'email','phone_number', 'first_name', 'last_name', 'national_code', 'date_joined']
    ordering = ['-date_joined',]