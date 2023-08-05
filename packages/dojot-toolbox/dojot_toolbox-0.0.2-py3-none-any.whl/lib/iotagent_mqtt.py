from .component import Component
from .optional import Optional
from .persistent import Persistent
from .optional import Optional
from .quantifiable import Quantifiable
from .authenticable import Authenticable
from .constants import iotagent_mqtt as constants


class IoTAgentMQTT(Component):

    def __init__(self):
        super().__init__()
        self._visible_name = constants['name']
        self.__use = True
        self.__use_insecure_mqtt = False
        self.__replicas = 1
        self.__optional = Optional()
        self.__quantifiable = Quantifiable()

    def ask_use(self):
        self.__use = self.__optional.ask_use(
            constants['use'], default=True)
        return self

    #TODO: verificar se serviço é escalável
    def and_replicas(self):
        if self.__use:
            question = constants['replicas'].format(self.__replicas)
            self.__replicas = self.__quantifiable.ask_quantity(
                question, self.__replicas)
        return self

    def and_use_insecure_mqtt(self):
        if self.__use:
            self.__use_insecure_mqtt = self.__optional.ask_use(
                constants['use_insecure_mqtt'], default=self.__use_insecure_mqtt)
        return self

    @property
    def vars(self):
        self._vars['dojot_iotagent_mosca_use'] = self.__use
        self._vars['dojot_iotagent_mosca_replicas'] = self.__replicas
        self._vars['dojot_insecure_mqtt'] = str(self.__use_insecure_mqtt).lower()
        return self._vars
