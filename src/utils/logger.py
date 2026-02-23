import datetime
import traceback
import sys

class SoulLogger:
    BRAIN = '\033[94m'
    SOUL = '\033[92m'
    SYSTEM = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def _get_time():
        return datetime.datetime.now().strftime("%H:%M:%S")

    @classmethod
    def brain(cls, message):
        print(f"[{cls._get_time()}] {cls.BRAIN}[BRAIN]{cls.ENDC} {message}")

    @classmethod
    def soul(cls, message):
        print(f"[{cls._get_time()}] {cls.SOUL}[SOUL]{cls.ENDC} {message}")

    @classmethod
    def sys(cls, message):
        print(f"[{cls._get_time()}] {cls.SYSTEM}[SYS]{cls.ENDC} {message}")

    @classmethod
    def err(cls, message):
        print(f"[{cls._get_time()}] {cls.ERROR}[!! ERROR !!]{cls.ENDC} {cls.BOLD}{message}{cls.ENDC}")
        traceback.print_exc(file=sys.stdout)