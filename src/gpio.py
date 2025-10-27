import importlib.util

try:
    importlib.util.find_spec("RPi.GPIO")
    from RPi import GPIO  # pyright: ignore[reportMissingModuleSource]  # noqa: F401
    from RPi.GPIO import PWM  # pyright: ignore[reportMissingModuleSource]  # noqa: F401
except ImportError:
    from FakeRPi import GPIO  # pyright: ignore[reportMissingModuleSource]  # noqa: F401
    from FakeRPi.PWM import (
        PWM,  # pyright: ignore[reportMissingModuleSource]  # noqa: F401
    )

GPIO.setmode(GPIO.BCM)  # pyright: ignore[reportArgumentType]
