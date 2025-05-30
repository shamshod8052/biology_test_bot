from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    class TgStatus(models.IntegerChoices):
        ACTIVE = 1, _('✅ Active')
        BOT_BLOCKED = 2, _('🚫 Blocked the bot')
        TELEGRAM_NOT_FOUND = 3, _('🔴 Telegram Not Found')
        BLOCKED = 4, _('⛔️ Blocked')
        FAILED = 5, _('❗️ Failed')

    phone = PhoneNumberField(_("Phone"), unique=True, null=True, blank=True)
    password = models.CharField(_("Password"), max_length=128, blank=True)
    first_name = models.CharField(_("First name"), max_length=150, blank=True)
    last_name = models.CharField(_("Last name"), max_length=150, null=True, blank=True)
    username = models.CharField(_("Username"), max_length=150, null=True, blank=True)
    language = models.CharField(max_length=15, choices=settings.LANGUAGES, default='uz')
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    tg_status = models.IntegerField(choices=TgStatus.choices, default=TgStatus.ACTIVE)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ('telegram_id',)

    class Meta:
        ordering = ('-id',)
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        swappable = "AUTH_USER_MODEL"
        # https://stackoverflow.com/questions/22025476/what-is-swappable-in-model-meta-for

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

class Channel(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    chat_id = models.CharField(verbose_name=_("Chat id"), max_length=50, unique=True)
    url = models.URLField(verbose_name=_("Url"), max_length=255)
    is_required = models.BooleanField(verbose_name=_("Is required"), default=True)
    is_active = models.BooleanField(verbose_name=_("Is active"), default=True)

    def get_chat_id(self):
        return int(self.chat_id)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Channel")
        verbose_name_plural = _("Channels")
