import time
from progress.spinner import Spinner
from threading import Thread

class SpinnerProgress(Thread):

    def __init__(self, phrase):
        self.__running = True
        Thread.__init__(self)
        self.__spinner = Spinner(phrase)

    def run(self):
        while self.__running:
            time.sleep(.300)
            self.__spinner.next()

    def finish(self):
        self.__running = False
        self.join()     
