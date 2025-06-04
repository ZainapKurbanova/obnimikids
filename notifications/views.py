from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from push_notifications.models import WebPushDevice

@login_required
@csrf_exempt
@require_POST
def subscribe(request):
    try:
        subscription_data = request.body.decode('utf-8')
        import json
        subscription = json.loads(subscription_data)

        # Создаём устройство для пользователя
        WebPushDevice.objects.create(
            user=request.user,
            registration_id=subscription['endpoint'],
            p256dh=subscription['keys']['p256dh'],
            auth=subscription['keys']['auth'],
        )
        return JsonResponse({"status": "success"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)