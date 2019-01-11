#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler
import dhelper.base as dhelper
import dhelper.tbot.base as tbot
import dhelper.tbot.actions as actions
import telegram
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def errorHandler(bot, update, error):
    try:
        raise error
    except tbot.SessionIsNotStartedError:
        chatId = update.effective_chat.id
        bot.send_message(chatId, "Сначала введите команду /new")
    except telegram.TelegramError:
        # handle all other telegram related errors
        logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    updater = Updater("634780311:AAHPQxaVkPv522pKwiMKxu5NrIzz1NVKXtY")
    dp = updater.dispatcher
    dp = tbot.DialogDispatcher(dp.bot, dp.update_queue)
    updater.dispatcher = dp

    dp.add_handler(CommandHandler("new", actions.new))
    dp.add_handler(CommandHandler("addAlts", actions.addAlts))
    dp.add_handler(CommandHandler("addFactors", actions.addFactors))
    dp.add_handler(CommandHandler("showAlts", actions.showAlts))
    dp.add_handler(CommandHandler("showFactors", actions.showFactors))
    dp.add_handler(CommandHandler("setupAlts", actions.askingAltSetup))
    dp.add_handler(CommandHandler("setupFactors", actions.askingFactorSetup))
    dp.add_handler(CommandHandler("decide", actions.decide))
    dp.add_handler(CommandHandler("stop", actions.stop))

    dp.add_error_handler(errorHandler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()