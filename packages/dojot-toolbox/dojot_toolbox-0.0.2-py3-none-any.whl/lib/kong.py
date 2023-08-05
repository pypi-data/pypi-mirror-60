from .component import Component
from .optional import Optional
from .scalable import Scalable
from .persistent import Persistent
from .authenticable import Authenticable
from .quantifiable import Quantifiable
from .constants import kong as constants

import getpass


class Kong(Component):

    def __init__(self):
        super().__init__()
        self.__req_per_minute = 5
        self.__req_per_hour = 40
        self.__pg_username = "kong"
        self.__pg_password = "kong"
        self.__name = constants['name']
        self._visible_name = constants['name']
        self.__authenticable = Authenticable()
        self.__quantifiable = Quantifiable()

    def ask_req_per_minute(self):
        self.__req_per_minute = self.__quantifiable.ask_quantity(
            constants['req_per_minute'].format(self.__req_per_minute), self.__req_per_minute)
        return self

    def ask_req_per_hour(self):
        self.__req_per_hour = self.__quantifiable.ask_quantity(
            constants['req_per_hour'].format(self.__req_per_hour), self.__req_per_hour)
        return self

    def ask_pg_username(self):
        self.__pg_username = self.__authenticable.ask_username(
            constants['pg_user'].format(self.__name, self.__pg_username), self.__pg_username)
        return self

    def ask_pg_password(self):
        self.__pg_password = self.__authenticable.ask_password(
            constants['pg_password'].format(self.__name, self.__pg_password), self.__pg_password)
        return self

    @property
    def vars(self):
        self._vars['dojot_kong_req_per_minute'] = self.__req_per_minute
        self._vars['dojot_kong_req_per_hour'] = self.__req_per_hour
        self._vars['dojot_psql_kong_user'] = self.__pg_username
        self._vars['dojot_psql_kong_passwd'] = self.__pg_password
        return self._vars
