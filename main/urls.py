from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.decorators.cache import never_cache
from ckeditor_uploader import views as ckeditor_views

from bot.views import process_update

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/upload/', ckeditor_views.upload, name='ckeditor_upload'),
    path('ckeditor/browse/', never_cache(ckeditor_views.browse), name='ckeditor_browse'),
    path("webhook/<str:token>/", process_update, name="bot-process-updates"),
]

if settings.DEBUG:
    urlpatterns += [
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]
