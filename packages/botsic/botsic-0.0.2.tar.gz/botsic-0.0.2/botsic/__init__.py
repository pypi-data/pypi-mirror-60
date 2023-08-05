import os

from telegram.ext import Updater
from telegram.ext import CommandHandler


class Bot(object):
    def __init__(self):
        self.updater = Updater(
            token=os.getenv('TELEGRAM_TOKEN'),
            use_context=True)
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('help', self.help))
        self.dispatcher.add_handler(CommandHandler('settings', self.settings))

    @property
    def dispatcher(self):
        return self.updater.dispatcher

    def start(self, update, context):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="I'm a bot, please talk to me!")

    def help(self, update, context):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You asked for help, but I don't know my purpose")

    def settings(self, update, context):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You asked for my settings. I only have my Telegram token, and I'm not going to tell you that.")

    def run(self):
        self.updater.start_polling()
