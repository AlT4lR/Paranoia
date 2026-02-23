import datetime

class SoulLogger:
    # ANSI Color Codes for terminal
    HEADER = '\033[95m'
    BRAIN = '\033[94m'   # Blue
    SOUL = '\033[92m'    # Green
    SYSTEM = '\033[93m'  # Yellow
    ERROR = '\033[91m'   # Red
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