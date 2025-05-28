from django.urls import path
from .views import update_test_order, update_answer_order

urlpatterns = [
    path('update-test-order/', update_test_order, name='update_test_order'),
    path('update-ans-order/', update_answer_order, name='update_answer_order'),
]
