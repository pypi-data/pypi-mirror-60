from termcolor import colored

class Component:
    def __init__(self):
        self._vars = {}
        self._visible_name = ""

    def show_name(self):
        print(colored("\n\n{}".format(self._visible_name), 'white', attrs=['bold']))
        return self
