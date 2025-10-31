import asyncio
from dataclasses import dataclass

from gpio import PwmPin

FREQUENCY: int = 416


class Shoulder:
    def __init__(self, open_pin: int, close_pin: int):
        self.__open_pwm = PwmPin(open_pin, FREQUENCY)
        self.__close_pwm = PwmPin(close_pin, FREQUENCY)

    async def open(self):
        self.__open_pwm.set_dc(50)
        try:
            await asyncio.sleep((1 / FREQUENCY) * 400)
        finally:
            self.__open_pwm.set_dc(0)

    async def close(self):
        self.__close_pwm.set_dc(50)
        try:
            await asyncio.sleep((1 / FREQUENCY) * 400)
        finally:
            self.__close_pwm.set_dc(0)


class Hand:
    __pwm: PwmPin
    __release_angle: float
    __grip_angle: float

    def __init__(
        self, pin_num: int, release_angle: float, grip_angle: float
    ) -> None:
        self.__pwm = PwmPin(pin_num, frequency=50)
        self.__release_angle = release_angle
        self.__grip_angle = grip_angle
        asyncio.run(self.__set_angle(release_angle))

    async def __set_angle(self, angle: float):
        self.__pwm.set_dc(2 + (angle / 18))
        try:
            await asyncio.sleep(0.5)
        finally:
            self.__pwm.set_dc(0)

    async def release(self):
        await self.__set_angle(self.__release_angle)

    async def grip(self):
        await self.__set_angle(self.__grip_angle)


@dataclass
class Arm:
    r_shoulder: Shoulder
    l_shoulder: Shoulder
    r_hand: Hand
    l_hand: Hand

    async def open_shoulders(self):
        await asyncio.gather(self.r_shoulder.open(), self.l_shoulder.open())

    async def close_shoulders(self):
        await asyncio.gather(self.r_shoulder.close(), self.l_shoulder.close())

    async def release_hands(self):
        await asyncio.gather(self.r_hand.release(), self.l_hand.release())

    async def grip_hands(self):
        await asyncio.gather(self.r_hand.grip(), self.l_hand.grip())
