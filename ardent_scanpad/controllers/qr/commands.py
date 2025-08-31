"""
QR Command Builders

Builds command payloads for different device domains:
- LED commands
- Buzzer commands  
- Device settings
- Key configuration
- Lua scripts
"""

import base64
import zlib
from typing import Dict, Any, List, Union
from pathlib import Path

from ...utils.constants import (
    KeyTypes, LEDs, BuzzerMelodies, KeyIDs
)
from ..base import Commands


class CommandData:
    """Container for command data"""
    
    def __init__(self, command_id: int, payload: bytes, domain: str, 
                 command_type: str, description: str, metadata: Dict[str, Any] = None):
        self.command_id = command_id
        self.payload = payload
        self.domain = domain  # 'device' or 'config'
        self.command_type = command_type
        self.description = description
        self.metadata = metadata or {}


class LEDCommandBuilder:
    """LED command payload builder"""
    
    def create_led_on_command(self, led_id: int) -> CommandData:
        if led_id not in LEDs.ALL:
            raise ValueError(f"Invalid LED ID {led_id}. Must be one of: {LEDs.ALL}")
            
        payload = bytes([led_id, 1])  # led_id, state=on
        led_name = LEDs.NAMES.get(led_id, f"LED {led_id}")
        
        return CommandData(
            Commands.LED_SET_STATE, payload, 'device',
            "LED Control", f"Turn {led_name} ON",
            {'led_id': led_id, 'state': 'on'}
        )
    
    def create_led_off_command(self, led_id: int) -> CommandData:
        if led_id not in LEDs.ALL:
            raise ValueError(f"Invalid LED ID {led_id}. Must be one of: {LEDs.ALL}")
            
        payload = bytes([led_id, 0])  # led_id, state=off  
        led_name = LEDs.NAMES.get(led_id, f"LED {led_id}")
        
        return CommandData(
            Commands.LED_SET_STATE, payload, 'device',
            "LED Control", f"Turn {led_name} OFF",
            {'led_id': led_id, 'state': 'off'}
        )
    
    def create_all_leds_off_command(self) -> CommandData:
        return CommandData(
            Commands.LED_ALL_OFF, bytes(), 'device',
            "LED Control", "Turn ALL LEDs OFF",
            {'action': 'all_off'}
        )


class BuzzerCommandBuilder:
    """Buzzer command payload builder"""
    
    def create_buzzer_melody_command(self, melody_name: str) -> CommandData:
        # Use BuzzerMelodies constants directly instead of mapping dict
        melody_upper = melody_name.upper()
        
        # Validate melody name exists in BuzzerMelodies
        if not hasattr(BuzzerMelodies, melody_upper):
            available_melodies = [name for name in dir(BuzzerMelodies) if not name.startswith('_') and name != 'NAMES']
            raise ValueError(f"Invalid melody '{melody_name}'. Must be one of: {available_melodies}")
            
        melody_id = getattr(BuzzerMelodies, melody_upper)
        payload = bytes([melody_id])
        
        return CommandData(
            Commands.BUZZER_MELODY, payload, 'device',
            "Buzzer Control", f"Play {melody_name} melody",
            {'melody_name': melody_name, 'melody_id': melody_id}
        )


class DeviceCommandBuilder:
    """Device settings command payload builder"""
    
    def create_orientation_command(self, orientation: int) -> CommandData:
        if orientation not in [0, 1, 2, 3]:
            raise ValueError(f"Orientation must be 0-3, got {orientation}")
            
        orientation_names = {
            0: "Portrait", 1: "Landscape", 
            2: "Reverse Portrait", 3: "Reverse Landscape"
        }
        
        payload = bytes([orientation])
        
        return CommandData(
            Commands.DEVICE_SET_ORIENTATION, payload, 'device',
            "Device Settings", f"Set orientation to {orientation_names[orientation]}",
            {'orientation': orientation, 'orientation_name': orientation_names[orientation]}
        )
    
    def create_lua_clear_command(self) -> CommandData:
        return CommandData(
            Commands.LUA_CLEAR_SCRIPT, bytes(), 'device',
            "Lua Script Management", "Clear Lua Script",
            {'action': 'clear_script', 'effect': 'removes_current_script'}
        )
    
    def create_lua_info_command(self) -> CommandData:
        return CommandData(
            Commands.LUA_GET_SCRIPT_INFO, bytes(), 'device',
            "Lua Script Management", "Get Lua Script Info", 
            {'action': 'get_info', 'returns': 'script_status'}
        )


class KeyConfigCommandBuilder:
    """Key configuration command payload builder"""
    
    def create_text_action(self, text: str) -> Dict[str, Any]:
        if len(text.encode('utf-8')) > 8:
            raise ValueError(f"Text too long (max 8 UTF-8 bytes): {text}")
            
        return {
            'type': KeyTypes.UTF8,
            'text': text,
            'delay': 10
        }
    
    def create_hid_action(self, keycode: int, modifier: int = 0, delay: int = 10) -> Dict[str, Any]:
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
        if not (0 <= control_code <= 65535):
            raise ValueError(f"Consumer control code must be 0-65535, got {control_code}")
            
        return {
            'type': KeyTypes.CONSUMER,
            'value': control_code,
            'delay': delay
        }
    
    def create_key_config_command(self, key_id: int, actions: list) -> CommandData:
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
        
        return CommandData(
            Commands.SET_KEY_CONFIG, bytes(payload), 'config',
            "Key Configuration", f"Configure {key_name} ({len(actions)} actions)",
            {'key_id': key_id, 'key_name': key_name, 'action_count': len(actions)}
        )


