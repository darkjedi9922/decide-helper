from telegram import ReplyKeyboardMarkup
from ..tbot import base as tbot
from .. import base as dhelper
import itertools

def start(bot, update):
    # Кнопочки меню, которое будет показано внизу экрана
    custom_keyboard = [
        ['/new', '/decide', '/stop'],
        ['/addAlts', '/addFactors'],
        ['/showAlts', '/showFactors'],
        ['/setupAlts', '/setupFactors']
    ]
    chat_id = update.effective_chat.id
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    message = """
    Использование: 
    1. Выбрать /new для решения новой задачи
    2. Ввести альтернативы и факторы с помощью /addAlts и /addFactors соответственно.
    3. Установить отношения альтернатив и факторов с помощью /setupAlts и /setupFactors соответственно.
    4. /decide для расчета решения.

    Дополнительно:
    * /showAlts и /showFactors выводят список введенных альтернатив и факторов.
    * /stop заканчивает/прерывает текущую задачу.
    """
    bot.send_message(chat_id, message, reply_markup=reply_markup)

def new(bot, update):
    tbot.Session.new(update)

def addAlts(bot, update):
    session = tbot.Session.require(update)
    net = session.getNet()
    chatId = session.getChatId()
    bot.send_message(chatId, "Введите альтернативы (одно на сообщение)")
    while True:
        name = yield None
        net.addAlternative(dhelper.Alternative(name))

def addFactors(bot, update):
    session = tbot.Session.require(update)
    net = session.getNet()
    chatId = session.getChatId()
    bot.send_message(chatId, "Введите факторы (одно на сообщение)")
    while True:
        name = yield None
        net.addFactor(dhelper.Factor(name))

def showAlts(bot, update):
    session = tbot.Session.require(update)
    net = session.getNet()
    reply = "\n".join(alt.getName() for alt in net.getAlternativeIterator())
    if reply:
        chatId = session.getChatId()
        bot.send_message(chatId, reply)

def showFactors(bot, update):
    session = tbot.Session.require(update)
    net = session.getNet()
    reply = "\n".join(factor.getName() for factor in net.getFactorIterator())
    if reply:
        chatId = session.getChatId()
        bot.send_message(chatId, reply)

def askingAltSetup(bot, update):
    session = tbot.Session.require(update)
    message = "Для ввода в процентах (от 0 до 1) введите 1, для ввода в числах введите 0: "
    isProcent = yield message
    isProcent = True if isProcent == "1" else False
    net = session.getNet()
    for factor in net.getFactorIterator():
        alterCombinations = itertools.combinations(net.getAlternativeIterator(), 2)
        for comb in alterCombinations:
            message = comb[0].getName() + " vs " + comb[1].getName()
            message += " по фактору " + factor.getName() + ": "
            compare = yield message
            compare = float(compare)
            net.setAltCompare(factor, comb[0], comb[1], compare, isProcent)

def askingFactorSetup(bot, update):
    session = tbot.Session.require(update)
    message = "Для ввода в процентах (от 0 до 1) введите 1, для ввода в числах введите 0: "
    isProcent = yield message
    isProcent = True if isProcent == "1" else False
    net = session.getNet()
    combinations = itertools.combinations(net.getFactorIterator(), 2)
    for comb in combinations:
        message = comb[0].getName() + " vs " + comb[1].getName() + ": "
        compare = yield message
        compare = float(compare)
        net.setFactorCompare(comb[0], comb[1], compare, isProcent)

def decide(bot, update):
    session = tbot.Session.require(update)
    net = session.getNet()
    decision = net.decide()
    lines = [item[0].getName() + ": " + str(item[1]) for item in decision.sort()]
    reply = "\n".join(lines)
    if reply:
        chatId = session.getChatId()
        bot.send_message(chatId, reply)

def stop(bot, update):
    tbot.Session.stop(update)
