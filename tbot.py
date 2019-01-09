#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import dhelper.base as dhelper
import dhelper.tbot.base as tbot
import dhelper.tbot.actions as actions
import telegram
import logging
import inspect

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Text handler to handle text messages
def textHandler(bot, update):
    session = tbot.Session.require(update)
    
    if session.activeGenerator:
        try:
            question = session.activeGenerator.send(update.message.text)
            # Вопроса может не быть, тогда генератор просто ожидает ответ.
            if question:
                update.message.reply_text(question)
            return
        except StopIteration:
            session.activeGenerator = None
        except Exception:
            session.activeGenerator = None
            raise

def errorHandler(bot, update, error):
    try:
        raise error
    except tbot.SessionIsNotStartedError:
        update.message.reply_text("Сначала введите команду /new")
    except telegram.TelegramError:
        # handle all other telegram related errors
        logger.warning('Update "%s" caused error "%s"', update, error)

def setCommandHandler(updater, command, callback):

    # Непосредственно выполняться как команда, собственно, будет wrapper.
    def wrapper(bot, update):

        # Коллбек выполняется независимо от того, генератор это или нет.
        # Если это не генератор, он просто вернет None.
        result = callback(bot, update)

        if not inspect.isgenerator(result):

            # Если был включен генератор, и пользователь перебил его вызовом
            # новой команды, установленной с помощью этой функции, тот 
            # генератор нужно отключить.
            session = tbot.Session.get(update)
            if session:
                session.activeGenerator = None

            # Так как это генератор, а дальше у нас действия по работе с
            # коллбеком как с генератором, делать нам больше тут нечего.
            return

        # Иначе, если эта команда запускает новый генератор, нужно активировать
        # этот новый генератор.
        session = tbot.Session.require(update)
        session.activeGenerator = result
        try:

            # Чтобы далее передавать значения в генератор через .send(), нам
            # нужно дойти до первого возвращаемого через yield вопроса.
            # Этот кусок кода будет выполнен только первый раз при выполнении
            # этого ненератора.
            firstQuestion = next(session.activeGenerator)

            # Вопроса может не быть, тогда генератор просто ожидает ответ.
            if firstQuestion:
                update.message.reply_text(firstQuestion)

        except StopIteration:
            session.activeGenerator = None
        except Exception:
            session.activeGenerator = None
            raise

    dp = updater.dispatcher
    dp.add_handler(CommandHandler(command, wrapper))

def main():
    updater = Updater("634780311:AAHPQxaVkPv522pKwiMKxu5NrIzz1NVKXtY")
    dp = updater.dispatcher

    setCommandHandler(updater, "new", actions.new)
    setCommandHandler(updater, "addAlts", actions.addAlts)
    setCommandHandler(updater, "addFactors", actions.addFactors)
    setCommandHandler(updater, "showAlts", actions.showAlts)
    setCommandHandler(updater, "showFactors", actions.showFactors)
    setCommandHandler(updater, "setupAlts", actions.askingAltSetup)
    setCommandHandler(updater, "setupFactors", actions.askingFactorSetup)
    setCommandHandler(updater, "decide", actions.decide)
    setCommandHandler(updater, "stop", actions.stop)

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