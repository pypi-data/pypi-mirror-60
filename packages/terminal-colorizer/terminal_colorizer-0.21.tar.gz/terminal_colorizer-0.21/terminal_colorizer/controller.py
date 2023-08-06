from . import settings


def turn_off():
    settings._turned_off = True
    return True


def turn_on():
    settings._turned_off = False
    return True
