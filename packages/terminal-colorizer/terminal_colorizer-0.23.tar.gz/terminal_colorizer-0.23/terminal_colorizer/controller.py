def turn_off():
    from terminal_colorizer import settings
    settings._turned_off = True
    return True


def turn_on():
    from terminal_colorizer import settings
    settings._turned_off = False
    return True
