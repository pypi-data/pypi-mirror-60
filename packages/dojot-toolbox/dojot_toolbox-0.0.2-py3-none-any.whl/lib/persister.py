from .component import Component
from .optional import Optional
from .persistent import Persistent
from .optional import Optional
from .quantifiable import Quantifiable
from .authenticable import Authenticable
from .constants import persister as constants

class Persister(Component):

    def __init__(self):
        super().__init__()
        self._visible_name = constants['name']
        self.__persistence_time = 0
        self.__persistence_use = True
        self.__optional = Optional()
        self.__quantifiable = Quantifiable()

    def ask_if_messages_will_be_persisted(self):
        self.__persistence_use = self.__optional.ask_use(
            constants['persistence_use'], self.__persistence_use)
        return self

    def and_persistence_time(self):
        if self.__persistence_use:
            question = constants['persistence_time'].format(
                self.__persistence_time)
            self.__persistence_time = self.__quantifiable.ask_quantity(
                question, default=self.__persistence_time)
        return self

    
    @property
    def vars(self):
        self._vars['dojot_persister_use'] = self.__persistence_use
        self._vars['dojot_persister_persistence_time'] = self.__persistence_time
        return self._vars    