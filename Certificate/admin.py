from django.contrib import admin

from Certificate.models import DiagnosticTest, Course, Channel, Lesson
from Knowledge.admin import BaseDiagnosticTestAdmin, BaseChannelAdmin, BaseCourseAdmin, BaseLessonAdmin
from Knowledge.models import Status


@admin.register(DiagnosticTest)
class DiagnosticTestAdmin(BaseDiagnosticTestAdmin):
    pass


@admin.register(Course)
class CourseAdmin(BaseCourseAdmin):
    pass


@admin.register(Channel)
class ChannelAdmin(BaseChannelAdmin):
    pass


@admin.register(Lesson)
class LessonAdmin(BaseLessonAdmin):
    def get_queryset(self, request):
        return Lesson.objects.filter(status=Status.CERTIFICATE)
