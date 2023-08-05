from .component import Component
from .optional import Optional
from .scalable import Scalable
from .constants import cron as constants

class Cron(Component):

    def __init__(self):
        super().__init__()
        self.__use = False
        self.__name = constants['name']
        self._visible_name =  constants['name']


    def ask_use(self):
        self.use = Optional().ask_use(constants['use'].format(self.__name))
        return self

    @property
    def vars(self):
        self._vars['dojot_cron_use'] = self.__use
        return self._vars