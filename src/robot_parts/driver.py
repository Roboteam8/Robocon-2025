import asyncio
from dataclasses import dataclass

import numpy as np

from gpio import GPIO, DigitalPin, PwmPin

DC: float = 50
MM_PER_SEC: float = (170 / 3) * 10
RAD_PER_SEC: float = 23/30 * np.pi


class Wheel:
    __start_stop: DigitalPin
    __run_break: DigitalPin
    __direction: DigitalPin
    __pwm: PwmPin

    def __init__(
        self, start_stop_pin: int, run_break_pin: int, direction_pin: int, pwm_pin: int
    ):
        self.__start_stop = DigitalPin(start_stop_pin, GPIO.OUT)
        self.__run_break = DigitalPin(run_break_pin, GPIO.OUT)
        self.__direction = DigitalPin(direction_pin, GPIO.OUT)
        self.__start_stop.set_state(GPIO.HIGH)
        self.__run_break.set_state(GPIO.HIGH)

        self.__pwm = PwmPin(pwm_pin, initial_dc=DC)
        self.__run_break.set_state(GPIO.LOW)

    async def run(self, direction: bool, duration: float):
        self.__direction.set_state(GPIO.HIGH if direction else GPIO.LOW)
        self.__start_stop.set_state(GPIO.LOW)
        try:
            await asyncio.sleep(duration)
        finally:
            self.__start_stop.set_state(GPIO.HIGH)


@dataclass
class Driver:
    r_wheel: Wheel
    l_wheel: Wheel

    async def straight(self, distance: float):
        duration = abs(distance) / MM_PER_SEC
        is_back = distance < 0
        await asyncio.gather(
            self.r_wheel.run(not is_back, duration),
            self.l_wheel.run(is_back, duration),
        )

    async def trun(self, angle: float):
        duration = abs(angle) / RAD_PER_SEC
        is_right = angle < 0
        await asyncio.gather(
            self.r_wheel.run(is_right, duration),
            self.l_wheel.run(is_right, duration),
        )
