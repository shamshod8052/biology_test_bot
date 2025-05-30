from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.utils.translation import gettext_lazy as _

from Admin.models import User, Channel


@admin.register(User)
class UserAdmin(_UserAdmin):
    fieldsets = (
        (None, {"fields": ("phone", "password", 'telegram_id', 'language')}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "username")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "tg_status",
                    # "groups",
                    # "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "password1", "password2"),
            },
        ),
    )

    list_display = ("id", "first_name", "last_name", "phone", "is_staff", "language", "tg_status")
    search_fields = ("id", "phone", "first_name", "last_name")
    ordering = ()
    list_filter = ("is_staff", "is_superuser", "is_active", "language", "tg_status")

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'chat_id', 'is_required', 'is_active']
