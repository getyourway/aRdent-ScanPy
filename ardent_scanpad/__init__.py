"""
aRdent ScanPad Python Library

A professional Python library for controlling aRdent ScanPad BLE HID devices.
Provides high-level async API for key configuration, LED control, device settings, and OTA updates.

Example:
    ```python
    from ardent_scanpad import ScanPad
    
    async with ScanPad() as device:
        # Configure a key to type "Hello"
        await device.keys.set_key_sequence("Hello", key_id=0)
        
        # Blink LED in red
        await device.leds.blink(led_id=1, color="red", duration=2.0)
        
        # Set French keyboard layout
        await device.device.set_language("french")
    ```

Version: 1.0.0
Author: aRdent Solutions
License: MIT
"""

from .scanpad import ScanPad
from .core.exceptions import (
    ScanPadError,
    ConnectionError,
    ConfigurationError,
    TimeoutError,
    DeviceNotFoundError,
    InvalidParameterError
)
from .utils.constants import (
    KeyIDs, KeyTypes, HIDKeyCodes, HIDModifiers, ConsumerCodes,
    BuzzerMelodies, KeyboardLayouts, DeviceOrientations, LEDs
)

__version__ = "1.0.0"
__author__ = "aRdent Solutions"
__license__ = "MIT"

# Public API
__all__ = [
    # Main class
    "ScanPad",
    
    # Exceptions
    "ScanPadError",
    "ConnectionError", 
    "ConfigurationError",
    "TimeoutError",
    "DeviceNotFoundError",
    "InvalidParameterError",
    
    # Constants
    "KeyIDs",
    "KeyTypes", 
    "HIDKeyCodes",
    "HIDModifiers",
    "ConsumerCodes",
    "BuzzerMelodies",
    "KeyboardLayouts", 
    "DeviceOrientations",
    "LEDs"
]