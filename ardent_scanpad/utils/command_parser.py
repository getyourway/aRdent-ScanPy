"""
Command Parser Utility

Pure utility for parsing JSON device commands to binary format.
Used by both QR generators and Bluetooth controllers.
No dependencies on specific transport layers.
"""

import logging
from typing import Dict, Any, List, Tuple
from .binary_protocol import BinaryProtocol

logger = logging.getLogger(__name__)


class CommandParser:
    """
    Parse JSON device commands to binary format
    
    Pure utility class with no transport-specific dependencies.
    Converts JSON command names to (command_id, payload) tuples.
    """
    
    @staticmethod
    def parse_json_commands(json_config: Dict[str, Any]) -> List[Tuple[int, bytes]]:
        """
        Parse JSON commands to list of binary commands (KISS format only)
        
        Supports:
        1. Single command: {"domain": "led_control", "action": "led_on", "parameters": {...}}
        2. Batch commands: {"commands": [{"domain": "led_control", "action": "led_on", ...}]}
        
        Args:
            json_config: JSON with KISS format commands
            
        Returns:
            List of (command_id, payload) tuples
        """
        # Single KISS command format
        if 'domain' in json_config and 'action' in json_config:
            command_id, payload = CommandParser._parse_kiss_command(json_config)
            return [(command_id, payload)]
        
        # Batch KISS commands format
        elif 'commands' in json_config:
            commands_data = json_config['commands']
            if not isinstance(commands_data, list):
                raise ValueError("Commands must be a list of command objects")
            
            binary_commands = []
            for cmd_data in commands_data:
                if not isinstance(cmd_data, dict):
                    continue
                    
                try:
                    command_id, payload = CommandParser._parse_kiss_command(cmd_data)
                    binary_commands.append((command_id, payload))
                except Exception as e:
                    domain = cmd_data.get('domain', 'unknown')
                    action = cmd_data.get('action', 'unknown')
                    logger.error(f"Error parsing command {domain}.{action}: {e}")
                    continue
            
            return binary_commands
        
        else:
            raise ValueError("JSON must contain 'domain'+'action' or 'commands' field")
    
    @staticmethod
    def _parse_kiss_command(cmd_data: Dict[str, Any]) -> Tuple[int, bytes]:
        """
        Parse a KISS command to binary format
        
        Args:
            cmd_data: KISS command dict with domain, action, parameters
            
        Returns:
            Tuple of (command_id, payload)
        """
        domain = cmd_data.get('domain', '')
        action = cmd_data.get('action', '')
        parameters = cmd_data.get('parameters', {})
        
        # LED Control domain
        if domain == 'led_control':
            if action == 'led_on':
                led_id = parameters.get('led_id', 1)
                return (0x10, BinaryProtocol.pack_uint8(led_id))
                
            elif action == 'led_off':
                led_id = parameters.get('led_id', 1)
                return (0x11, BinaryProtocol.pack_uint8(led_id))
                
            elif action == 'all_leds_off':
                return (0x12, b'')
                
            elif action == 'led_blink':
                led_id = parameters.get('led_id', 1)
                frequency = parameters.get('frequency', 2)
                payload = BinaryProtocol.pack_uint8(led_id) + BinaryProtocol.pack_uint16_le(int(frequency))
                return (0x13, payload)
                
            elif action == 'led_stop_blink':
                led_id = parameters.get('led_id', 1)
                return (0x14, BinaryProtocol.pack_uint8(led_id))
        
        # Buzzer Control domain
        elif domain == 'buzzer_control':
            if action == 'play_melody':
                melody = parameters.get('melody', 'SUCCESS').upper()
                melody_map = {'SUCCESS': 0, 'ERROR': 1, 'WARNING': 2, 'KEY': 3, 'START': 4, 'STOP': 5}
                melody_id = melody_map.get(melody, 0)
                return (0x20, BinaryProtocol.pack_uint8(melody_id))
                
            elif action == 'beep':
                duration = parameters.get('duration', 200)
                frequency = parameters.get('frequency', 1000)
                payload = BinaryProtocol.pack_uint16_le(duration) + BinaryProtocol.pack_uint16_le(frequency)
                return (0x21, payload)
                
            elif action == 'set_volume':
                volume = parameters.get('volume', 50)
                enabled = parameters.get('enabled', True)
                payload = BinaryProtocol.pack_uint8(1 if enabled else 0) + BinaryProtocol.pack_uint8(volume)
                return (0x22, payload)
        
        # Device Settings domain
        elif domain == 'device_settings':
            if action == 'set_orientation':
                orientation = parameters.get('orientation', 0)
                return (0x30, BinaryProtocol.pack_uint8(orientation))
                
            elif action == 'set_language':
                language_code = parameters.get('language_code', 0x0409)
                if isinstance(language_code, str) and language_code.startswith('0x'):
                    language_code = int(language_code, 16)
                return (0x31, BinaryProtocol.pack_uint16_le(language_code))
                
            elif action == 'set_auto_shutdown':
                enabled = parameters.get('enabled', True)
                no_conn_timeout = parameters.get('ble_timeout', 30)
                no_activity_timeout = parameters.get('activity_timeout', 60)
                payload = (BinaryProtocol.pack_uint8(1 if enabled else 0) + 
                          BinaryProtocol.pack_uint16_le(no_conn_timeout) + 
                          BinaryProtocol.pack_uint16_le(no_activity_timeout))
                return (0x32, payload)
        
        # Power Management domain  
        elif domain == 'power_management':
            if action == 'shutdown':
                return (0x70, b'')
            elif action == 'restart':
                return (0x71, b'')
        
        # Lua Management domain
        elif domain == 'lua_management':
            if action == 'clear_script':
                return (0x50, b'')
            elif action == 'get_script_info':
                return (0x51, b'')
            elif action == 'deploy_script':
                script_data = parameters.get('script', '')
                if isinstance(script_data, str):
                    script_data = script_data.encode('utf-8')
                return (0x52, script_data)
        
        # If we reach here, command is not supported
        raise ValueError(f"Unsupported command: {domain}.{action}")
    
    @staticmethod
    def create_batch_binary(commands: List[Tuple[int, bytes]]) -> bytes:
        """
        Create batch binary format from list of commands
        
        Format: [count][len1][cmd_id1][payload1][len2][cmd_id2][payload2]...
        
        Args:
            commands: List of (command_id, payload) tuples
            
        Returns:
            Binary batch data
        """
        # Use centralized batch builder
        return BinaryProtocol.build_batch_command(commands)