class Optional:

    def ask_use(self, phrase, default=False):
        res = input(phrase)
        if (not res) or (res != "y" and res != "n"):
            return default
        return True if res == "y" else False