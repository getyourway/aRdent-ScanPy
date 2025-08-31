"""
Command Parser Utility

Pure utility for parsing JSON device commands to binary format.
Used by both QR generators and Bluetooth controllers.
No dependencies on specific transport layers.
"""

import logging
from typing import Dict, Any, List, Tuple
from .binary_protocol import BinaryProtocol
from .constants import BuzzerMelodies, DeviceOrientations, LEDs, KeyboardLayouts

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
                # Validate LED ID using constants
                if led_id not in LEDs.ALL:
                    raise ValueError(f"Invalid LED ID {led_id}. Must be one of {LEDs.ALL}")
                # LED_SET_STATE with state=1 (on)
                payload = BinaryProtocol.pack_uint8(led_id) + BinaryProtocol.pack_uint8(1)
                return (0x10, payload)
                
            elif action == 'led_off':
                led_id = parameters.get('led_id', 1)
                # Validate LED ID using constants
                if led_id not in LEDs.ALL:
                    raise ValueError(f"Invalid LED ID {led_id}. Must be one of {LEDs.ALL}")
                # LED_SET_STATE with state=0 (off)
                payload = BinaryProtocol.pack_uint8(led_id) + BinaryProtocol.pack_uint8(0)
                return (0x10, payload)
                
            elif action == 'all_leds_off':
                return (0x14, b'')  # LED_ALL_OFF
                
            elif action == 'led_blink':
                led_id = parameters.get('led_id', 1)
                # Validate LED ID using constants
                if led_id not in LEDs.ALL:
                    raise ValueError(f"Invalid LED ID {led_id}. Must be one of {LEDs.ALL}")
                frequency = parameters.get('frequency', 2)
                payload = BinaryProtocol.pack_uint8(led_id) + BinaryProtocol.pack_uint16_le(int(frequency))
                return (0x12, payload)  # LED_START_BLINK
                
            elif action == 'led_stop_blink':
                led_id = parameters.get('led_id', 1)
                # Validate LED ID using constants
                if led_id not in LEDs.ALL:
                    raise ValueError(f"Invalid LED ID {led_id}. Must be one of {LEDs.ALL}")
                return (0x13, BinaryProtocol.pack_uint8(led_id))  # LED_STOP_BLINK
        
        # Buzzer Control domain
        elif domain == 'buzzer_control':
            if action == 'play_melody':
                melody = parameters.get('melody', 'SUCCESS').upper()
                # Use BuzzerMelodies constants directly from library
                melody_id = getattr(BuzzerMelodies, melody, BuzzerMelodies.SUCCESS)
                return (0x21, BinaryProtocol.pack_uint8(melody_id))  # BUZZER_MELODY
                
            elif action == 'beep':
                duration = parameters.get('duration', 200)
                frequency = parameters.get('frequency', 1000)
                payload = BinaryProtocol.pack_uint16_le(duration) + BinaryProtocol.pack_uint16_le(frequency)
                return (0x20, payload)  # BUZZER_BEEP
                
            elif action == 'set_volume':
                volume = parameters.get('volume', 50)
                enabled = parameters.get('enabled', True)
                payload = BinaryProtocol.pack_uint8(1 if enabled else 0) + BinaryProtocol.pack_uint8(volume)
                return (0x22, payload)  # BUZZER_SET_CONFIG
        
        # Device Settings domain
        elif domain == 'device_settings':
            if action == 'set_orientation':
                orientation_param = parameters.get('orientation', 0)
                
                # Support both numeric values and orientation names
                if isinstance(orientation_param, str):
                    # String name like "PORTRAIT", "LANDSCAPE" 
                    orientation_name = orientation_param.upper()
                    orientation = getattr(DeviceOrientations, orientation_name, DeviceOrientations.PORTRAIT)
                else:
                    # Numeric value (0, 1, 2, 3) - validate against constants
                    orientation = int(orientation_param)
                    valid_values = [DeviceOrientations.PORTRAIT, DeviceOrientations.LANDSCAPE, 
                                   DeviceOrientations.REVERSE_PORTRAIT, DeviceOrientations.REVERSE_LANDSCAPE]
                    if orientation not in valid_values:
                        orientation = DeviceOrientations.PORTRAIT  # Default fallback
                
                return (0x40, BinaryProtocol.pack_uint8(orientation))  # DEVICE_SET_ORIENTATION
                
            elif action == 'set_language':
                language_param = parameters.get('language_code', 'WIN_US_QWERTY')
                
                # Support multiple input formats
                if isinstance(language_param, str):
                    if language_param.startswith('0x'):
                        # Hex string like "0x1110"
                        language_code = int(language_param, 16)
                    elif hasattr(KeyboardLayouts, language_param.upper()):
                        # Layout name like "WIN_US_QWERTY", "MAC_FR_AZERTY"
                        language_code = getattr(KeyboardLayouts, language_param.upper())
                    else:
                        # Default to US QWERTY if unknown
                        language_code = KeyboardLayouts.WIN_US_QWERTY
                else:
                    # Numeric value (int)
                    language_code = int(language_param)
                
                return (0x42, BinaryProtocol.pack_uint16_le(language_code))  # DEVICE_SET_LANGUAGE
                
            elif action == 'set_auto_shutdown':
                enabled = parameters.get('enabled', True)
                no_conn_timeout = parameters.get('ble_timeout', 30)
                no_activity_timeout = parameters.get('activity_timeout', 60)
                payload = (BinaryProtocol.pack_uint8(1 if enabled else 0) + 
                          BinaryProtocol.pack_uint16_le(no_conn_timeout) + 
                          BinaryProtocol.pack_uint16_le(no_activity_timeout))
                return (0x50, payload)  # POWER_SET_AUTO_SHUTDOWN
        
        # Power Management domain  
        elif domain == 'power_management':
            if action == 'shutdown':
                return (0x70, b'')  # SYSTEM_SHUTDOWN
            elif action == 'restart':
                return (0x71, b'')  # SYSTEM_RESTART
        
        # Lua Management domain
        elif domain == 'lua_management':
            if action == 'clear_script':
                return (0x6A, b'')  # LUA_CLEAR_SCRIPT
            elif action == 'get_script_info':
                return (0x69, b'')  # LUA_GET_SCRIPT_INFO
            elif action == 'deploy_script':
                script_data = parameters.get('script', '')
                if isinstance(script_data, str):
                    script_data = script_data.encode('utf-8')
                return (0x68, script_data)  # LUA_DEPLOY_SCRIPT
        
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