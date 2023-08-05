class Quantifiable:

    def ask_quantity(self, phrase, default=0):
        try:
            quantity = int(input(phrase))
            return quantity
        except ValueError:
            return default