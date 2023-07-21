from . import bot
import discord
import os
from flask import Blueprint

bp = Blueprint('chalubot', __name__,
               url_prefix='/api/chalubot/')


@bp.route("/activate/")
def activate():
    if not bot.client.user:
        bot.client.run(os.getenv("BOT_TOKEN"))
    else:
        return 'ChaluBot is already active. <3'

@bp.route("/status/")
def status():
    return 'ChaluBot is active!' if bot.client.user else 'ChaluBot is offline. Activate it <a href="/api/chalubot/activate/">here</a>.'
