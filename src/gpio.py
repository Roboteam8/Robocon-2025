import importlib.util

try:
    importlib.util.find_spec("RPi.GPIO")
    from RPi import GPIO  # pyright: ignore[reportMissingModuleSource]
    from RPi.GPIO import PWM  # pyright: ignore[reportMissingModuleSource]
except ImportError:
    from FakeRPi import GPIO  # pyright: ignore[reportMissingModuleSource]  # noqa: F401
    from FakeRPi.PWM import (
        PWM,  # pyright: ignore[reportMissingModuleSource]  # noqa: F401
    )
