"""
QR Code Generator Controller for aRdent ScanPad

UPDATED: Now uses modular QR system while preserving existing API
Provides QR code generation for device commands, enabling GUI applications 
to create scannable codes for device configuration without BLE connection.

Architecture:
- Follows same controller pattern as device.py and keys.py
- Reuses all existing constants (LEDs, BuzzerMelodies, HIDKeyCodes, etc.)
- Generates scanner-compatible format ($CMD:DEV: / $CMD:KEY:)
- Creates PNG images with embedded QR codes
- INTERNAL: Delegates to new modular qr/ system
"""

import logging
from typing import Optional, Dict, Any, Union, List
from pathlib import Path

# Import from new modular system
from .qr.commands import (
    LEDCommandBuilder, BuzzerCommandBuilder, DeviceCommandBuilder,
    KeyConfigCommandBuilder, FullConfigCommandBuilder, LuaCommandBuilder
)
from .qr.formats import QRFormatter
from .qr.images import QRImageSaver

# Keep constants import for compatibility
from ..utils.constants import (
    KeyTypes, KeyIDs, HIDKeyCodes, ConsumerCodes, 
    LEDs, BuzzerMelodies, DeviceOrientations, KeyboardLayouts
)

# For external PIL availability check
try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

logger = logging.getLogger(__name__)


class QRCommand:
    """
    QR Command wrapper - PRESERVED API
    
    Maintains exact same interface as before but uses modular backend
    """
    
    def __init__(self, command_data: str, command_type: str, description: str, metadata: Dict[str, Any] = None):
        """
        Args:
            command_data: Raw command string (e.g., "$CMD:DEV:100201CMD$") 
            command_type: Type description (e.g., "LED Control", "Key Configuration")
            description: Human-readable description (e.g., "Turn LED 2 ON")
            metadata: Additional command information
        """
        self.command_data = command_data
        self.command_type = command_type
        self.description = description
        self.metadata = metadata or {}
        self._qr_image = None
        
        # Create image saver for compatibility methods
        self._image_saver = QRImageSaver()
        
    def generate_qr_image(self, 
                         size: int = 300,
                         border: int = 4,
                         error_correction=None) -> Optional['Image.Image']:
        """
        Generate QR code image for this command - PRESERVED API
        """
        if not QR_AVAILABLE:
            logger.warning("qrcode library not available. Install with: pip install qrcode[pil]")
            return None
            
        # Use modular image generator
        return self._image_saver._generator.generate_qr_image(
            qr_data=self.command_data,
            title=self.command_type,
            description=self.description,
            size=size,
            border=border,
            error_correction=error_correction,
            add_title=self.metadata.get('add_title', True)
        )
    
    def save(self, filename: Union[str, Path], **kwargs) -> bool:
        """
        Save QR code as PNG image - PRESERVED API
        """
        return self._image_saver.save_qr_image(
            qr_data=self.command_data,
            filename=filename,
            title=self.command_type,
            description=self.description,
            **kwargs
        )
    
    def __str__(self) -> str:
        return f"QRCommand({self.command_type}: {self.description})"


