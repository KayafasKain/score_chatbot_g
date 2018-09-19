from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from .chat_bot_core import ChatBotCore

# Create your views here.
import telepot
from telepot.loop import MessageLoop
TelegramBot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)

def handle(request):
    ChatBotCore(request, TelegramBot)


MessageLoop(TelegramBot, handle).run_as_thread()