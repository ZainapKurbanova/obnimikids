import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from obnimikids.bot import dispatcher

@csrf_exempt
async def telegram_webhook(request):
    if request.method == 'POST':
        try:
            update = Update.de_json(json.loads(request.body), dispatcher.bot)
            await dispatcher.process_update(update)
            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=400)
    return HttpResponse("Method not allowed", status=405)