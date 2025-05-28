import logging
from functools import cached_property
from typing import Optional

from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from Admin.models import User
from helpers.reducer import text_reducer
from helpers.tele_bot import tele_bot


class Status(models.IntegerChoices):
    NOTSET = 0, _('Not set')
    ATTESTATION = 1, _('Attestation')
    CERTIFICATE = 2, _('Certificate')


class BaseDiagnosticTest(models.Model):
    class TestResultDisplayMode(models.IntegerChoices):
        OVERALL_ONLY = 1, _("Overall result")
        CORRECT_COUNT_ONLY = 2, _("Correct answers number")
        ONLY_SELECTED = 3, _("Only selected answers")

    name = models.CharField(_('Name'), max_length=255)
    file = models.FileField(verbose_name=_('File'), upload_to='documents')
    tg_file_id = models.CharField(_('Telegram File ID'), max_length=255, blank=True, null=True, editable=False)
    saved_file_path = models.CharField(_('Saved File Path'), max_length=255, blank=True, null=True, editable=False)
    description = models.TextField(
        verbose_name=_('Description'), null=True, blank=True,
        help_text=_("This text will contain information about the test.")
    )
    result_display_mode = models.IntegerField(
        verbose_name=_("Select the result display mode?"), choices=TestResultDisplayMode.choices,
        default=TestResultDisplayMode.CORRECT_COUNT_ONLY
    )
    started_at = models.DateTimeField(verbose_name=_('Started at'), null=True, blank=True)
    ends_at = models.DateTimeField(verbose_name=_('Ends at'), null=True, blank=True)

    is_active = models.BooleanField(_('Active'), default=True)
    status = models.IntegerField(verbose_name=_('Status'), choices=Status.choices, default=Status.NOTSET, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    def get_times_str(self):
        text = ''
        if self.started_at:
            text += "<i>" + _(f"Started at: ") + self.started_at.strftime("%Y-%m-%d %H:%M") + "</i>\n"
        if self.ends_at:
            text += "<i>" + _(f"Ends at: ") + self.ends_at.strftime("%Y-%m-%d %H:%M") + "</i>"

        return "\n\n" + text.strip() if text else ''

    def get_description(self):
        text = (
            f"{self.get_times_str()}"
            f"\n\n{self.description}"
        )

        return text

    def is_end(self):
        status = self.ends_at and self.ends_at <= now()

        return status

    def is_view(self):
        status = self.is_active and (not self.started_at or self.started_at <= now())

        return status

    def is_answered(self, user: User):
        user_answer = self.user_answers.filter(user=user).first()

        return user_answer and user_answer.answers_text

    def add_user_answers(self, user: User, answers_text: Optional[str] = None, is_validate=True):
        if is_validate:
            user_answers = self.parse_user_answers(answers_text)
            self._validate_answers(user_answers)

        BaseUserAnswer.objects.add(self, user, answers_text)

    def group_answer_types(self) -> list[list[str] | str]:
        """
        Ketma-ket CLOSE javob turlarini guruhlarga ajratadi.
        """
        answer_types = list(self.answers.values_list('type', flat=True))
        grouped = []
        temp = []

        for t in answer_types:
            if t == BaseAnswer.Type.CLOSE:
                temp.append(t)
            else:
                if temp:
                    grouped.append(temp.copy())
                    temp.clear()
                grouped.append(t)

        if temp:
            grouped.append(temp)

        return grouped

    @staticmethod
    def parse_close_group(group: list[str], line_iter: iter) -> list[str]:
        """
        CLOSE tipidagi javoblarni guruhlash (masalan: ['A', 'C', 'B']).
        """
        try:
            line = next(line_iter)
        except StopIteration:
            raise ValueError("CLOSE javoblar uchun yetarli satr mavjud emas.")

        if len(line) < len(group):
            raise ValueError("CLOSE javoblar soni noto‘g‘ri.")

        close_answers = list(line[:len(group)])
        # remaining = line[len(group):].strip()
        #
        # if remaining:
        #     # Qolganini iterga qaytaramiz
        #     line_iter = iter([remaining] + list(line_iter))

        return close_answers

    @staticmethod
    def parse_open_answer(line_iter: iter) -> str:
        """
        OPEN tipidagi javobni olish.
        """
        try:
            return next(line_iter)
        except StopIteration:
            raise ValueError("OPEN javob uchun satr yetishmayapti.")

    def parse_user_answers(self, answers_text: str) -> list[list[str] | str]:
        """
        Foydalanuvchi javoblarini toza struktura asosida parsing qiladi.
        """
        answers_text = answers_text or ''
        lines = [line.strip() for line in answers_text.splitlines() if line.strip()]
        if not lines:
            return []
        line_iter = iter(lines)

        grouped_types = self.group_answer_types()
        user_answers = []

        for group in grouped_types:
            if isinstance(group, list):  # CLOSE guruhi
                try:
                    close_group = self.parse_close_group(group, line_iter)
                except ValueError as e:
                    raise ValidationError(str(e))
                user_answers.extend(close_group)
            else:  # OPEN
                try:
                    open_answer = self.parse_open_answer(line_iter)
                except ValueError as e:
                    raise ValidationError(str(e))
                user_answers.append(open_answer)

        return user_answers

    def _validate_answers(self, user_answers: list):
        if self.answers.count() != len(user_answers):
            raise ValidationError(_("Not enough answers!"))

    def is_file_synchronized(self):
        return self.file.path == self.saved_file_path

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_file_synchronized():
            return

        if self.file and self.file.path:
            try:
                with open(self.file.path, 'rb') as f:
                    response = tele_bot.send_document(
                        chat_id=settings.DEFAULT_BOT_CHAT,
                        document=f
                    )
            except Exception as e:
                logging.error(f"Telegram fayl yuborishda xatolik: {e}")
                return
            else:
                self.tg_file_id = response.document.file_id
                self.saved_file_path = self.file.path
                super().save(update_fields=["tg_file_id", "saved_file_path"])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Diagnostic test')
        verbose_name_plural = _('Diagnostic tests')
        ordering = ['id']


class BaseAnswer(models.Model):
    class Type(models.IntegerChoices):
        OPEN = 1, _("Open")
        CLOSE = 2, _("Close")
    test = models.ForeignKey(BaseDiagnosticTest, verbose_name=_('Diagnostic test'), on_delete=models.CASCADE, related_name='answers')
    type = models.IntegerField(verbose_name=_('Type'), choices=Type.choices, default=Type.CLOSE)
    value = models.CharField(_('Value'), max_length=255)

    def check_answer(self, user_answer: str) -> bool:
        if self.value.strip() == user_answer.strip():
            return True
        return False

    def __str__(self):
        return text_reducer(self.value, 32)

    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')


class BaseUserAnswerManager(models.Manager):
    def add(self, test: BaseDiagnosticTest, user: User, user_answer: str):
        obj, cr = self.get_or_create(user=user, test=test)
        obj.answers_text = user_answer
        obj.save()


class BaseUserAnswer(models.Model):
    objects = BaseUserAnswerManager()

    user = models.ForeignKey(User, verbose_name=_('User'), on_delete=models.CASCADE)
    test = models.ForeignKey(BaseDiagnosticTest, verbose_name=_('Diagnostic test'), on_delete=models.CASCADE, related_name='user_answers')
    answers_text = models.TextField(_('Answers text'), null=True, blank=True, default='')

    @cached_property
    def user_answers_list(self) -> list[str]:
        """
        answers_text satrlarini ajratadi. Birinchi qatordagi belgilarni
        alohida element qilib, keyingi qatordagi butun satrlarni element sifatida oladi.
        """

        return self.test.parse_user_answers(self.answers_text)

    def get_user_result(self):
        """
            Bu metod list qaytaradi [{'number': 1, 'correct': True, 'text': 'Banana'}, ...]
        """
        answers = list(self.test.answers.all())
        user_ans = self.user_answers_list
        result = []

        for idx, answer in enumerate(answers):
            ua = user_ans[idx] if idx < len(user_ans) else ''  # user answer
            result.append(
                {
                    'number': idx + 1,
                    'correct': answer.check_answer(ua),
                    'text': ua,
                }
            )

        return result

    def count_correct_incorrect(self) -> tuple[int, int]:
        """
        Foydalanuvchining toʻgʻri va notoʻgʻri javoblari sonini qaytaradi (correct_count, incorrect_count).
        """
        result = self.get_user_result()
        correct = sum(1 for ch in result if ch['correct'])
        incorrect = len(result) - correct

        return correct, incorrect

    def get_result_text(self):
        if self.test.result_display_mode == self.test.TestResultDisplayMode.OVERALL_ONLY:
            correct, incorrect = self.count_correct_incorrect()
            answers_text = ''
            for n, result in enumerate(self.get_user_result()):
                answers_text += f"{result['number']}. {result['text']} {'✅' if result['correct'] else '❌'}  "
                if n != 0 and n % 5 == 0:
                    answers_text += "\n"
            text = (
                f"{self.test.name}\n\n"
                f"<b>{_('Your result:')} "
                "{correct}/{all_number}</b>\n\n"
                f"{_('Your answers:')}\n"
                "<blockquote expandable>"
                "{answers_text}"
                "</blockquote>"
            ).format(
                correct=correct,
                all_number=correct + incorrect,
                answers_text=answers_text
            )
        elif self.test.result_display_mode == self.test.TestResultDisplayMode.CORRECT_COUNT_ONLY:
            correct, incorrect = self.count_correct_incorrect()
            text = (
                f"{self.test.name}\n\n"
                f"<b>{_('Your result:')} "
                "{correct}/{all_number}</b>\n\n"
                f"{_('Your answers:')}\n"
                f"<blockquote expandable>"
                f"{self.answers_text}"
                f"</blockquote>"
            ).format(
                correct=correct,
                all_number=correct + incorrect
            )
        elif self.test.result_display_mode == self.test.TestResultDisplayMode.ONLY_SELECTED:
            text = (
                f"{self.test.name}\n\n"
                f"{_('Your answers:')}\n\n"
                f"<blockquote expandable>"
                f"{self.answers_text}"
                f"</blockquote>"
            )
        else:
            text = str(_("Not found!"))

        return text

    def __str__(self):
        return f"{self.user}"

    class Meta:
        verbose_name = _('User answer')
        verbose_name_plural = _('User answers')


class BaseCourseManager(models.Manager):
    def get_text(self):
        course = self.get_queryset().filter(is_active=True)
        if not course.exists():
            return str(_("Course information is not available!"))
        else:
            return course.first().about

class BaseCourse(models.Model):
    about = models.TextField(verbose_name=_('About the course'), blank=True)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)

    status = models.IntegerField(verbose_name=_('Status'), choices=Status.choices, default=Status.NOTSET, editable=False)

    def __str__(self):
        return text_reducer(self.about, 40)

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        ordering = ['id']


