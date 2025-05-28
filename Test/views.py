from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Test, Option


@csrf_exempt
def update_test_order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        order = data.get('order', [])
        for index, obj_id in enumerate(order):
            Test.objects.filter(id=obj_id).update(order=index + 1)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)


@csrf_exempt
def update_answer_order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        order = data.get('order', [])
        for index, obj_id in enumerate(order):
            Option.objects.filter(id=obj_id).update(order=index + 1)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)
