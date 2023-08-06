def turn_off():
    from . import settings
    settings._turned_off = True
    return True


def turn_on():
    from . import settings
    settings._turned_off = False
    return True
