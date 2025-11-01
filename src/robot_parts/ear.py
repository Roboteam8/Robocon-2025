import asyncio
import time

from gpio import GPIO, DigitalPin

TRIG = 6
ECHO = 12

trigger_pin = DigitalPin(TRIG, GPIO.OUT)
echo_pin = DigitalPin(ECHO, GPIO.OUT)


async def hear_ultrasonic(timeout=float("NaN")):
    trigger_pin.set_state(GPIO.LOW)
    await asyncio.sleep(0.1)

    echo_pin.set_state(GPIO.HIGH)
    await asyncio.sleep(1e-5)
    echo_pin.set_state(GPIO.LOW)

    pulse_start = None
    pulse_end = None

    start = time.time()
    while GPIO.input(ECHO) == GPIO.LOW:
        pulse_start = time.time()
        if time.time() - start > timeout:
            return float("NaN")

    start = time.time()
    while GPIO.input(ECHO) == GPIO.HIGH:
        pulse_end = time.time()
        if time.time() - start > timeout:
            return float("NaN")

    if pulse_start is None or pulse_end is None:
        return float("NaN")

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 343000 / 2
    return round(distance, 2)
