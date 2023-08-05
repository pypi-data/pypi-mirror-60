GREEN = "\033[92m"
ORANGE = "\033[93m"
RED = "\033[91m"
GRAY = "\033[90m"
BOLD = '\033[1m'
END = "\033[0m"


def _format(style, text):
    return f"{style}{text}{END}"


def green(text):
    return _format(GREEN, text)


def orange(text):
    return _format(ORANGE, text)


def red(text):
    return _format(RED, text)


def gray(text):
    return _format(GRAY, text)


def bold(text):
    return _format(BOLD, text)