class QRGeneratorController:
    """
    QR Code Generator Controller - PRESERVED API
    
    This controller generates QR codes for device commands without requiring
    BLE connection. Reuses all existing constants and command structures.
    
    UPDATED: Now delegates to modular qr/ system internally
    """
    
    def __init__(self):
        """Initialize QR code generator controller"""
        self._logger = logging.getLogger(self.__class__.__name__)
        self._validate_dependencies()
        
        # Initialize modular components
        self._led_builder = LEDCommandBuilder()
        self._buzzer_builder = BuzzerCommandBuilder()
        self._device_builder = DeviceCommandBuilder()
        self._key_builder = KeyConfigCommandBuilder()
        self._full_builder = FullConfigCommandBuilder()
        self._lua_builder = LuaCommandBuilder()
        self._formatter = QRFormatter()
        self._image_saver = QRImageSaver()
        
    def _validate_dependencies(self):
        """Check if required libraries are available"""
        if not QR_AVAILABLE:
            self._logger.warning(
                "QR code generation requires additional dependencies. "
                "Install with: pip install qrcode[pil]"
            )
    
    def _create_qr_command(self, command_data, command_type: str, description: str, 
                          metadata: Dict[str, Any] = None) -> QRCommand:
        """Create QRCommand from modular CommandData"""
        formatted_data = self._formatter.format_command(command_data)
        
        full_metadata = {
            'domain': command_data.domain,
            'command_id': command_data.command_id,
            'payload_hex': command_data.payload.hex().upper(),
            **(metadata or {}),
            **command_data.metadata
        }
        
        return QRCommand(formatted_data, command_type, description, full_metadata)
    
    # ========================================
    # LED COMMANDS - PRESERVED API
    # ========================================
    
    def create_led_on_command(self, led_id: int) -> QRCommand:
        """Create LED ON command - PRESERVED API"""
        command_data = self._led_builder.create_led_on_command(led_id)
        return self._create_qr_command(command_data, command_data.command_type, command_data.description)
    
    def create_led_off_command(self, led_id: int) -> QRCommand:
        """Create LED OFF command - PRESERVED API"""
        command_data = self._led_builder.create_led_off_command(led_id)
        return self._create_qr_command(command_data, command_data.command_type, command_data.description)
    
    def create_all_leds_off_command(self) -> QRCommand:
        """Create command to turn all LEDs off - PRESERVED API"""
        command_data = self._led_builder.create_all_leds_off_command()
        return self._create_qr_command(command_data, command_data.command_type, command_data.description)
    
    # ========================================  
    # BUZZER COMMANDS - PRESERVED API
    # ========================================
    
    def create_buzzer_melody_command(self, melody_name: str) -> QRCommand:
        """Create buzzer melody command - PRESERVED API"""
        command_data = self._buzzer_builder.create_buzzer_melody_command(melody_name)
        return self._create_qr_command(command_data, command_data.command_type, command_data.description)
    
    # ========================================
    # DEVICE SETTINGS COMMANDS - PRESERVED API
    # ========================================
    
    def create_orientation_command(self, orientation: int) -> QRCommand:
        """Create device orientation command - PRESERVED API"""
        command_data = self._device_builder.create_orientation_command(orientation)
        return self._create_qr_command(command_data, command_data.command_type, command_data.description)
    
    # ========================================
    # LUA SCRIPT COMMANDS - PRESERVED API
    # ========================================
    
    def create_lua_clear_command(self) -> QRCommand:
        """Create command to clear/delete currently loaded Lua script - PRESERVED API"""
        command_data = self._device_builder.create_lua_clear_command()
        return self._create_qr_command(command_data, command_data.command_type, command_data.description)
    
    def create_lua_info_command(self) -> QRCommand:
        """Create command to get Lua script information - PRESERVED API"""
        command_data = self._device_builder.create_lua_info_command()
        return self._create_qr_command(command_data, command_data.command_type, command_data.description)
    
    # ========================================
    # KEY CONFIGURATION COMMANDS - PRESERVED API
    # ========================================
    
    def create_text_action(self, text: str) -> Dict[str, Any]:
        """Create a text action for key configuration - PRESERVED API"""
        return self._key_builder.create_text_action(text)
    
    def create_hid_action(self, keycode: int, modifier: int = 0, delay: int = 10) -> Dict[str, Any]:
        """Create an HID action for key configuration - PRESERVED API"""
        return self._key_builder.create_hid_action(keycode, modifier, delay)
    
    def create_consumer_action(self, control_code: int, delay: int = 10) -> Dict[str, Any]:
        """Create a consumer control action for key configuration - PRESERVED API"""
        return self._key_builder.create_consumer_action(control_code, delay)
    
    def create_key_config_command(self, key_id: int, actions: list) -> QRCommand:
        """Create key configuration command - PRESERVED API"""
        command_data = self._key_builder.create_key_config_command(key_id, actions)
        return self._create_qr_command(command_data, command_data.command_type, command_data.description)
    
    # ========================================
    # FULL KEYBOARD CONFIGURATION - PRESERVED API
    # ========================================
    
    def create_full_keyboard_config(self, 
                                   keyboard_config: Dict[int, List[Dict[str, Any]]],
                                   compression_level: int = 6) -> QRCommand:
        """Create a full keyboard configuration QR code with $FULL: format - PRESERVED API"""
        command_data = self._full_builder.create_full_keyboard_config(keyboard_config, compression_level)
        return self._create_qr_command(command_data, command_data.command_type, command_data.description)
    
    def create_standard_numpad_config(self) -> QRCommand:
        """Create a standard numeric keypad configuration - PRESERVED API"""
        config = {}
        for i in range(10):
            config[i] = [self.create_text_action(str(i))]
        return self.create_full_keyboard_config(config)
    
    def create_standard_alpha_config(self) -> QRCommand:
        """Create a standard alphabetic configuration - PRESERVED API"""
        config = {}
        for i in range(16):
            letter = chr(ord('A') + i)
            config[i] = [self.create_text_action(letter)]
        return self.create_full_keyboard_config(config)
    
    def create_demo_mixed_config(self) -> QRCommand:
        """Create a demonstration configuration with mixed action types - PRESERVED API"""
        config = {
            # Numbers 1-9
            0: [self.create_text_action("1")],
            1: [self.create_text_action("2")], 
            2: [self.create_text_action("3")],
            3: [self.create_text_action("4")],
            4: [self.create_text_action("5")],
            5: [self.create_text_action("6")],
            6: [self.create_text_action("7")],
            7: [self.create_text_action("8")],
            8: [self.create_text_action("9")],
            
            # Letters A-D
            9: [self.create_text_action("A")],
            10: [self.create_text_action("B")],
            11: [self.create_text_action("C")],
            12: [self.create_text_action("D")],
            
            # Special keys with HID codes
            13: [self.create_hid_action(HIDKeyCodes.LEFT_ARROW)],   # ←
            14: [self.create_hid_action(HIDKeyCodes.RIGHT_ARROW)],  # →
            15: [self.create_hid_action(HIDKeyCodes.ENTER)],        # ↵
        }
        
        return self.create_full_keyboard_config(config)
    
    # ========================================
    # LUA SCRIPT DEPLOYMENT - PRESERVED API
    # ========================================
    
    def create_lua_script_qr(self, 
                           script_content: str,
                           max_qr_size: int = 1000,
                           compression_level: int = 6) -> List[QRCommand]:
        """Create QR codes for Lua script deployment - PRESERVED API"""
        command_data_list = self._lua_builder.create_lua_script_commands(
            script_content, max_qr_size, compression_level
        )
        
        qr_commands = []
        for command_data in command_data_list:
            qr_command = self._create_qr_command(command_data, command_data.command_type, command_data.description)
            qr_commands.append(qr_command)
        
        return qr_commands
    
    def create_lua_script_from_file(self, 
                                  script_path: Union[str, Path],
                                  **kwargs) -> List[QRCommand]:
        """Create QR codes from a Lua script file - PRESERVED API"""
        command_data_list = self._lua_builder.create_lua_script_from_file(script_path, **kwargs)
        
        qr_commands = []
        for command_data in command_data_list:
            qr_command = self._create_qr_command(command_data, command_data.command_type, command_data.description)
            qr_commands.append(qr_command)
        
        return qr_commands
    
    # ========================================
    # BATCH OPERATIONS - PRESERVED API
    # ========================================
    
    def save_multiple_qr_codes(self, commands: List[QRCommand], 
                              output_dir: Union[str, Path],
                              filename_prefix: str = "qr_",
                              **qr_kwargs) -> List[str]:
        """Save multiple QR codes to files - PRESERVED API"""
        qr_data_list = []
        
        for command in commands:
            qr_data_list.append({
                'qr_data': command.command_data,
                'title': command.command_type,
                'description': command.description
            })
        
        return self._image_saver.save_multiple_qr_images(
            qr_data_list, output_dir, filename_prefix, **qr_kwargs
        )
    
    def save_lua_script_qr_sequence(self,
                                   script_content: str,
                                   output_dir: Union[str, Path],
                                   filename_prefix: str = "lua_script_",
                                   **kwargs) -> List[str]:
        """Generate and save complete QR sequence for a Lua script - PRESERVED API"""
        # Generate QR commands
        qr_commands = self.create_lua_script_qr(script_content, **kwargs)
        
        # Prepare data for specialized Lua saver
        qr_data_list = []
        for cmd in qr_commands:
            qr_data_list.append({
                'qr_data': cmd.command_data,
                'title': cmd.command_type,
                'description': cmd.description
            })
        
        return self._image_saver.save_lua_script_sequence(
            qr_data_list, output_dir, filename_prefix
        )
    
    # ========================================
    # CONVENIENCE METHODS - PRESERVED API
    # ========================================
    
    def create_quick_text_key(self, key_id: int, text: str) -> QRCommand:
        """Quick method to create a single-text-action key - PRESERVED API"""
        action = self.create_text_action(text)
        return self.create_key_config_command(key_id, [action])
    
    def create_quick_hid_key(self, key_id: int, keycode: int, modifier: int = 0) -> QRCommand:
        """Quick method to create a single-HID-action key - PRESERVED API"""
        action = self.create_hid_action(keycode, modifier)
        return self.create_key_config_command(key_id, [action])