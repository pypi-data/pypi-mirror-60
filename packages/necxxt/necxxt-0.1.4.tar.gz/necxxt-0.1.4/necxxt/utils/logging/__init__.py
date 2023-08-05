import sys


class colors:
    END = "\033[0m"
    ERROR = "\033[1;31m"
    INFO = "\033[1;32m"
    WARNING = "\033[1;33m"
    DEBUG = "\033[1;34m"


def error(msg):
    sys.stderr.write(colors.ERROR + msg + colors.END + "\n")


def info(msg):
    print(colors.INFO + msg + colors.END)


def warn(msg):
    print(colors.WARNING + msg + colors.END)


def debug(msg):
    print(colors.DEBUG + msg + colors.END)
