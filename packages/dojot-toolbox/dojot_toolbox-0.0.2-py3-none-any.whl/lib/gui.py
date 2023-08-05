from .component import Component
from .optional import Optional
from .constants import gui as constants

class Gui(Component):

    def __init__(self):
        super().__init__()
        self.__use = True
        self.__name = constants['name']
        self._visible_name = constants['name']

    def ask_use(self):
        self.__use = Optional().ask_use(constants['use'].format(self.__name))
        return self

    @property
    def vars(self):
        self._vars['dojot_gui_use'] = self.__use
        return self._vars