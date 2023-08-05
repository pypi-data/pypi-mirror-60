import getpass

class Authenticable:
    
    def ask_username(self, phrase, default):
        username = input(phrase)
        return username if username else default

    def ask_password(self, phrase, default):
        password = getpass.getpass(prompt=phrase, stream=None)
        return password if password else default