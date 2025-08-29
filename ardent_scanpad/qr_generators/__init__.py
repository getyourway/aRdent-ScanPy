"""
QR Generators - Hybrid API Architecture

Level 1: Traditional API (preserved in controllers/qr_generator.py)
Level 2: JSON + Traditional API (new generators with both approaches)

Usage:
    # Traditional API
    from ardent_scanpad import ScanPad
    qr = scanpad.qr
    led_qr = qr.create_led_on_command(1)
    
    # Hybrid API  
    from ardent_scanpad.qr_generators import KeyboardConfigGenerator
    gen = KeyboardConfigGenerator()
    
    # JSON approach
    qr_codes = gen.from_json_file("config.json")
    
    # Traditional approach in same generator
    qr_codes = gen.create_numpad_config()
"""

from .keyboard_config import KeyboardConfigGenerator
from .device_commands import DeviceCommandGenerator

__all__ = ['KeyboardConfigGenerator', 'DeviceCommandGenerator']