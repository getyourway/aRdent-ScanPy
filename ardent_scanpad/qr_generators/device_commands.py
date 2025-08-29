"""
Device Commands QR Generator

Hybrid API for device commands:
- JSON-driven approach for batch device configurations
- Traditional methods for direct device control
- Both use the same modular QR backend
"""

import logging
from typing import Dict, Any, List, Union, Optional
from pathlib import Path

from .utils.json_support import JSONValidator
from .utils.qr_core import QRCore, QRCommand


class DeviceCommandGenerator:
    """
    Hybrid device command generator
    
    Supports both JSON-driven and traditional API approaches for device commands
    """
    
    def __init__(self):
        self._qr_core = QRCore()
        self._logger = logging.getLogger(self.__class__.__name__)
    
    # ===== JSON API =====
    
    def from_json_file(self, filepath: Union[str, Path]) -> List[QRCommand]:
        """
        Generate QR codes from JSON device command file
        
        Args:
            filepath: Path to JSON device command file
            
        Returns:
            List of QRCommand objects
        """
        json_data = JSONValidator.load_json_file(filepath)
        return self.from_json(json_data)
    
    def from_json(self, json_data: Dict[str, Any]) -> List[QRCommand]:
        """
        Generate QR codes from JSON device commands
        
        Format: {"commands": {"led_1_on": {}, "buzzer_success": {}}}
        
        Args:
            json_data: JSON device command dict
            
        Returns:
            List of QRCommand objects
        """
        # Validate JSON structure
        JSONValidator.validate_device_json(json_data)
        
        # Handle device commands
        if 'commands' in json_data:
            commands_data = json_data['commands']
            
            if not isinstance(commands_data, dict):
                raise ValueError("Commands must be an object. List format is not supported.")
            
            self._logger.info("📱 Processing device commands")
            return self._create_batch_qr_command(json_data)
        
        return []
    

    def _build_binary_command(self, cmd_data: Dict[str, Any]) -> bytes:
        """
        Build binary command from JSON command data
        Reuses existing QRCore command builders
        """
        domain = cmd_data.get('domain', '')
        action = cmd_data.get('action', '')
        parameters = cmd_data.get('parameters', {})
        
        # Route to appropriate command builder based on domain via QRCore
        # CRITICAL FIX: Return [command_id] + payload instead of just payload
        if domain == 'led_control':
            if action == 'led_on':
                led_id = parameters.get('led_id', 1)
                cmd_obj = self._qr_core._led_builder.create_led_on_command(led_id)
                return bytes([cmd_obj.command_id]) + cmd_obj.payload
            elif action == 'led_off':
                led_id = parameters.get('led_id', 1)
                cmd_obj = self._qr_core._led_builder.create_led_off_command(led_id)
                return bytes([cmd_obj.command_id]) + cmd_obj.payload
            elif action == 'all_leds_off':
                cmd_obj = self._qr_core._led_builder.create_all_leds_off_command()
                return bytes([cmd_obj.command_id]) + cmd_obj.payload
                
        elif domain == 'buzzer_control':
            if action == 'play_melody':
                melody = parameters.get('melody', 'SUCCESS')
                cmd_obj = self._qr_core._buzzer_builder.create_buzzer_melody_command(melody)
                return bytes([cmd_obj.command_id]) + cmd_obj.payload
                
        elif domain == 'device_settings':
            if action == 'set_orientation':
                orientation = parameters.get('orientation', 0)
                cmd_obj = self._qr_core._device_builder.create_orientation_command(orientation)
                return bytes([cmd_obj.command_id]) + cmd_obj.payload
                
        elif domain == 'lua_management':
            if action == 'clear_script':
                cmd_obj = self._qr_core._device_builder.create_lua_clear_command()
                return bytes([cmd_obj.command_id]) + cmd_obj.payload
            elif action == 'get_script_info':
                cmd_obj = self._qr_core._device_builder.create_lua_info_command()
                return bytes([cmd_obj.command_id]) + cmd_obj.payload
        
        # If we reach here, command is not supported
        raise ValueError(f"Unsupported command: {domain}.{action}")
    
    def _create_batch_qr_command(self, json_data: Dict[str, Any]) -> List[QRCommand]:
        """
        Create a single QR code containing multiple device commands
        Format: $BATCH:base64_encoded_binary_commands$
        Binary format: [count][len1][cmd1][len2][cmd2]...
        """
        import base64
        import struct
        
        # Extract commands and metadata
        commands_data = json_data['commands']
        metadata = json_data.get('metadata', {})
        
        # Use shared command parser utility
        from ..utils.command_parser import CommandParser
        
        try:
            # Parse JSON to binary commands using shared utility
            commands = CommandParser.parse_json_commands(json_data)
            # Convert to old format for compatibility with batch creation
            binary_commands = []
            for command_id, payload in commands:
                binary_commands.append(bytes([command_id]) + payload)
        except Exception as e:
            self._logger.error(f"Error parsing commands: {e}")
            return []
        
        if not binary_commands:
            self._logger.error("No valid commands to batch")
            return []
        
        # Build batch binary format: [count][len1][cmd1][len2][cmd2]...
        try:
            batch_binary = struct.pack('B', len(binary_commands))  # command count
            for cmd_binary in binary_commands:
                batch_binary += struct.pack('B', len(cmd_binary)) + cmd_binary  # length + command
            
            # Base64 encode the binary data
            b64_data = base64.b64encode(batch_binary).decode('ascii')
        except Exception as e:
            self._logger.error(f"Failed to encode batch commands: {e}")
            return []
        
        # Create batch QR command
        command_data = f"$BATCH:{b64_data}$"
        
        # Generate description
        command_count = len(commands_data)
        command_types = set()
        for cmd in commands_data:
            command_types.add(f"{cmd['domain']}.{cmd['action']}")
        
        description = f"Device Batch: {command_count} commands ({', '.join(sorted(command_types))})"
        
        # Create metadata
        qr_metadata = {
            'qr_format': 'BATCH',
            'command_count': command_count,
            'commands': command_types,
            'binary_size_bytes': len(batch_binary),
            'base64_size_chars': len(b64_data),
            'qr_size_chars': len(command_data),
            **metadata
        }
        
        # Use legacy QRCommand class for direct string command
        from ..controllers.qr_generator import QRCommand
        
        batch_qr = QRCommand(
            command_data,
            "Device Batch Commands",
            description,
            qr_metadata
        )
        
        return [batch_qr]
    
    def _process_single_command(self, cmd_json: Dict[str, Any]) -> Optional[QRCommand]:
        """Process a single device command from JSON"""
        domain = cmd_json['domain']
        action = cmd_json['action']
        params = cmd_json.get('parameters', {})
        
        # LED Control
        if domain == 'led_control':
            if action == 'led_on':
                return self._qr_core.create_led_on_command(params['led_id'])
            elif action == 'led_off':
                return self._qr_core.create_led_off_command(params['led_id'])
            elif action == 'all_leds_off':
                return self._qr_core.create_all_leds_off_command()
        
        # Buzzer Control
        elif domain == 'buzzer_control':
            if action == 'play_melody':
                return self._qr_core.create_buzzer_melody_command(params['melody'])
        
        # Device Settings
        elif domain == 'device_settings':
            if action == 'set_orientation':
                return self._qr_core.create_orientation_command(params['orientation'])
        
        # Lua Management
        elif domain == 'lua_management':
            if action == 'clear_script':
                return self._qr_core.create_lua_clear_command()
            elif action == 'get_script_info':
                return self._qr_core.create_lua_info_command()
        
        self._logger.warning(f"Unsupported command: {domain}.{action}")
        return None
    
    # ===== Traditional API =====
    
    def create_led_on_command(self, led_id: int) -> QRCommand:
        """Create LED ON command (traditional API)"""
        return self._qr_core.create_led_on_command(led_id)
    
    def create_led_off_command(self, led_id: int) -> QRCommand:
        """Create LED OFF command (traditional API)"""
        return self._qr_core.create_led_off_command(led_id)
    
    def create_all_leds_off_command(self) -> QRCommand:
        """Create all LEDs OFF command (traditional API)"""
        return self._qr_core.create_all_leds_off_command()
    
    def create_buzzer_melody_command(self, melody_name: str) -> QRCommand:
        """Create buzzer melody command (traditional API)"""
        return self._qr_core.create_buzzer_melody_command(melody_name)
    
    def create_orientation_command(self, orientation: int) -> QRCommand:
        """Create device orientation command (traditional API)"""
        return self._qr_core.create_orientation_command(orientation)
    
    def create_lua_clear_command(self) -> QRCommand:
        """Create Lua script clear command (traditional API)"""
        return self._qr_core.create_lua_clear_command()
    
    def create_lua_info_command(self) -> QRCommand:
        """Create Lua script info command (traditional API)"""
        return self._qr_core.create_lua_info_command()
    
    # ===== Utility Methods =====
    
    def save_qr_codes(self, qr_commands: List[QRCommand], output_dir: Union[str, Path],
                     filename_prefix: str = "device_", **kwargs) -> List[str]:
        """
        Save QR codes to files
        
        Args:
            qr_commands: List of QRCommand objects
            output_dir: Output directory
            filename_prefix: Filename prefix
            **kwargs: Additional QR generation options
            
        Returns:
            List of saved file paths
        """
        return self._qr_core.save_multiple_qr_codes(
            qr_commands, output_dir, filename_prefix, **kwargs
        )