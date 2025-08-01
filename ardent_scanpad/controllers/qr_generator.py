"""
QR Code Generator Controller for aRdent ScanPad

Provides QR code generation for device commands, enabling GUI applications 
to create scannable codes for device configuration without BLE connection.

Architecture:
- Follows same controller pattern as device.py and keys.py
- Reuses all existing constants (LEDs, BuzzerMelodies, HIDKeyCodes, etc.)
- Generates scanner-compatible format ($CMD:DEV: / $CMD:KEY:)
- Creates PNG images with embedded QR codes
"""

import io
import logging
import base64
import zlib
from typing import Optional, Dict, Any, Union, List
from pathlib import Path

try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

from ..utils.constants import (
    KeyTypes, KeyIDs, HIDKeyCodes, ConsumerCodes, 
    LEDs, BuzzerMelodies, DeviceOrientations, KeyboardLayouts
)
from .base import BaseController, Commands

logger = logging.getLogger(__name__)


class QRCommand:
    """
    Wrapper for a generated QR command with metadata and image generation
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
        
    def generate_qr_image(self, 
                         size: int = 300,
                         border: int = 4,
                         error_correction=None) -> Optional['Image.Image']:
        """
        Generate QR code image for this command
        
        Args:
            size: Image size in pixels (square)
            border: QR code border thickness
            error_correction: QR error correction level
            
        Returns:
            PIL Image object or None if qrcode not available
        """
        if not QR_AVAILABLE:
            logger.warning("qrcode library not available. Install with: pip install qrcode[pil]")
            return None
            
        if error_correction is None:
            error_correction = qrcode.constants.ERROR_CORRECT_M
            
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_correction,
            box_size=10,
            border=border,
        )
        qr.add_data(self.command_data)
        qr.make(fit=True)
        
        # Generate image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Resize to requested size
        qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Add title if metadata contains it
        if self.metadata.get('add_title', True):
            qr_img = self._add_title_to_image(qr_img, size)
            
        self._qr_image = qr_img
        return qr_img
    
    def _add_title_to_image(self, qr_img: 'Image.Image', qr_size: int) -> 'Image.Image':
        """Add title and description to QR image"""
        if not QR_AVAILABLE:
            return qr_img
            
        # Calculate title area height
        title_height = 60
        total_height = qr_size + title_height
        
        # Create new image with title area
        final_img = Image.new('RGB', (qr_size, total_height), 'white')
        
        # Paste QR code
        final_img.paste(qr_img, (0, title_height))
        
        # Add text
        draw = ImageDraw.Draw(final_img)
        
        try:
            # Try to use a better font
            font_title = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
            font_desc = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 10)
        except:
            # Fallback to default font
            font_title = ImageFont.load_default()
            font_desc = ImageFont.load_default()
        
        # Draw title
        title_text = f"{self.command_type}"
        title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (qr_size - title_width) // 2
        draw.text((title_x, 5), title_text, fill='black', font=font_title)
        
        # Draw description  
        desc_text = self.description[:50] + ("..." if len(self.description) > 50 else "")
        desc_bbox = draw.textbbox((0, 0), desc_text, font=font_desc)
        desc_width = desc_bbox[2] - desc_bbox[0]
        desc_x = (qr_size - desc_width) // 2
        draw.text((desc_x, 25), desc_text, fill='gray', font=font_desc)
        
        return final_img
    
    def save(self, filename: Union[str, Path], **kwargs) -> bool:
        """
        Save QR code as PNG image
        
        Args:
            filename: Output filename
            **kwargs: Additional arguments for generate_qr_image()
            
        Returns:
            True if saved successfully
        """
        try:
            if self._qr_image is None:
                self._qr_image = self.generate_qr_image(**kwargs)
                
            if self._qr_image is None:
                logger.error("Cannot generate QR image - qrcode library not available")
                return False
                
            self._qr_image.save(filename, 'PNG')
            logger.info(f"QR code saved to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save QR code: {e}")
            return False
    
    def __str__(self) -> str:
        return f"QRCommand({self.command_type}: {self.description})"


class QRGeneratorController:
    """
    QR Code Generator Controller - Follows same pattern as other controllers
    
    This controller generates QR codes for device commands without requiring
    BLE connection. Reuses all existing constants and command structures.
    """
    
    def __init__(self):
        """Initialize QR code generator controller"""
        self._logger = logging.getLogger(self.__class__.__name__)
        self._validate_dependencies()
        
    def _validate_dependencies(self):
        """Check if required libraries are available"""
        if not QR_AVAILABLE:
            self._logger.warning(
                "QR code generation requires additional dependencies. "
                "Install with: pip install qrcode[pil]"
            )
    
    # ========================================
    # COMMAND FORMAT HELPERS
    # ========================================
    
    def _create_device_command(self, command_id: int, payload: bytes, 
                              command_type: str, description: str, 
                              metadata: Dict[str, Any] = None) -> QRCommand:
        """Create device domain command QR code"""
        hex_data = payload.hex().upper()
        command_data = f"$CMD:DEV:{command_id:02X}{hex_data}CMD$"
        
        full_metadata = {
            'domain': 'device',
            'command_id': command_id,
            'payload_hex': hex_data,
            **(metadata or {})
        }
        
        return QRCommand(command_data, command_type, description, full_metadata)
    
    def _create_config_command(self, command_id: int, payload: bytes,
                              command_type: str, description: str,
                              metadata: Dict[str, Any] = None) -> QRCommand:
        """Create config domain command QR code"""
        hex_data = payload.hex().upper()
        command_data = f"$CMD:KEY:{command_id:02X}{hex_data}CMD$"
        
        full_metadata = {
            'domain': 'config', 
            'command_id': command_id,
            'payload_hex': hex_data,
            **(metadata or {})
        }
        
        return QRCommand(command_data, command_type, description, full_metadata)
    
    # ========================================
    # LED COMMANDS
    # ========================================
    
    def create_led_on_command(self, led_id: int) -> QRCommand:
        """Create LED ON command"""
        if led_id not in LEDs.ALL:
            raise ValueError(f"Invalid LED ID {led_id}. Must be one of: {LEDs.ALL}")
            
        payload = bytes([led_id, 1])  # led_id, state=on
        led_name = LEDs.NAMES.get(led_id, f"LED {led_id}")
        
        return self._create_device_command(
            Commands.LED_SET_STATE, payload,
            "LED Control", f"Turn {led_name} ON",
            {'led_id': led_id, 'state': 'on'}
        )
    
    def create_led_off_command(self, led_id: int) -> QRCommand:
        """Create LED OFF command"""
        if led_id not in LEDs.ALL:
            raise ValueError(f"Invalid LED ID {led_id}. Must be one of: {LEDs.ALL}")
            
        payload = bytes([led_id, 0])  # led_id, state=off  
        led_name = LEDs.NAMES.get(led_id, f"LED {led_id}")
        
        return self._create_device_command(
            Commands.LED_SET_STATE, payload,
            "LED Control", f"Turn {led_name} OFF",
            {'led_id': led_id, 'state': 'off'}
        )
    
    def create_all_leds_off_command(self) -> QRCommand:
        """Create command to turn all LEDs off"""
        return self._create_device_command(
            Commands.LED_ALL_OFF, bytes(),
            "LED Control", "Turn ALL LEDs OFF",
            {'action': 'all_off'}
        )
    
    # ========================================  
    # BUZZER COMMANDS
    # ========================================
    
    def create_buzzer_melody_command(self, melody_name: str) -> QRCommand:
        """Create buzzer melody command"""
        melody_map = {
            'KEY': BuzzerMelodies.KEY,
            'START': BuzzerMelodies.START,
            'STOP': BuzzerMelodies.STOP,
            'NOTIF_UP': BuzzerMelodies.NOTIF_UP,
            'NOTIF_DOWN': BuzzerMelodies.NOTIF_DOWN,
            'CONFIRM': BuzzerMelodies.CONFIRM,
            'WARNING': BuzzerMelodies.WARNING,
            'ERROR': BuzzerMelodies.ERROR,
            'SUCCESS': BuzzerMelodies.SUCCESS
        }
        
        melody_upper = melody_name.upper()
        if melody_upper not in melody_map:
            raise ValueError(f"Invalid melody '{melody_name}'. Must be one of: {list(melody_map.keys())}")
            
        melody_id = melody_map[melody_upper]
        payload = bytes([melody_id])
        
        return self._create_device_command(
            Commands.BUZZER_MELODY, payload,
            "Buzzer Control", f"Play {melody_name} melody",
            {'melody_name': melody_name, 'melody_id': melody_id}
        )
    
    # ========================================
    # DEVICE SETTINGS COMMANDS  
    # ========================================
    
    def create_orientation_command(self, orientation: int) -> QRCommand:
        """Create device orientation command"""
        if orientation not in [0, 1, 2, 3]:
            raise ValueError(f"Orientation must be 0-3, got {orientation}")
            
        orientation_names = {
            0: "Portrait", 1: "Landscape", 
            2: "Reverse Portrait", 3: "Reverse Landscape"
        }
        
        payload = bytes([orientation])
        
        return self._create_device_command(
            Commands.DEVICE_SET_ORIENTATION, payload,
            "Device Settings", f"Set orientation to {orientation_names[orientation]}",
            {'orientation': orientation, 'orientation_name': orientation_names[orientation]}
        )
    
    # ========================================
    # KEY CONFIGURATION COMMANDS
    # ========================================
    
    def create_text_action(self, text: str) -> Dict[str, Any]:
        """Create a text action for key configuration (helper method)"""
        if len(text.encode('utf-8')) > 8:
            raise ValueError(f"Text too long (max 8 UTF-8 bytes): {text}")
            
        return {
            'type': KeyTypes.UTF8,
            'text': text,
            'delay': 10
        }
    
    def create_hid_action(self, keycode: int, modifier: int = 0, delay: int = 10) -> Dict[str, Any]:
        """Create an HID action for key configuration (helper method)"""
        if not (0 <= keycode <= 255):
            raise ValueError(f"HID keycode must be 0-255, got {keycode}")
        if not (0 <= modifier <= 255): 
            raise ValueError(f"HID modifier must be 0-255, got {modifier}")
            
        return {
            'type': KeyTypes.HID,
            'value': keycode,
            'mask': modifier,
            'delay': delay
        }
    
    def create_consumer_action(self, control_code: int, delay: int = 10) -> Dict[str, Any]:
        """Create a consumer control action for key configuration (helper method)"""
        if not (0 <= control_code <= 65535):
            raise ValueError(f"Consumer control code must be 0-65535, got {control_code}")
            
        return {
            'type': KeyTypes.CONSUMER,
            'value': control_code,
            'delay': delay
        }
    
    def create_key_config_command(self, key_id: int, actions: list) -> QRCommand:
        """Create key configuration command"""
        if not (0 <= key_id <= 19):
            raise ValueError(f"Key ID must be 0-19, got {key_id}")
        if len(actions) > 10:
            raise ValueError(f"Maximum 10 actions per key, got {len(actions)}")
        if not actions:
            raise ValueError("At least one action required")
            
        # Build payload matching keys controller format: [key_id][action_count][actions...]
        payload = bytearray([key_id, len(actions)])
        
        for i, action in enumerate(actions):
            if not isinstance(action, dict) or 'type' not in action:
                raise ValueError(f"Action {i} must be dict with 'type' key")
                
            action_type = action['type']
            value = action.get('value', 0)
            mask = action.get('mask', 0) 
            delay = action.get('delay', 10)
            
            # Add action following keys controller format:
            # [action_index][action_type][value][mask][delay_low][delay_high]
            payload.extend([
                i,  # action index
                action_type,
                value & 0xFF,
                mask,
                delay & 0xFF,        # delay low byte
                (delay >> 8) & 0xFF  # delay high byte
            ])
            
            # Add UTF-8 text data for text actions (matching keys controller)
            if action_type == KeyTypes.UTF8 and 'text' in action:
                text = action['text']
                if text:
                    text_bytes = text.encode('utf-8')
                    if len(text_bytes) <= 8:
                        # UTF-8 fits within 8-byte limit
                        payload.extend([len(text_bytes)] + list(text_bytes))
                    else:
                        # UTF-8 exceeds 8-byte limit - truncate
                        truncated_bytes = text_bytes[:8]
                        payload.extend([len(truncated_bytes)] + list(truncated_bytes))
                else:
                    # Empty text
                    payload.extend([0])  # No UTF-8 data
        
        # Get key name
        key_name = KeyIDs.NAMES.get(key_id, f"Key {key_id}")
        
        return self._create_config_command(
            Commands.SET_KEY_CONFIG, bytes(payload),
            "Key Configuration", f"Configure {key_name} ({len(actions)} actions)",
            {'key_id': key_id, 'key_name': key_name, 'action_count': len(actions)}
        )
    
    # ========================================
    # CONVENIENCE METHODS
    # ========================================
    
    def create_quick_text_key(self, key_id: int, text: str) -> QRCommand:
        """Quick method to create a single-text-action key"""
        action = self.create_text_action(text)
        return self.create_key_config_command(key_id, [action])
    
    def create_quick_hid_key(self, key_id: int, keycode: int, modifier: int = 0) -> QRCommand:
        """Quick method to create a single-HID-action key"""
        action = self.create_hid_action(keycode, modifier)
        return self.create_key_config_command(key_id, [action])
    
    # ========================================
    # BATCH OPERATIONS
    # ========================================
    
    def save_multiple_qr_codes(self, commands: List[QRCommand], 
                              output_dir: Union[str, Path],
                              filename_prefix: str = "qr_",
                              **qr_kwargs) -> List[str]:
        """
        Save multiple QR codes to files
        
        Args:
            commands: List of QRCommand objects
            output_dir: Output directory path
            filename_prefix: Prefix for generated filenames
            **qr_kwargs: Additional arguments for QR generation
            
        Returns:
            List of generated filenames
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        for i, command in enumerate(commands):
            # Generate safe filename from command description
            safe_desc = "".join(c for c in command.description if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_desc = safe_desc.replace(' ', '_')[:50]  # Limit length
            
            filename = f"{filename_prefix}{i:03d}_{safe_desc}.png"
            filepath = output_path / filename
            
            try:
                if command.save(filepath, **qr_kwargs):
                    saved_files.append(str(filepath))
                    self._logger.info(f"Saved QR code: {filepath}")
                else:
                    self._logger.error(f"Failed to save QR code: {filepath}")
            except Exception as e:
                self._logger.error(f"Error saving {filepath}: {e}")
        
        return saved_files
    
    # ========================================
    # FULL KEYBOARD CONFIGURATION ($FULL:)
    # ========================================
    
    def create_full_keyboard_config(self, 
                                   keyboard_config: Dict[int, List[Dict[str, Any]]],
                                   compression_level: int = 6) -> QRCommand:
        """
        Create a full keyboard configuration QR code with $FULL: format
        
        This method generates a compressed QR code containing the complete
        keyboard configuration for all specified keys using the binary format:
        
        Header: [GYW][version][key_count]
        Per Key: [key_id][action_count][actions...]
        Per Action: [type][delay/text_len][value/text_data...] (depending on type)
        
        Args:
            keyboard_config: Dict mapping key_id (0-19) to list of actions
            compression_level: zlib compression level (1-9, 6=default)
            
        Returns:
            QRCommand with $FULL: format
            
        Example:
            config = {
                0: [qr.create_text_action("1")],
                1: [qr.create_text_action("2")], 
                2: [qr.create_hid_action(HIDKeyCodes.ENTER)]
            }
            full_qr = qr.create_full_keyboard_config(config)
        """
        if not keyboard_config:
            raise ValueError("Keyboard configuration cannot be empty")
            
        if not (1 <= compression_level <= 9):
            raise ValueError("Compression level must be 1-9")
            
        # Validate key IDs and actions
        for key_id, actions in keyboard_config.items():
            if not (0 <= key_id <= 19):
                raise ValueError(f"Key ID must be 0-19, got {key_id}")
            if not actions:
                raise ValueError(f"Key {key_id} must have at least one action")
            if len(actions) > 10:
                raise ValueError(f"Key {key_id} has too many actions (max 10): {len(actions)}")
                
        # Build binary configuration
        binary_config = bytearray()
        
        # Header: Magic + Version + Key Count
        binary_config.extend(b"GYW")  # Magic header
        binary_config.append(0x01)   # Version
        binary_config.append(len(keyboard_config))  # Key count
        
        # Process each key
        total_actions = 0
        for key_id in sorted(keyboard_config.keys()):
            actions = keyboard_config[key_id]
            
            # Key header: [key_id][action_count]
            binary_config.append(key_id)
            binary_config.append(len(actions))
            
            # Process each action
            for action in actions:
                if not isinstance(action, dict) or 'type' not in action:
                    raise ValueError(f"Key {key_id} action must be dict with 'type' key")
                    
                action_type = action['type']
                
                if action_type == KeyTypes.UTF8:
                    # UTF-8 text action: [type=0][text_len][delay][text_data...]
                    text = action.get('text', '')
                    delay = action.get('delay', 10)
                    
                    text_bytes = text.encode('utf-8')
                    if len(text_bytes) > 8:
                        raise ValueError(f"Key {key_id} text too long (max 8 UTF-8 bytes): {text}")
                        
                    binary_config.append(0)  # UTF-8 type
                    binary_config.append(len(text_bytes))  # text length
                    binary_config.append(delay & 0xFF)     # delay
                    binary_config.extend(text_bytes)       # text data
                    
                elif action_type == KeyTypes.HID:
                    # HID action: [type=1][hid_code][modifiers][delay]
                    value = action.get('value', 0)
                    mask = action.get('mask', 0)
                    delay = action.get('delay', 10)
                    
                    if not (0 <= value <= 255):
                        raise ValueError(f"Key {key_id} HID value must be 0-255: {value}")
                    if not (0 <= mask <= 255):
                        raise ValueError(f"Key {key_id} HID mask must be 0-255: {mask}")
                        
                    binary_config.append(1)        # HID type
                    binary_config.append(value)    # HID keycode
                    binary_config.append(mask)     # HID modifiers 
                    binary_config.append(delay & 0xFF)  # delay
                    
                else:
                    raise ValueError(f"Key {key_id} unsupported action type: {action_type}")
                    
                total_actions += 1
        
        # Compress binary configuration
        try:
            compressed_data = zlib.compress(bytes(binary_config), level=compression_level)
        except Exception as e:
            raise ValueError(f"Compression failed: {e}")
            
        # Encode to Base64
        try:
            b64_data = base64.b64encode(compressed_data).decode('ascii')
        except Exception as e:
            raise ValueError(f"Base64 encoding failed: {e}")
            
        # Create $FULL: command
        command_data = f"$FULL:{b64_data}$"
        
        # Calculate compression statistics
        original_size = len(binary_config)
        compressed_size = len(compressed_data)
        b64_size = len(b64_data)
        compression_ratio = (compressed_size / original_size) * 100 if original_size > 0 else 0
        
        description = f"Full keyboard: {len(keyboard_config)} keys, {total_actions} actions"
        
        metadata = {
            'keys_configured': len(keyboard_config),
            'total_actions': total_actions,
            'original_size_bytes': original_size,
            'compressed_size_bytes': compressed_size,
            'base64_size_chars': b64_size,
            'compression_ratio_percent': round(compression_ratio, 1),
            'compression_level': compression_level,
            'qr_format': 'FULL'
        }
        
        return QRCommand(command_data, "Full Keyboard Config", description, metadata)
    
    def create_standard_numpad_config(self) -> QRCommand:
        """
        Create a standard numeric keypad configuration (keys 0-9)
        
        Returns:
            QRCommand with numeric keypad layout
        """
        config = {}
        
        # Keys 0-9 with corresponding numbers
        for i in range(10):
            config[i] = [self.create_text_action(str(i))]
            
        return self.create_full_keyboard_config(config)
    
    def create_standard_alpha_config(self) -> QRCommand:
        """
        Create a standard alphabetic configuration (A-P for keys 0-15)
        
        Returns:
            QRCommand with alphabetic layout
        """
        config = {}
        
        # Keys 0-15 with letters A-P
        for i in range(16):
            letter = chr(ord('A') + i)  # A, B, C, ..., P
            config[i] = [self.create_text_action(letter)]
            
        return self.create_full_keyboard_config(config)
    
    def create_demo_mixed_config(self) -> QRCommand:
        """
        Create a demonstration configuration with mixed action types
        
        Returns:
            QRCommand with demonstration layout including text, HID, and special keys
        """
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