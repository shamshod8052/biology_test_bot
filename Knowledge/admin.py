from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from Knowledge.models import BaseAnswer, BaseDiagnosticTest, BaseCourse, BaseChannel, BaseUserAnswer, BaseLesson, Status
from helpers.reducer import text_reducer


class BaseAnswerInline(admin.TabularInline):
    model = BaseAnswer
    extra = 1
    fields = ('order', 'value', 'type')
    show_change_link = True
    readonly_fields = ('order',)

    def order(self, obj):
        if obj.test:
            answer_count = obj.test.answers.filter(id__lte=obj.id).count()
            return answer_count
        return "-"

    order.short_description = "№"


class BaseUserAnswerInline(admin.TabularInline):
    model = BaseUserAnswer
    extra = 0
    fields = ('order', 'user', 'view_answers', 'result')
    readonly_fields = ('order', 'user', 'view_answers', 'result')

    def has_add_permission(self, request, obj=None):
        return False

    def order(self, obj):
        if obj.test:
            user_answer_count = obj.test.user_answers.filter(id__lte=obj.id).count()
            return user_answer_count
        return "-"

    order.short_description = "№"

    def result(self, obj: BaseUserAnswer):
        return f"{obj.count_correct_incorrect()[0]}/{obj.test.answers.count()}"

    result.short_description = _('Result')

    def view_answers(self, obj):
        if not obj.pk:
            return '-'

        # HTML content yaratish
        answer_items_html = ""
        for ans in obj.get_user_result():
            icon = "&#10004;" if ans["correct"] else "&#10060;"
            answer_items_html += f"""
                        <div class="answer-item">
                            <span>{ans['number']}.</span>
                            <span>{ans['text']}</span>
                            <span class="icon">{icon}</span>
                        </div>
                    """

        return mark_safe(
            f"""
                <button type="button" class="btn btn-primary open-modal" data-target="modal-{obj.pk}">
                    {_('View answers')}
                </button>

                <div id="modal-{obj.pk}" class="custom-modal-overlay">
                  <div class="custom-modal">
                    <span class="custom-close-btn" data-target="modal-{obj.pk}">&times;</span>
                    <h2>{obj.user.full_name}</h2>
                    <p><strong>ID:</strong> {obj.user.telegram_id}</p>
                    <hr>
                    <div class="answer-grid">
                        {answer_items_html}
                    </div>
                  </div>
                </div>
            """
        )

    class Media:
        css = {
            'all': ('css/modal.css',)
        }
        js = (
            'js/modal.js',
        )

    view_answers.short_description = _('Answers')

@admin.register(BaseUserAnswer)
class BaseUserAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'test', 'short_answers', 'correct_result')
    list_filter = ('test', 'user')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'test__name')
    ordering = ('-id',)

    def short_answers(self, obj):
        """Answers text ni qisqacha ko'rsatish."""
        return text_reducer(obj.answers_text, 20)

    short_answers.short_description = _("Answers Text")

    def correct_result(self, obj):
        """Nechta to'g'ri javob berilgan / nechta umumiy savol borligini ko'rsatish."""
        correct, incorrect = obj.count_correct_incorrect()
        total = obj.test.answers.count()
        return f"{correct}/{total}"

    correct_result.short_description = _("Result")


@admin.register(BaseDiagnosticTest)
class BaseDiagnosticTestAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'file_synchronized_status', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    inlines = [BaseAnswerInline, BaseUserAnswerInline]

    @admin.display(description='Is file synchronized', boolean=True)
    def file_synchronized_status(self, obj: BaseDiagnosticTest):
        return obj.is_file_synchronized()


@admin.register(BaseCourse)
class BaseCourseAdmin(admin.ModelAdmin):
    list_display = ('short_about', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('about',)

    def short_about(self, obj):
        return text_reducer(obj.about, 40)
    short_about.short_description = _('About')


@admin.register(BaseChannel)
class BaseChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'username')


@admin.register(BaseLesson)
class BaseLessonAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'file_synchronized_status', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status=Status.NOTSET)

    @admin.display(description='Is video synchronized', boolean=True)
    def file_synchronized_status(self, obj):
        return obj.is_file_synchronized()
