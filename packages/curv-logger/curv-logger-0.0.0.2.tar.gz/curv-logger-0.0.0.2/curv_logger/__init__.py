__version__ = "0.0.0.2"
import logging
from dataclasses import dataclass
from enum import Enum
from functools import partial
from time import time
from typing import Dict, List, Callable, Union, Any

from dataclasses_json import DataClassJsonMixin


class LoggerState(str, Enum):
    enter = "enter"
    exit = "exit"


@dataclass
class LoggerInfo(DataClassJsonMixin):
    depth: int
    name: str
    state: Union[LoggerState, str]


@dataclass
class LoggerInfoTimed(LoggerInfo):
    seconds: float


class LoggerLevel(int, Enum):
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARN = logging.WARNING
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


class Logger(logging.LoggerAdapter):
    _start_times = Dict[str, float]
    _names: List[str]
    level = LoggerLevel

    def __init__(
        self, name: str = __name__, level: Union[int, str, LoggerLevel] = logging.INFO
    ):
        _level = logging._nameToLevel[level] if isinstance(level, str) else level
        logging.basicConfig()
        logger = logging.getLogger(name)
        logger.setLevel(_level)
        super().__init__(logger, extra={})
        self._level = _level
        self._start_times = {}
        self._names = []

    def enter(self, value: Any, depth: int = 0) -> Callable[[], Any]:
        name = self._parse_name(value)
        self.log(
            self._level,
            LoggerInfo(name=name, state=LoggerState.enter, depth=depth).to_json(),
        )
        ret = partial(self.exit, name, depth)
        self._start_times[name] = time()
        return ret

    def exit(self, value: Any, depth: int = 0):
        end_time = time()
        name = self._parse_name(value)
        seconds = round((end_time - self._start_times[name]), 2)
        self.log(
            self._level,
            LoggerInfoTimed(
                name=name,
                state=LoggerState.exit,
                seconds=seconds,
                depth=depth,
            ).to_json(),
        )

    @staticmethod
    def _parse_name(value: Any) -> str:
        if isinstance(value, (str, int, float)):
            name = str(value)
        elif hasattr(value, "__name__"):
            name = value.__name__
        elif hasattr(value, "__class__"):
            if hasattr(value.__class__, "__name__"):
                name = value.__class__.__name__
            else:
                name = str(repr(value))
        else:
            name = str(repr(value))
        return name

    def __call__(self, value: Any):
        name = self._parse_name(value)
        self._names.append(name)
        return self

    def __enter__(self):
        if not self._names:
            raise Exception(
                "Must add a name first via the  builtin '__call__'. For example:\n"
                "with logger('my_name'):\n"
                "    print('hello')\n"
            )
        name = self._names[-1]
        depth = len(self._names)
        self.enter(name, depth)

    def __exit__(self, exception_type, exception_value, traceback):
        depth = len(self._names)
        name = self._names.pop()
        self.exit(name, depth)


if __name__ == "__main__":
    from time import sleep

    def _test():
        logger = Logger()
        # logger = Logger(name="my-logger", level=Logger.level.WARNING)
        with logger(sleep):
            sleep(0.01)
        with logger("sleep for 0.1s"):
            sleep(0.1)
        with logger("sleep for 1s"):
            sleep(1)
    _test()
