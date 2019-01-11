from .. import base as dhelper
from telegram.ext import *
from telegram.ext.dispatcher import *
import telegram
import inspect

class SessionIsNotStartedError(telegram.TelegramError):
    def __init__(self):
        super().__init__("")

class Session:
    _instances = {}

    @classmethod
    def new(cls, update):
        chatId = update.effective_chat.id
        Session._instances[chatId] = Session(chatId)

    @classmethod
    def get(cls, update):
        chatId = update.effective_chat.id
        if chatId not in Session._instances:
            return None
        session = Session._instances[chatId]
        return session

    @classmethod
    def require(cls, update):
        session = Session.get(update)
        if not session:
            raise SessionIsNotStartedError
        return session

    @classmethod
    def stop(cls, update):
        chatId = update.effective_chat.id
        if chatId in Session._instances:
            del Session._instances[chatId]

    def __init__(self, chatId):
        self._net = dhelper.Net()
        self._chatId = chatId
        self.setActiveDialog(None)

    def getChatId(self):
        return self._chatId

    def getNet(self):
        return self._net

    def setActiveDialog(self, callback):
        self._activeGenerator = callback

    def getActiveDialog(self):
        return self._activeGenerator

class DialogDispatcher(Dispatcher):
    def __init__(self, bot, update_queue):
        super().__init__(bot, update_queue)

        # Этот автоматически устанавливаемый обработчик отправляет ответ в
        # диалог, когда это нужно.
        def textHandler(bot, update):
            session = Session.get(update)
            dialog = session.getActiveDialog() if session else None
            if dialog:
                try:
                    question = dialog.send(update.message.text)
                    
                    # Вопроса может не быть, тогда генератор просто ожидает ответ.
                    if question:
                        chatId = session.getChatId()
                        bot.send_message(chatId, question)

                    return
                except StopIteration:
                    session.setActiveDialog(None)
                except Exception:
                    session.setActiveDialog(None)
                    raise

                # Если сейчас ведется диалог, то не нужно после этого обработчика
                # обрабатывать остальные в других группах. Для остановки
                # обработки нужно выбросить такое исключение.
                raise DispatcherHandlerStop("Dialog text handler acted.")

        # Этот обработчик находится первым в -1 группе, а значит он имеет
        # наивысший приоритет, а значит для всех сообщений с текстом, сначала
        # будет выполнятся этот обработчик, работающий с активным диалогом,
        # если такой есть.
        super().add_handler(MessageHandler(Filters.text, textHandler), group=-1)

    def add_handler(self, handler, group=DEFAULT_GROUP):
        # Группа не может быть меньше 0, потому что такие группы уже используюся
        # в приватных целях.
        if group < 0:
            raise Exception("Handler group less than 0")

        # Нужно окружить callback "декоратором", который будет позволять выполнять
        # его как диалог. При этом мы работаем с тем же объектом обработчика.
        handler.callback = self._wrap_handler(handler.callback)

        # Если понадобится удалить этот обработчик, в соответствующем методе нужно
        # будет передавать тот же объект обработчика. Так как сюда мы добавляем,
        # собственно, тот же объект, то он удалится нормально.
        super().add_handler(handler, group)

    def remove_handler(self, handler, group=DEFAULT_GROUP):
        # Нельзя удалять обработчики с групп < 0, потому что такие группы уже 
        # используюся в приватных целях.
        if group < 0:
            return
        super().remove_handler(handler, group)

    def _wrap_handler(self, callback):
        # Непосредственно выполняться как команда, собственно, будет wrapper.
        def wrapper(bot, update):

            # Коллбек выполняется независимо от того, генератор это или нет.
            # Если это не генератор, он просто вернет None.
            result = callback(bot, update)

            if not inspect.isgenerator(result):

                # Если был включен генератор, и пользователь перебил его вызовом
                # новой команды, установленной с помощью этой функции, тот 
                # генератор нужно отключить.
                session = Session.get(update)
                if session:
                    session.setActiveDialog(None)

                # Так как это генератор, а дальше у нас действия по работе с
                # коллбеком как с генератором, делать нам больше тут нечего.
                return

            # Иначе, если эта команда запускает новый генератор, нужно активировать
            # этот новый генератор.
            session = Session.require(update)
            session.setActiveDialog(result)
            try:

                # Чтобы далее передавать значения в генератор через .send(), нам
                # нужно дойти до первого возвращаемого через yield вопроса.
                # Этот кусок кода будет выполнен только первый раз при выполнении
                # этого ненератора.
                firstQuestion = next(result)

                # Вопроса может не быть, тогда генератор просто ожидает ответ.
                if firstQuestion:
                    chatId = session.getChatId()
                    bot.send_message(chatId, firstQuestion)

            except StopIteration:
                session.setActiveDialog(None)
            except Exception:
                session.setActiveDialog(None)
                raise

        return wrapper