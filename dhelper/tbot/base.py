from .. import base as dhelper
import telegram

class SessionIsNotStartedError(telegram.TelegramError):
    def __init__(self):
        super().__init__("")

class Session:
    _instances = {}

    @classmethod
    def new(cls, update):
        chatId = update.effective_chat.id
        Session._instances[chatId] = Session(update)

    @classmethod
    def get(cls, update):
        chatId = update.effective_chat.id
        if chatId not in Session._instances:
            return None
        session = Session._instances[chatId]
        session.setUpdate(update)
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

    def __init__(self, update):
        self._net = dhelper.Net()
        self.setUpdate(update)
        
        self.activeGenerator = None

    def getNet(self):
        return self._net

    def setUpdate(self, update):
        self._update = update