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


_mode: Literal[10, 11] | None


def setmode(mode: Literal[10, 11], /) -> None:
    _debug(f"GPIO.setmode called with mode: {mode}")
    _mode = mode


def getmode() -> Literal[10, 11] | None:
    _debug("GPIO.getmode called")
    return _mode  # noqa: F821


def add_event_detect(
    channel: int,
    edge: int,
    callback: _EventCallback | None = None,
    bouncetime: int = -666,
) -> None:
    _debug(
        f"GPIO.add_event_detect called with channel: {channel}, edge: {edge}, callback: {callback}, bouncetime: {bouncetime}"
    )


def remove_event_detect(channel: int, /) -> None:
    _debug(f"GPIO.remove_event_detect called with channel: {channel}")


def event_detected(channel: int, /) -> bool:
    _debug(f"GPIO.event_detected called with channel: {channel}")
    return False


def add_event_callback(channel: int, callback: _EventCallback) -> None:
    _debug(
        f"GPIO.add_event_callback called with channel: {channel}, callback: {callback}"
    )


def wait_for_edge(
    channel: int, edge: int, bouncetime: int = -666, timeout: int = -1
) -> int | None:
    _debug(
        f"GPIO.wait_for_edge called with channel: {channel}, edge: {edge}, bouncetime: {bouncetime}, timeout: {timeout}"
    )
    return None


def gpio_function(channel: int, /) -> int:
    _debug(f"GPIO.gpio_function called with channel: {channel}")
    return UNKNOWN


def setwarnings(gpio_warnings: bool, /) -> None:
    _debug(f"GPIO.setwarnings called with gpio_warnings: {gpio_warnings}")


class PWM:
    def __init__(self, channel: int, frequency: float, /) -> None:
        self.channel = channel
        self.freqency = frequency

    def start(self, dutycycle: float, /) -> None:
        self.dutycycle = dutycycle
        _debug(
            f"GPIO.PWM.start called on channel: {self.channel} with dutycycle: {dutycycle}"
        )

    def ChangeDutyCycle(self, dutycycle: float, /) -> None:
        self.dutycycle = dutycycle
        _debug(
            f"GPIO.PWM.ChangeDutyCycle called on channel: {self.channel} with dutycycle: {dutycycle}"
        )

    def ChangeFrequency(self, frequency: float, /) -> None:
        self.frequency = frequency
        _debug(
            f"GPIO.PWM.ChangeFrequency called on channel: {self.channel} with frequency: {frequency}"
        )

    def stop(self) -> None:
        _debug(f"GPIO.PWM.stop called on channel: {self.channel}")
