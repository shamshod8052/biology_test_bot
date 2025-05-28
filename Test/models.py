import time
import uuid
from typing import Any, List, Optional, Self, Union

from aiogram import Bot
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, QuerySet
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from ordered_model.models import OrderedModel, OrderedModelManager, OrderedModelQuerySet
from shortuuid.django_fields import ShortUUIDField

from helpers.reducer import text_reducer
from helpers.tele_bot import tele_bot
from helpers.time_string import seconds_to_text
from Admin.models import User


class TitleManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)


class Title(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Title name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active"))

    objects = TitleManager()

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Title")
        verbose_name_plural = _("Titles")


class TestQuerySet(QuerySet):
    def active(self) -> Self:
        return self.filter(is_active=True)

    def of_type(self, type_value: int) -> Self:
        return self.filter(type=type_value)


class TestManager(models.Manager):
    def get_queryset(self) -> TestQuerySet:
        return TestQuerySet(self.model, using=self._db)

    def active(self) -> TestQuerySet:
        return self.get_queryset().active()

    def quiz(self) -> TestQuerySet:
        return self.active().of_type(Test.Type.QUIZ)

    def inline(self) -> TestQuerySet:
        return self.active().of_type(Test.Type.INLINE)


class Test(models.Model):
    class Type(models.IntegerChoices):
        QUIZ = 1, _("Quiz")
        INLINE = 2, _("Inline")

    type = models.IntegerField(
        choices=Type.choices,
        default=Type.QUIZ,
        verbose_name=_("Question type"),
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="tests",
        verbose_name=_("Test title"),
    )
    name = models.CharField(max_length=200, verbose_name=_("Test name"))
    time_limit = models.PositiveIntegerField(
        default=30, blank=True, null=True,
        verbose_name=_('Time limit (sec)'), help_text=_('Seconds to answer every quiz'),
    )
    shuffle_questions = models.BooleanField(default=False, verbose_name=_("Shuffle questions"))
    protect_content = models.BooleanField(default=True, verbose_name=_("Protect content"))
    show_answer = models.BooleanField(default=True, verbose_name=_("Show true answer"))
    is_active = models.BooleanField(default=False, verbose_name=_("Active"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    objects = TestManager()

    def __str__(self) -> str:
        return self.name

    def full_info(self) -> str:
        return _(
            "♻️ {topic}\n\n"
            "🖊 {quest_num} questions\n"
            "💬 {test_type}\n"
            "{wait_time_text}"
            "🏁 When you're ready, click the button below."
        ).format(
            topic=f"{self.title} / {self.name}",
            quest_num=self.questions.count(),
            test_type=self.get_type_display(),
            wait_time_text=f"⏱️ {seconds_to_text(self.time_limit)} per question\n\n"
            if self.type == self.Type.QUIZ
            else '\n'
        )

    class Meta:
        verbose_name = _("Test")
        verbose_name_plural = _("Tests")
        ordering = ['-id']


class QuestionQuerySet(OrderedModelQuerySet):
    def for_test(self, test: Test) -> Self:
        return self.filter(test=test)

    def pending(self) -> Self:
        return self.filter(quests__status=Quest.Status.NOTSET)


class QuestionManager(OrderedModelManager):
    def get_queryset(self) -> QuestionQuerySet:
        return QuestionQuerySet(self.model, using=self._db)

    def for_test(self, test: Test) -> QuestionQuerySet:
        return self.get_queryset().for_test(test)

    def pending(self) -> QuestionQuerySet:
        return self.get_queryset().pending()


class Question(OrderedModel):
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name=_('Test'),
    )
    text = models.TextField(verbose_name=_('Question text'))
    time_limit = models.PositiveIntegerField(
        default=0, blank=True, null=True,
        verbose_name=_('Time limit (sec)'), help_text=_('Seconds to answer quiz'),
    )
    shuffle_answers = models.BooleanField(default=False, verbose_name=_('Shuffle answers'))
    explanation = models.TextField(blank=True, null=True, verbose_name=_('Explanation'))

    objects = QuestionManager()

    class Meta(OrderedModel.Meta):
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        ordering = ['test', 'order']

    def __str__(self) -> str:
        return text_reducer(self.text, 32)

    def clean(self) -> None:
        if self.test.type == Test.Type.QUIZ and not self.time_limit:
            raise ValidationError({'time_limit': _("Time limit required for quiz questions.")})

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        self.full_clean()

    def get_answers(self) -> List['Option']:
        qs = self.options.all()
        return list(qs.order_by('?')) if self.shuffle_answers else list(qs.order_by('order'))


class PhotoManager(models.Manager):
    def for_question(self, question: Question) -> QuerySet:
        return self.filter(question=question)


class Photo(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='photos', verbose_name=_('Question'))
    image = models.ImageField(upload_to='photos', verbose_name=_('Image'))
    file_id = models.TextField(verbose_name=_('Telegram file ID'), null=True, blank=True, editable=False)

    objects = PhotoManager()

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        with open(self.image.path, 'rb') as f:
            resp = tele_bot.send_photo(chat_id=settings.DEFAULT_BOT_CHAT, photo=f)
        self.file_id = resp.photo[-1].file_id
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.image.name)

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')


class AnswerManager(OrderedModelManager):
    def get_queryset(self):
        return super().get_queryset()

    def get_correct(self) -> Optional['Option']:
        return self.get_queryset().filter(is_correct=True).first()

    def incorrect(self) -> QuerySet:
        return self.get_queryset().filter(is_correct=False)


class Option(OrderedModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options', verbose_name=_('Question'))
    text = models.TextField(verbose_name=_('Option text'))
    is_correct = models.BooleanField(default=False, verbose_name=_('Is correct option'), help_text=_('Only one correct for quizzes'))

    objects = AnswerManager()

    # def clean(self) -> None:
    #     if self.is_correct and self.question.test.type == Test.Type.QUIZ:
    #         existing = self.question.answers.filter(is_correct=True)
    #         if existing.exists():
    #             raise ValidationError(_('A quiz can have only one correct answer.'))

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta(OrderedModel.Meta):
        verbose_name = _('Option')
        verbose_name_plural = _('Options')
        ordering = ['question', 'order']


class TaskQuerySet(QuerySet):
    def for_user(self, user: User) -> Self:
        return self.filter(chat=user)

    def active(self) -> Self:
        return self.filter(is_started=True)


class TaskManager(models.Manager):
    def get_queryset(self) -> TaskQuerySet:
        return TaskQuerySet(self.model, using=self._db)

    def for_user(self, user: User) -> TaskQuerySet:
        return self.get_queryset().for_user(user)

    def active(self) -> TaskQuerySet:
        return self.get_queryset().active()

    def create_for_user(self, user: User) -> 'Task':
        return self.create(chat=user)


class Task(models.Model):
    code = ShortUUIDField(primary_key=True, length=8, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', verbose_name=_('User chat'))
    language = models.CharField(max_length=15, choices=settings.LANGUAGES, default=settings.LANGUAGES[0][0], verbose_name=_('Language'))
    is_started = models.BooleanField(default=False, verbose_name=_('Started'))
    started_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Started at'))
    poll_id = models.CharField(verbose_name=_('Poll ID'), max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = TaskManager()

    def __str__(self) -> str:
        return str(self.code)

    @property
    def test(self) -> Optional[Test]:
        return self.quests.first().question.test if self.quests.exists() else None

    def start(self) -> None:
        if self.is_started:
            return
        self.participants.get_or_create(
            fullname=self.chat.full_name,
            username=self.chat.username,
            telegram_id=self.chat.telegram_id
        )
        self.is_started = True
        self.started_at = now()
        self.save(update_fields=['is_started', 'started_at'])

    def stop(self) -> None:
        if not self.is_started:
            return
        self.is_started = False
        self.save(update_fields=['is_started'])

    def add_questions(self, *questions: Question) -> None:
        for q in questions:
            try:
                q.full_clean()
            except ValidationError as e:
                pass
            else:
                Quest.objects.create(task=self, question=q)

    @property
    def last_quest(self):
        return self.quests.filter(status=Quest.Status.PENDING).first()

    def get_next(self) -> 'Quest':
        qs = self.quests.filter(status=Quest.Status.NOTSET)
        if not qs.exists():
            raise ValueError(_('No remaining questions'))
        return qs.order_by('?').first() if self.test.shuffle_questions else qs.order_by('question__order').first()

    async def stop_poll(self, bot: Bot) -> None:
        if not self.last_quest:
            return
        message_id = self.last_quest.meta.get('message_id')
        if message_id and self.test.type == Test.Type.QUIZ:
            try:
                await bot.stop_poll(self.chat.telegram_id, message_id)
            except Exception as e:
                pass

    def add_points4gamer(
            self, telegram_id: Union[int, str], full_name: Optional[str], username: Optional[str], answer: int
    ):
        try:
            gamer = self.participants.get(telegram_id=telegram_id)
        except Participant.DoesNotExist:
            gamer = self.participants.create(full_name=full_name, username=username, telegram_id=telegram_id)
        gamer.correct += answer == self.last_quest.meta.get('correct_id')
        gamer.incorrect += answer != self.last_quest.meta.get('correct_id')
        gamer.time_spent += time.time() - self.last_quest.meta.get('sent_time')
        gamer.save()

    class Meta:
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
        constraints = [
            models.UniqueConstraint(fields=['chat'], condition=Q(is_started=True), name='unique_started_task_per_chat')
        ]


class ParticipantManager(models.Manager):
    def for_user(self, user: User) -> QuerySet:
        return self.filter(user=user)

    def leaderboard(self) -> QuerySet:
        return self.order_by('-correct', 'incorrect')


class Participant(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='participants', verbose_name=_('Task'))
    fullname = models.CharField(_("Full name"), max_length=150, blank=True)
    username = models.CharField(_("Username"), max_length=150, null=True, blank=True)
    telegram_id = models.BigIntegerField(null=True, blank=True)

    correct = models.PositiveIntegerField(default=0, verbose_name=_('Correct'))
    incorrect = models.PositiveIntegerField(default=0, verbose_name=_('Incorrect'))
    time_spent = models.FloatField(default=0.0, verbose_name=_('Time spent(s)'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    objects = ParticipantManager()

    def __str__(self) -> str:
        return text_reducer(self.fullname, 32)

    class Meta:
        verbose_name = _('Participant')
        verbose_name_plural = _('Participants')


class Quest(models.Model):
    class Status(models.IntegerChoices):
        NOTSET = 0, _('Not set')
        PENDING = 1, _('Pending')
        ANSWERED = 2, _('Answered')

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='quests', verbose_name=_('Task'))
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='quests', verbose_name=_('Question'))
    status = models.IntegerField(choices=Status.choices, default=Status.NOTSET, verbose_name=_('Status'))
    meta = models.JSONField(default=dict, verbose_name=_('Meta'))

    def __str__(self) -> str:
        return f"{self.task.code} - Q{self.question.order}"

    def set_pending(self) -> None:
        self.status = self.Status.PENDING
        self.save()

    def set_answered(self) -> None:
        self.status = self.Status.ANSWERED
        self.save()

    class Meta:
        verbose_name = _('Quest')
        verbose_name_plural = _('Quests')
        constraints = [
            models.UniqueConstraint(fields=['task'], condition=Q(status=1), name='unique_pending_quest_per_task')
        ]
