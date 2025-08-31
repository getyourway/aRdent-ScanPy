"""
Device Commands QR Generator

Hybrid API for device commands:
- JSON-driven approach for batch device configurations
- Traditional methods for direct device control
- Both use the same modular QR backend
"""

import logging
import struct
from typing import Dict, Any, List, Union, Optional, Callable
from pathlib import Path

from .utils.json_support import JSONValidator
from .utils.qr_core import QRCore, QRCommand
from ..controllers.base import Commands


class DeviceCommandGenerator:
    """
    Hybrid device command generator
    
    Supports both JSON-driven and traditional API approaches for device commands
    """
    
    def __init__(self):
        self._qr_core = QRCore()
        self._logger = logging.getLogger(self.__class__.__name__)
        
        # Command mapping table for easy maintenance
        # Format: (domain, action) -> builder function
        self._command_builders = self._init_command_builders()
    
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
        
        Supports multiple formats (auto-detected):
        - Single command: {"domain": "led_control", "action": "led_on", ...}
        - Batch commands: {"commands": [...]}
        - With type field: {"type": "single_command", ...} (optional)
        
        Args:
            json_data: JSON device command dict
            
        Returns:
            List of QRCommand objects
        """
        # Auto-detect format if type not specified
        if 'type' not in json_data:
            if 'commands' in json_data:
                json_data['type'] = 'device_batch'
            elif 'domain' in json_data and 'action' in json_data:
                json_data['type'] = 'single_command'
            else:
                raise ValueError("Unable to auto-detect command format. Add 'type' field or use standard structure.")
        
        # Validate JSON structure
        JSONValidator.validate_device_json(json_data)
        
        # Handle different command formats
        if json_data.get('type') == 'single_command':
            # Single command format
            self._logger.info("📱 Processing single device command")
            return self._create_single_qr_command(json_data)
        elif 'commands' in json_data:
            # Batch commands format
            commands_data = json_data['commands']
            
            # Accept both list (for batch) and dict (for legacy format)
            if not isinstance(commands_data, (list, dict)):
                raise ValueError("Commands must be a list or object")
            
            self._logger.info("📱 Processing batch device commands")
            return self._create_batch_qr_command(json_data)
        
        return []
    
    def from_simple_command(self, domain: str, action: str, parameters: Dict[str, Any] = None) -> List[QRCommand]:
        """
        Generate QR code from a single simple command (KISS approach)
        
        This is the simplest way to generate a QR code for GUI applications.
        No need to build complex JSON structures.
        
        Args:
            domain: Command domain (e.g., 'led_control', 'buzzer_control')
            action: Command action (e.g., 'led_on', 'play_melody')
            parameters: Optional parameters dict (e.g., {'led_id': 1})
            
        Returns:
            List with single QRCommand object
            
        Example:
            generator.from_simple_command('led_control', 'led_on', {'led_id': 1})
            generator.from_simple_command('buzzer_control', 'play_melody', {'melody': 'SUCCESS'})
        """
        if parameters is None:
            parameters = {}
            
        # Build minimal JSON structure
        json_data = {
            "type": "single_command",
            "domain": domain,
            "action": action,
            "parameters": parameters
        }
        
        return self.from_json(json_data)
    
    def _init_command_builders(self) -> Dict[tuple, Callable]:
        """
        Initialize command builder mapping table
        
        This makes it easy to add new commands without modifying _build_binary_command
        Just add a new entry here!
        """
        return {
            # LED Control
            ('led_control', 'led_on'): self._build_led_on,
            ('led_control', 'led_off'): self._build_led_off,
            ('led_control', 'led_blink'): self._build_led_blink,
            ('led_control', 'led_stop_blink'): self._build_led_stop_blink,
            ('led_control', 'all_leds_off'): self._build_all_leds_off,
            
            # Buzzer Control
            ('buzzer_control', 'play_melody'): self._build_play_melody,
            ('buzzer_control', 'beep'): self._build_beep,
            ('buzzer_control', 'set_volume'): self._build_set_volume,
            
            # Device Settings
            ('device_settings', 'set_orientation'): self._build_set_orientation,
            ('device_settings', 'set_language'): self._build_set_language,
            ('device_settings', 'set_auto_shutdown'): self._build_set_auto_shutdown,
            
            # Power Management
            ('power_management', 'shutdown'): self._build_shutdown,
            ('power_management', 'restart'): self._build_restart,
            ('power_management', 'deep_sleep'): self._build_deep_sleep,
            
            # Lua Management
            ('lua_management', 'clear_script'): self._build_clear_script,
            ('lua_management', 'get_script_info'): self._build_get_script_info,
        }
    
    # === Command Builders (Easy to add new ones!) ===
    
    def _build_led_on(self, params: Dict) -> bytes:
        """Build LED ON command"""
        led_id = params.get('led_id', 1)
        cmd_obj = self._qr_core._led_builder.create_led_on_command(led_id)
        return bytes([cmd_obj.command_id]) + cmd_obj.payload
    
    def _build_led_off(self, params: Dict) -> bytes:
        """Build LED OFF command"""
        led_id = params.get('led_id', 1)
        cmd_obj = self._qr_core._led_builder.create_led_off_command(led_id)
        return bytes([cmd_obj.command_id]) + cmd_obj.payload
    
    def _build_led_blink(self, params: Dict) -> bytes:
        """Build LED BLINK command"""
        led_id = params.get('led_id', 1)
        frequency = params.get('frequency', 2.0)
        payload = bytes([led_id]) + struct.pack('<f', frequency)
        return bytes([Commands.LED_START_BLINK]) + payload
    
    def _build_led_stop_blink(self, params: Dict) -> bytes:
        """Build LED STOP BLINK command"""
        led_id = params.get('led_id', 1)
        return bytes([Commands.LED_STOP_BLINK, led_id])
    
    def _build_all_leds_off(self, params: Dict) -> bytes:
        """Build ALL LEDs OFF command"""
        cmd_obj = self._qr_core._led_builder.create_all_leds_off_command()
        return bytes([cmd_obj.command_id]) + cmd_obj.payload
    
    def _build_play_melody(self, params: Dict) -> bytes:
        """Build PLAY MELODY command"""
        melody = params.get('melody', 'SUCCESS')
        cmd_obj = self._qr_core._buzzer_builder.create_buzzer_melody_command(melody)
        return bytes([cmd_obj.command_id]) + cmd_obj.payload
    
    def _build_beep(self, params: Dict) -> bytes:
        """Build BEEP command"""
        duration = params.get('duration', 200)
        frequency = params.get('frequency', 1000)
        payload = struct.pack('<HH', duration, frequency)
        return bytes([Commands.BUZZER_BEEP]) + payload
    
    def _build_set_volume(self, params: Dict) -> bytes:
        """Build SET VOLUME command"""
        volume = params.get('volume', 50)
        return bytes([Commands.BUZZER_SET_CONFIG, volume])
    
    def _build_set_orientation(self, params: Dict) -> bytes:
        """Build SET ORIENTATION command"""
        orientation = params.get('orientation', 0)
        # Use existing builder method
        cmd_obj = self._qr_core._device_builder.create_orientation_command(orientation)
        return bytes([cmd_obj.command_id]) + cmd_obj.payload
    
    def _build_set_language(self, params: Dict) -> bytes:
        """Build SET LANGUAGE command"""
        language = params.get('language_code', 0x040C)
        if isinstance(language, str):
            language = int(language, 16) if language.startswith('0x') else int(language)
        # Manual command building since no builder exists
        import struct
        payload = struct.pack('<I', language)  # 32-bit language code
        return bytes([Commands.DEVICE_SET_LANGUAGE]) + payload
    
    def _build_set_auto_shutdown(self, params: Dict) -> bytes:
        """Build SET AUTO SHUTDOWN command"""
        ble_timeout = params.get('ble_timeout', 30)
        activity_timeout = params.get('activity_timeout', 60)
        # Manual command building
        payload = struct.pack('<HH', ble_timeout, activity_timeout)
        return bytes([Commands.POWER_SET_AUTO_SHUTDOWN]) + payload
    
    def _build_shutdown(self, params: Dict) -> bytes:
        """Build SHUTDOWN command"""
        return bytes([Commands.SYSTEM_SHUTDOWN])
    
    def _build_restart(self, params: Dict) -> bytes:
        """Build RESTART command"""
        return bytes([Commands.SYSTEM_RESTART])
    
    def _build_deep_sleep(self, params: Dict) -> bytes:
        """Build DEEP SLEEP command"""
        duration = params.get('duration', 0)
        # Note: Implementation depends on ESP32 deep sleep command format
        return bytes([0x74, duration & 0xFF, (duration >> 8) & 0xFF])  # Example
    
    def _build_clear_script(self, params: Dict) -> bytes:
        """Build CLEAR SCRIPT command"""
        # Use existing builder method  
        cmd_obj = self._qr_core._device_builder.create_lua_clear_command()
        return bytes([cmd_obj.command_id]) + cmd_obj.payload
    
    def _build_get_script_info(self, params: Dict) -> bytes:
        """Build GET SCRIPT INFO command"""
        # Use existing builder method
        cmd_obj = self._qr_core._device_builder.create_lua_info_command()
        return bytes([cmd_obj.command_id]) + cmd_obj.payload

    def _build_binary_command(self, cmd_data: Dict[str, Any]) -> bytes:
        """
        Build binary command from JSON command data using mapping table
        
        Much cleaner and easier to maintain than big if/else blocks!
        """
        domain = cmd_data.get('domain', '')
        action = cmd_data.get('action', '')
        parameters = cmd_data.get('parameters', {})
        
        # Look up command builder in mapping table
        builder_key = (domain, action)
        builder = self._command_builders.get(builder_key)
        
        if builder:
            return builder(parameters)
        else:
            # Command not supported - list available commands for better debugging
            available = [f"{d}.{a}" for (d, a) in self._command_builders.keys()]
            raise ValueError(f"Unsupported command: {domain}.{action}\nAvailable commands: {', '.join(sorted(available))}")
    
    def _create_single_qr_command(self, json_data: Dict[str, Any]) -> List[QRCommand]:
        """
        Create a QR code for a single device command
        
        Args:
            json_data: Single command JSON with domain, action, parameters
            
        Returns:
            List with single QRCommand object
        """
        try:
            # Build binary command
            binary_command = self._build_binary_command(json_data)
            
            if not binary_command:
                self._logger.error("Failed to build binary command")
                return []
            
            # Format as QR command
            import base64
            encoded = base64.b64encode(binary_command).decode('utf-8')
            qr_data = f"$DCMD:{encoded}$"
            
            # Create QRCommand object
            from .utils.qr_core import QRCommand, CommandData
            cmd_data = CommandData(
                command_id=binary_command[0] if binary_command else 0,
                payload=binary_command[1:] if len(binary_command) > 1 else b'',
                domain="device",  # Device domain commands
                command_type="Device Command",
                description=f"{json_data.get('domain', '')}.{json_data.get('action', '')}",
                metadata={"format": "single"}
            )
            
            # Return QRCommand with pre-formatted data
            qr_cmd = QRCommand(cmd_data)
            qr_cmd.command_data = qr_data  # Override with our formatted data
            return [qr_cmd]
            
        except Exception as e:
            self._logger.error(f"Error creating single QR command: {e}")
            return []
    
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