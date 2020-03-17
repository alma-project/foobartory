from foobartory import Foobartory


if __name__ == "__main__":
    foobartory = Foobartory(cash_start=0, nbrobots_start=2)
    foobartory.start(nbrobots_max=30)
    print()
