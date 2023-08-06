def __run(*args, color: str, sep: str):
    from . import settings
    context = __string_formatter(*args, sep=sep)
    if settings._turned_off:
        return context
    prefix = settings.palette[f'{color}']
    postfix = settings.palette['RESET']
    return prefix + context + postfix


def __string_formatter(*args, sep: str):
    context = ''
    for arg in args:
        context += arg.__str__() + sep
    return context[:-len(sep)]


def carrot(*args, sep: str = ' '):
    return __run(*args, color='carrot', sep=sep)


def mint(*args, sep: str = ' '):
    return __run(*args, color='mint', sep=sep)


def brown(*args, sep: str = ' '):
    return __run(*args, color='brown', sep=sep)


def grey(*args, sep: str = ' '):
    return __run(*args, color='grey', sep=sep)


def purple(*args, sep: str = ' '):
    return __run(*args, color='purple', sep=sep)


def white(*args, sep: str = ' '):
    return __run(*args, color='white', sep=sep)


def black(*args, sep: str = ' '):
    return __run(*args, color='black', sep=sep)


def yellow(*args, sep: str = ' '):
    return __run(*args, color='yellow', sep=sep)


def cyan(*args, sep: str = ' '):
    return __run(*args, color='cyan', sep=sep)


def green(*args, sep: str = ' '):
    return __run(*args, color='green', sep=sep)


def pink(*args, sep: str = ' '):
    return __run(*args, color='pink', sep=sep)


def blue(*args, sep: str = ' '):
    return __run(*args, color='blue', sep=sep)


def red(*args, sep: str = ' '):
    return __run(*args, color='red', sep=sep)