class BaseChannelManager(models.Manager):
    def get_channels(self):
        return [
            {
                'name': channel.name,
                'username': channel.username,
            } for channel in self.get_queryset().filter(is_active=True).all()
        ]

    def get_text(self):
        return '\n'.join(
            [
                f"{n + 1}. <a href='{channel['username']}'>{channel['name']}</a>"
                for n, channel in enumerate(self.get_channels())
            ]
        )


class BaseChannel(models.Model):
    name = models.CharField(verbose_name=_('Channel name'), max_length=100)
    username = models.CharField(
        verbose_name=_("Channel username"),
        max_length=255,
        help_text=_("Example: https://t.me/username")
    )

    status = models.IntegerField(verbose_name=_('Status'), choices=Status.choices, default=Status.NOTSET, editable=False)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Channel")
        verbose_name_plural = _("Channels")

class BaseLesson(models.Model):
    name = models.CharField(verbose_name=_('Lesson name'), max_length=100)
    video_file = models.FileField(verbose_name=_('Video file'), upload_to='videos/')
    file_id = models.CharField(verbose_name=_('File ID'), max_length=100, editable=False)
    saved_file_path = models.CharField(_('Saved File Path'), max_length=255, null=True, blank=True, editable=False)
    protect_content = models.BooleanField(verbose_name=_('Protect content'), default=False)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    description = models.TextField(verbose_name=_('Description'), blank=True, default='')

    status = models.IntegerField(verbose_name=_('Status'), choices=Status.choices, default=Status.NOTSET, editable=False)
    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    def is_file_synchronized(self):
        return self.video_file.path == self.saved_file_path

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_file_synchronized():
            return

        if self.video_file and self.video_file.path:
            try:
                with open(self.video_file.path, 'rb') as f:
                    response = tele_bot.send_video(
                        chat_id=settings.DEFAULT_BOT_CHAT,
                        video=f
                    )
            except Exception as e:
                logging.error(f"Telegram fayl yuborishda xatolik: {e}")
                return
            else:
                self.file_id = response.video.file_id
                self.saved_file_path = self.video_file.path
                super().save(update_fields=["file_id", "saved_file_path"])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Video lesson")
        verbose_name_plural = _("Video lessons")
        ordering = ('id',)
