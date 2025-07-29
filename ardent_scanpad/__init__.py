"""
aRdent ScanPad Python Library

A professional Python library for controlling aRdent ScanPad BLE HID devices.
Provides high-level async API for key configuration, LED control, device settings, and OTA updates.

Example:
    ```python
    from ardent_scanpad import ScanPad, HIDKeyCodes, HIDModifiers
    
    async with ScanPad() as device:
        # Configure a key to type "Hello"
        text_action = device.keys.create_text_action("Hello")
        await device.keys.set_key_config(0, [text_action])
        
        # Blink LED
        await device.device.led.blink(1, frequency=2.0)
        
        # Set French keyboard layout
        await device.device.set_language(0x040C)  # FR_AZERTY
    ```

Version: 1.0.0
Author: aRdent Solutions
License: MIT
"""

from .scanpad import ScanPad, DeviceInfo
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
    "DeviceInfo",
    
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