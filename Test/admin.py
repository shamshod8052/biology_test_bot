from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin

from .models import (
    Title,
    Test,
    Question,
    Photo,
    Option,
    Task,
    Participant,
    Quest,
)

@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'type', 'is_active', 'created_at', 'updated_at']
    list_filter = ['type', 'is_active', 'title', 'shuffle_questions']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'


class AnswerInline(admin.TabularInline):
    model = Option
    extra = 0


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0


@admin.register(Question)
class QuestionAdmin(OrderedModelAdmin):
    list_display = ['__str__', 'test', 'time_limit', 'shuffle_answers', 'order', 'move_up_down_links']
    list_filter = ['test', 'shuffle_answers']
    search_fields = ['text', 'explanation']
    inlines = [AnswerInline, PhotoInline]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'question']
    list_filter = ['question__test']


@admin.register(Option)
class AnswerAdmin(OrderedModelAdmin):
    list_display = ['text', 'question', 'is_correct', 'order', 'move_up_down_links']
    list_filter = ['question__test', 'is_correct']
    search_fields = ['text']


class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 0
    readonly_fields = ['username', 'fullname', 'telegram_id', 'correct', 'incorrect', 'time_spent']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['code', 'chat', 'language', 'is_started', 'started_at', 'created_at']
    list_filter = ['is_started', 'language']
    search_fields = ['code', 'chat__username']
    readonly_fields = ['code', 'poll_id']
    date_hierarchy = 'created_at'
    inlines = [ParticipantInline]


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['fullname', 'task', 'correct', 'incorrect', 'time_spent']
    list_filter = ['task__is_started']
    search_fields = ['fullname']
    readonly_fields = ['task', 'fullname', 'telegram_id', 'correct', 'incorrect', 'time_spent']


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'task', 'question', 'status']
    list_filter = ['status', 'task']
    readonly_fields = ['task', 'question', 'meta']