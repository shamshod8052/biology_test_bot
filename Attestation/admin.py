from django.contrib import admin

from Attestation.models import DiagnosticTest, Course, Channel, Lesson
from Knowledge.admin import BaseChannelAdmin, BaseCourseAdmin, BaseLessonAdmin
from Knowledge.models import Status


@admin.register(DiagnosticTest)
class DiagnosticTestAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_active')
    search_fields = ('text',)
    list_filter = ('is_active',)


@admin.register(Course)
class CourseAdmin(BaseCourseAdmin):
    pass


@admin.register(Channel)
class ChannelAdmin(BaseChannelAdmin):
    pass


@admin.register(Lesson)
class LessonAdmin(BaseLessonAdmin):
    def get_queryset(self, request):
        return Lesson.objects.filter(status=Status.ATTESTATION)
