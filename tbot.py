#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import dhelper.base as dhelper
import telegram
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

chats = {}

class SessionIsNotStartedError(telegram.TelegramError):
    def __init__(self):
        super().__init__("")

def requireNet(update):
    chatId = update.effective_chat.id
    if chatId not in chats:
        raise SessionIsNotStartedError()
    return chats[chatId]["net"]

def setState(update, state):
    chatId = update.effective_chat.id
    if chatId not in chats:
        raise SessionIsNotStartedError()
    chats[chatId]["state"] = state

def requireState(update):
    chatId = update.effective_chat.id
    if chatId not in chats:
        raise SessionIsNotStartedError()
    return chats[chatId]["state"]

def getState(update):
    """
    :return str or None
    """
    chatId = update.effective_chat.id
    if chatId in chats:
        return chats[chatId]["state"]
    return None

def newNet(update):
    chatId = update.effective_chat.id
    chats[chatId] = {"net": dhelper.Net(), "state": "net-created"}

def delNet(update):
    chatId = update.effective_chat.id
    del chats[chatId]

# Define command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def new(bot, update):
    newNet(update)

def addAlts(bot, update):
    setState(update, "adding-alts")
    update.message.reply_text("Введите альтернативы (одно на сообщение)")

def addFactors(bot, update):
    setState(update, "adding-factors")
    update.message.reply_text("Введите факторы (одно на сообщение)")

def showAlts(bot, update):
    setState(update, "shown-alts")
    net = requireNet(update)
    reply = "\n".join(alt.getName() for alt in net.getAlternativeIterator())
    if reply:
        update.message.reply_text(reply)

def showFactors(bot, update):
    setState(update, "shown-factors")
    net = requireNet(update)
    reply = "\n".join(factor.getName() for factor in net.getFactorIterator())
    if reply:
        update.message.reply_text(reply)

def setupAlts(bot, update):
    setState(update, "setup-alts")

def setupFactors(bot, update):
    setState(update, "setup-factors")

def decide(bot, update):
    net = requireNet(update)
    decision = net.decide()
    lines = [item[0].getName() + ": " + str(item[1]) for item in decision.sort()]
    reply = "\n".join(lines)
    if reply:
        update.message.reply_text(reply)

def stop(bot, update):
    #TODO: add if has net
    delNet(update)

# Text handler to handle text messages
def textHandler(bot, update):
    state = getState(update) # can be None
    if state == "adding-alts":
        net = requireNet(update)
        net.addAlternative(dhelper.Alternative(update.message.text)) 
    elif state == "adding-factors":
        net = requireNet(update)
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
    except SessionIsNotStartedError:
        update.message.reply_text("Сначала введите команду /new")
    except telegram.TelegramError:
        # handle all other telegram related errors
        logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    updater = Updater("634780311:AAHPQxaVkPv522pKwiMKxu5NrIzz1NVKXtY")
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
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