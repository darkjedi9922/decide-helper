#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import dhelper.base as dhelper
import dhelper.tbot as tbot
import telegram
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def new(bot, update):
    tbot.Session.new(update)

def addAlts(bot, update):
    session = tbot.Session.require(update)
    session.setState(tbot.Session.ADDING_ALTS_STATE)
    update.message.reply_text("Введите альтернативы (одно на сообщение)")

def addFactors(bot, update):
    session = tbot.Session.require(update)
    session.setState(tbot.Session.ADDING_FACTORS_STATE)
    update.message.reply_text("Введите факторы (одно на сообщение)")

def showAlts(bot, update):
    session = tbot.Session.require(update)
    session.setState(tbot.Session.SHOWN_ALTS_STATE)
    net = session.getNet()
    reply = "\n".join(alt.getName() for alt in net.getAlternativeIterator())
    if reply:
        update.message.reply_text(reply)

def showFactors(bot, update):
    session = tbot.Session.require(update)
    session.setState(tbot.Session.SHOWN_FACTORS_STATE)
    net = session.getNet()
    reply = "\n".join(factor.getName() for factor in net.getFactorIterator())
    if reply:
        update.message.reply_text(reply)

def setupAlts(bot, update):
    pass
    #setState(update, "setup-alts")

def setupFactors(bot, update):
    pass
    #setState(update, "setup-factors")

def decide(bot, update):
    session = tbot.Session.require(update)
    net = session.getNet()
    decision = net.decide()
    lines = [item[0].getName() + ": " + str(item[1]) for item in decision.sort()]
    reply = "\n".join(lines)
    if reply:
        update.message.reply_text(reply)

def stop(bot, update):
    tbot.Session.stop(update)

# Text handler to handle text messages
def textHandler(bot, update):
    session = tbot.Session.require(update)
    net = session.getNet()
    state = session.getState()
    if state == tbot.Session.ADDING_ALTS_STATE:
        net.addAlternative(dhelper.Alternative(update.message.text)) 
    elif state == tbot.Session.ADDING_FACTORS_STATE:
        net.addFactor(dhelper.Factor(update.message.text))

def askAltCompare(bot, update):
    """
    chatId = update.effective_chat.id
    if chatId not in chats:
        update.message.reply_text("Сначала введите команду /decide")
        return
    altCombinationGen = chats[chatId]["altCombinationGen"]
    """
    pass

def errorHandler(bot, update, error):
    try:
        raise error
    except tbot.SessionIsNotStartedError:
        update.message.reply_text("Сначала введите команду /new")
    except telegram.TelegramError:
        # handle all other telegram related errors
        logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    updater = Updater("634780311:AAHPQxaVkPv522pKwiMKxu5NrIzz1NVKXtY")
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("new", new))
    dp.add_handler(CommandHandler("addAlts", addAlts))
    dp.add_handler(CommandHandler("addFactors", addFactors))
    dp.add_handler(CommandHandler("showAlts", showAlts))
    dp.add_handler(CommandHandler("showFactors", showFactors))
    dp.add_handler(CommandHandler("setupAlts", setupAlts))
    dp.add_handler(CommandHandler("setupFactors", setupFactors))
    dp.add_handler(CommandHandler("decide", decide))
    dp.add_handler(CommandHandler("stop", stop))

    dp.add_handler(MessageHandler(Filters.text, textHandler))
    dp.add_error_handler(errorHandler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()