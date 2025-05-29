from django.core.paginator import Paginator


def get_objects_text(queryset, atr_name, rows_num, page_num=1):
    paginated = Paginator(queryset, rows_num)
    page = paginated.page(page_num)
    text = f"\n"
    for n, lesson in enumerate(page.object_list, 1 + (page.number - 1) * rows_num):
        text += f"\n<b>{n}.</b> {getattr(lesson, atr_name)}"

    return text.strip()
