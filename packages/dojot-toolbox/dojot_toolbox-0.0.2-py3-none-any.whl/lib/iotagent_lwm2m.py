from .component import Component
from .optional import Optional
from .optional import Optional
from .constants import iotagent_lwm2m as constants


class IoTAgentLWM2M(Component):

    def __init__(self):
        super().__init__()
        self._visible_name = constants['name']
        self.__use = True
        self.__use_insecure_mqtt = False
        self.__replicas = 1
        self.__optional = Optional()

    def ask_use(self):
        self.__use = self.__optional.ask_use(
            constants['use'], default=True)
        return self


    @property
    def vars(self):
        self._vars['dojot_iotagent_lwm2m_use'] = self.__use
        return self._vars
