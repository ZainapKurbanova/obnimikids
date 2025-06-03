import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from .telegram_bot import application

@csrf_exempt
async def telegram_webhook(request):
    if request.method == 'POST':
        try:
            update = Update.de_json(json.loads(request.body.decode('utf-8')), application.bot)
            await application.process_update(update)
            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)
    return HttpResponse(status=405)