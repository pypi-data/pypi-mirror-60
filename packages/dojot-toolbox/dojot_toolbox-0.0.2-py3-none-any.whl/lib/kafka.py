from .component import Component
from .optional import Optional
from .constants import kafka as constants
from .quantifiable import Quantifiable


class Kafka(Component):

    def __init__(self):
        super().__init__()
        self._visible_name = constants['name']
        self.__persistence_time = 0
        self.__use_persistent_volume = False
        self.__volume_size = 10
        self.__optional = Optional()
        self.__quantifiable = Quantifiable()


    def ask_persistence_time(self):
        question = constants['persistence_time'].format(
            self.__persistence_time)
        self.__persistence_time = self.__quantifiable.ask_quantity(
            question, default=self.__persistence_time)
        return self

    #TODO: verificar se tem volume para persistir
    def and_if_use_persistent_volume(self):
        self.__use_persistent_volume = self.__optional.ask_use(
            constants['use_persistent_volume'])
        return self

    def and_volume_size(self):
        if self.__use_persistent_volume:
            question = constants['volume_size'].format(self.__volume_size)
            self.__volume_size = self.__quantifiable.ask_quantity(question)
        return self

    @property
    def vars(self):
        self._vars['dojot_kafka_persistence_time'] = self.__persistence_time
        self._vars['dojot_kafka_persistent_volumes'] = self.__use_persistent_volume
        self._vars['dojot_kafka_volume_size'] = self.__volume_size
        return self._vars
