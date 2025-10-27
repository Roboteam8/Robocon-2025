import sys
from collections.abc import Callable
from typing import Final, Literal, TypedDict

from typing_extensions import TypeAlias

VERBOSE = True


class _RPi_Info(TypedDict):
    P1_REVISION: int
    REVISION: str
    TYPE: str
    MANUFACTURER: str
    PROCESSOR: str
    RAM: str


VERSION: str = ""
RPI_INFO: _RPi_Info = {
    "P1_REVISION": 0,
    "REVISION": "",
    "TYPE": "",
    "MANUFACTURER": "",
    "PROCESSOR": "",
    "RAM": "",
}
RPI_REVISION: int = 0

HIGH: Literal[1] = 1
LOW: Literal[0] = 0

OUT: Final = 0
IN: Final = 1
HARD_PWM: Final = 43
SERIAL: Final = 40
I2C: Final = 42
SPI: Final = 41
UNKNOWN: Final = -1

BOARD: Final = 10
BCM: Final = 11

PUD_OFF: Final = 20
PUD_UP: Final = 22
PUD_DOWN: Final = 21

RISING: Final = 31
FALLING: Final = 32
BOTH: Final = 33

_EventCallback: TypeAlias = Callable[[int], object]


def _debug(*values: object):
    if VERBOSE:
        print("mock.RPi.GPIO:", *values)


def setup(
    channel: int | list[int] | tuple[int, ...],
    direction: Literal[0, 1],
    pull_up_down: int = 20,
    initial: int = -1,
) -> None:
    _debug(
        f"GPIO.setup called with channels: {channel}, direction: {direction}, pull_up_down: {pull_up_down}, initial: {initial}"
    )


def cleanup(channel: int | list[int] | tuple[int, ...] = -666) -> None:
    _debug(f"GPIO.cleanup called with channel: {channel}")


def output(
    channel: int | list[int] | tuple[int, ...],
    value: Literal[0, 1]
    | bool
    | list[Literal[0, 1] | bool]
    | tuple[Literal[0, 1] | bool, ...],
    /,
) -> None:
    _debug(f"GPIO.output called with channel: {channel}, value: {value}")


def input(channel: int, /) -> bool:
    _debug(f"GPIO.input called with channel: {channel}")
    return False


self = sys.modules[__name__]

_mode: Literal[10, 11] | None


def setmode(mode: Literal[10, 11], /) -> None:
    _debug(f"GPIO.setmode called with mode: {mode}")
    _mode = mode


def getmode() -> Literal[10, 11] | None:
    _debug("GPIO.getmode called")
    return self._mode


def add_event_detect(
    channel: int,
    edge: int,
    callback: _EventCallback | None = None,
    bouncetime: int = -666,
) -> None: ...
def remove_event_detect(channel: int, /) -> None: ...
def event_detected(channel: int, /) -> bool: ...
def add_event_callback(channel: int, callback: _EventCallback) -> None: ...
def wait_for_edge(
    channel: int, edge: int, bouncetime: int = -666, timeout: int = -1
) -> int | None: ...
def gpio_function(channel: int, /) -> int: ...
def setwarnings(gpio_warnings: bool, /) -> None: ...


class PWM:
    def __init__(self, channel: int, frequency: float, /) -> None: ...
    def start(self, dutycycle: float, /) -> None: ...
    def ChangeDutyCycle(self, dutycycle: float, /) -> None: ...
    def ChangeFrequency(self, frequency: float, /) -> None: ...
    def stop(self) -> None: ...