class FullConfigCommandBuilder:
    """Full keyboard configuration command builder"""
    
    def __init__(self):
        self._key_builder = KeyConfigCommandBuilder()
    
    def create_full_keyboard_config(self, 
                                   keyboard_config: Dict[int, List[Dict[str, Any]]],
                                   compression_level: int = 6) -> CommandData:
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
            'qr_format': 'FULL',
            'b64_data': b64_data  # Used by formatter
        }
        
        return CommandData(
            0, bytes(), 'full',  # Special case - no command_id for FULL format
            "Full Keyboard Config", description, metadata
        )


class LuaCommandBuilder:
    """Lua script command builder"""
    
    def create_lua_script_commands(self, 
                                  script_content: str,
                                  max_qr_size: int = 1000,
                                  compression_level: int = 6) -> List[CommandData]:
        if not script_content.strip():
            raise ValueError("Script content cannot be empty")
            
        if not (1 <= compression_level <= 9):
            raise ValueError("Compression level must be 1-9")
            
        if max_qr_size < 100:
            raise ValueError("max_qr_size too small (min 100 bytes)")
        
        try:
            # Compress the script
            script_bytes = script_content.encode('utf-8')
            compressed_data = zlib.compress(script_bytes, level=compression_level)
            
            # Encode to base64
            b64_data = base64.b64encode(compressed_data).decode('ascii')
            
        except Exception as e:
            raise ValueError(f"Script compression/encoding failed: {e}")
        
        # Calculate compression statistics
        original_size = len(script_bytes)
        compressed_size = len(compressed_data)
        b64_size = len(b64_data)
        compression_ratio = (compressed_size / original_size) * 100 if original_size > 0 else 0
        
        # Calculate fragment overhead: "$LUAn:" + "$" = 7 chars for fragment 1-9, 8 chars for 10+
        base_overhead = 7  # Assume single digit fragments initially
        available_size = max_qr_size - base_overhead
        
        if available_size <= 0:
            raise ValueError(f"max_qr_size {max_qr_size} too small for fragment overhead")
        
        # Fragment the base64 data
        fragments = []
        offset = 0
        fragment_num = 1
        
        while offset < len(b64_data):
            # Adjust overhead for fragment number
            current_overhead = 7 if fragment_num <= 9 else 8  # $LUA1:$ vs $LUA10:$
            current_available = max_qr_size - current_overhead
            
            if current_available <= 0:
                raise ValueError(f"Fragment {fragment_num}: max_qr_size too small")
            
            # Check if this is the last fragment
            remaining_data = len(b64_data) - offset
            if remaining_data <= current_available:
                # Last fragment - take ALL remaining data
                fragment_data = b64_data[offset:]
                fragments.append(fragment_data)
                break
            else:
                # Intermediate fragment - limit by current_available
                fragment_data = b64_data[offset:offset + current_available]
                fragments.append(fragment_data)
                
                offset += len(fragment_data)
                fragment_num += 1
            
            # Safety check to prevent infinite loop
            if fragment_num > 99:
                raise ValueError("Script too large (would require >99 QR fragments)")
        
        if not fragments:
            raise ValueError("No fragments generated (empty script?)")
        
        # Generate CommandData objects
        command_list = []
        total_fragments = len(fragments)
        
        for i, fragment_data in enumerate(fragments):
            fragment_num = i + 1
            
            # Generate description
            if total_fragments == 1:
                description = f"Lua Script ({original_size} bytes, {compression_ratio:.1f}% compressed)"
                fragment_desc = "Execute"
            elif fragment_num == total_fragments:
                description = f"Lua Script Fragment {fragment_num}/{total_fragments} (Execute)"
                fragment_desc = f"Fragment {fragment_num}/{total_fragments} (Execute)"
            else:
                description = f"Lua Script Fragment {fragment_num}/{total_fragments}"
                fragment_desc = f"Fragment {fragment_num}/{total_fragments}"
            
            # Create metadata
            metadata = {
                'script_type': 'lua',
                'fragment_number': fragment_num,
                'total_fragments': total_fragments,
                'fragment_data': fragment_data,  # Used by formatter
                'fragment_size_chars': len(fragment_data),
                'is_final_fragment': fragment_num == total_fragments,
                'original_size_bytes': original_size,
                'compressed_size_bytes': compressed_size,
                'base64_size_chars': b64_size,
                'compression_ratio_percent': round(compression_ratio, 1),
                'compression_level': compression_level
            }
            
            # Add overall statistics to first fragment
            if fragment_num == 1:
                metadata.update({
                    'script_preview': script_content[:100] + ("..." if len(script_content) > 100 else ""),
                    'script_lines': len(script_content.split('\n'))
                })
            
            command_data = CommandData(
                0, bytes(), 'lua',  # Special case - no command_id for Lua format
                "Lua Script Deployment", description, metadata
            )
            
            command_list.append(command_data)
        
        return command_list
    
    def create_lua_script_from_file(self, 
                                   script_path: Union[str, Path],
                                   **kwargs) -> List[CommandData]:
        script_file = Path(script_path)
        
        if not script_file.exists():
            raise FileNotFoundError(f"Script file not found: {script_path}")
        
        if not script_file.suffix.lower() == '.lua':
            pass  # Warning suppressed - just log it
        
        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                script_content = f.read()
        except Exception as e:
            raise ValueError(f"Failed to read script file {script_path}: {e}")
        
        # Generate commands
        commands = self.create_lua_script_commands(script_content, **kwargs)
        
        # Add file info to all commands
        for cmd in commands:
            cmd.metadata.update({
                'script_filename': script_file.name,
                'script_filepath': str(script_file),
                'file_size_bytes': script_file.stat().st_size
            })
        
        return commands