import atexit
import importlib.util

try:
    importlib.util.find_spec("RPi.GPIO")
    from RPi import GPIO  # pyright: ignore[reportMissingModuleSource]  # noqa: F401
    from RPi.GPIO import PWM  # pyright: ignore[reportMissingModuleSource]  # noqa: F401
except ImportError:
    from mock.RPi import (
        GPIO,  # noqa: F401
    )
    from mock.RPi.GPIO import (
        PWM,  # noqa: F401
    )

GPIO.setmode(GPIO.BCM)

atexit.register(lambda: GPIO.cleanup())
