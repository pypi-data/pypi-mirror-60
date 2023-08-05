from .component import Component
from .persistent import Persistent
from .authenticable import Authenticable
from .quantifiable import Quantifiable
from .optional import Optional
from .constants import auth as constants

import getpass


class Auth(Component):

    def __init__(self):
        super().__init__()
        self._visible_name = constants['name']
        self.__pg_username = "auth"
        self.__pg_password = "auth"
        self.__send_email = True
        self.__smtp_host = ""
        self.__smtp_username = ""
        self.__smtp_password = ""
        self.__password_reset_link = ""
        self.__authenticable = Authenticable()
        self.__quantifiable = Quantifiable()
        self.__optional = Optional()

    def and_pg_username(self):
        question = constants['pg_user'].format(self.__pg_username)
        self.__pg_username = self.__authenticable.ask_username(
            question, self.__pg_username)
        return self

    def and_pg_password(self):
        question = constants['pg_password'].format(self.__pg_password)
        self.__pg_password = self.__authenticable.ask_password(
            question, self.__pg_password)
        return self

    def ask_if_should_send_mail(self):
        self.__send_email = self.__optional.ask_use(
            constants['send_mail'], default=self.__send_email)
        return self

    def and_smtp_host(self):
        if self.__send_email:
            host = input(constants['smtp_host'])
            if host:
                self.__smtp_host = host
        return self

    def and_smtp_username(self):
        if self.__send_email:
            self.__smtp_username = self.__authenticable.ask_username(
                constants['smtp_user'], self.__pg_username)
        return self

    def and_smtp_password(self):
        if self.__send_email:
            self.__smtp_password = self.__authenticable.ask_password(
                constants['smtp_password'], self.__pg_password)
        return self

    #TODO: montar o link automaticamente
    def and_password_reset_link(self):
        if self.__send_email:
            link = input(constants['password_reset_link'])
            if link:
                self.__password_reset_link = link
        return self

    @property
    def vars(self):
        self._vars['dojot_psql_auth_user'] = self.__pg_username
        self._vars['dojot_psql_auth_passwd'] = self.__pg_password
        self._vars['dojot_auth_email_enabled'] = self.__send_email
        self._vars['dojot_auth_email_host'] = self.__smtp_host
        self._vars['dojot_auth_email_user'] = self.__smtp_username
        self._vars['dojot_auth_email_passwd'] = self.__smtp_password
        self._vars['dojot_auth_smtp_reset_link'] = self.__password_reset_link
        return self._vars
