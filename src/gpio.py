import atexit
import importlib.util
from dataclasses import dataclass, field
from typing import Literal

try:
    importlib.util.find_spec("RPi.GPIO")
    from RPi import GPIO  # pyright: ignore[reportMissingModuleSource]  # noqa: F401
    from RPi.GPIO import PWM  # pyright: ignore[reportMissingModuleSource]  # noqa: F401
except ImportError:
    from mock.RPi import GPIO  # noqa: F401
    from mock.RPi.GPIO import PWM  # noqa: F401

GPIO.setmode(GPIO.BCM)

@dataclass
class DigitalPin:
    pin_num: int
    pin_mode: Literal[0, 1]

    def __post_init__(self):
        GPIO.setup(self.pin_num, self.pin_mode)

    def on(self):
        GPIO.output(self.pin_num, GPIO.HIGH)

    def off(self):
        GPIO.output(self.pin_num, GPIO.LOW)

    def set_state(self, state: Literal[0, 1]):
        GPIO.output(self.pin_num, state)

@dataclass
class PwmPin:
    pin_num: int
    freqency: int = 1000
    initial_dc: float = 0

    __pwm: PWM = field(init=False)

    def __post_init__(self):
        GPIO.setup(self.pin_num, GPIO.OUT)
        self.__pwm = GPIO.PWM(self.pin_num, self.freqency)
        self.__pwm.start(self.initial_dc)

    def __del__(self):
        self.__pwm.stop()

    def set_dc(self, dc: float):
        if dc < 0 or 100 < dc:
            raise ValueError("Duty cycle must be between 0 and 100")
        self.__pwm.ChangeDutyCycle(dc)


atexit.register(lambda: GPIO.cleanup())
