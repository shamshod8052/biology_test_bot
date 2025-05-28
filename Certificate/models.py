from django.db import models
from django.utils.translation import gettext_lazy as _

from Knowledge.models import BaseAnswer, Status, BaseCourseManager, BaseLesson
from Knowledge.models import BaseChannel
from Knowledge.models import BaseChannelManager
from Knowledge.models import BaseCourse
from Knowledge.models import BaseDiagnosticTest
from Knowledge.models import BaseUserAnswer


class DiagnosticTestManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Status.CERTIFICATE)


class DiagnosticTest(BaseDiagnosticTest):
    objects = DiagnosticTestManager()

    def save(self, *args, **kwargs):
        self.status = Status.CERTIFICATE
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Diagnostic test')
        verbose_name_plural = _('Diagnostic tests')
        proxy = True


class Answer(BaseAnswer):
    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
        proxy = True


class UserAnswer(BaseUserAnswer):
    class Meta:
        verbose_name = _('User answer')
        verbose_name_plural = _('User answers')
        proxy = True


class CourseManager(BaseCourseManager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Status.CERTIFICATE)


class Course(BaseCourse):
    objects = CourseManager()

    def save(self, *args, **kwargs):
        self.status = Status.CERTIFICATE
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['id']
        proxy = True


class ChannelManager(BaseChannelManager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Status.CERTIFICATE)


class Channel(BaseChannel):
    objects = ChannelManager()

    def save(self, *args, **kwargs):
        self.status = Status.CERTIFICATE
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Channel")
        verbose_name_plural = _("Channels")
        proxy = True


class Lesson(BaseLesson):

    def save(self, *args, **kwargs):
        self.status = Status.CERTIFICATE
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Test analyse video")
        verbose_name_plural = _("Test analyse videos")
        proxy = True
