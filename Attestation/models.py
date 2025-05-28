from django.db import models
from django.utils.translation import gettext_lazy as _

from Knowledge.models import BaseChannel, BaseLesson
from Knowledge.models import BaseChannelManager
from Knowledge.models import BaseCourse
from Knowledge.models import Status, BaseCourseManager


class DiagnosticTestManager(models.Manager):
    def get_text(self):
        tests = self.filter(is_active=True)
        if tests.exists():
            return tests.first().text
        else:
            return str(_("The test is not available!"))


class DiagnosticTest(models.Model):
    objects = DiagnosticTestManager()

    text = models.TextField(verbose_name=_("Text"))
    is_active = models.BooleanField(verbose_name=_("Is active"), default=True)

    def save(self, *args, **kwargs):
        self.status = Status.ATTESTATION
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Diagnostic test')
        verbose_name_plural = _('Diagnostic tests')


class CourseManager(BaseCourseManager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Status.ATTESTATION)


class Course(BaseCourse):
    objects = CourseManager()

    def save(self, *args, **kwargs):
        self.status = Status.ATTESTATION
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['id']
        proxy = True


class ChannelManager(BaseChannelManager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Status.ATTESTATION)


class Channel(BaseChannel):
    objects = ChannelManager()

    def save(self, *args, **kwargs):
        self.status = Status.ATTESTATION
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Channel")
        verbose_name_plural = _("Channels")
        proxy = True


class Lesson(BaseLesson):

    def save(self, *args, **kwargs):
        self.status = Status.ATTESTATION
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Test analyse video")
        verbose_name_plural = _("Test analyse videos")
        proxy = True
