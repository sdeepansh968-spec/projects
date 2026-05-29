"""
Logger utility for WebSentinel
"""


class Logger:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def info(self, msg):
        print(msg)

    def success(self, msg):
        print(f"\033[92m{msg}\033[0m")

    def error(self, msg):
        print(f"\033[91m{msg}\033[0m")

    def debug(self, msg):
        if self.verbose:
            print(f"\033[90m[DEBUG] {msg}\033[0m")
