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
        Parse JSON commands to list of binary commands
        
        Args:
            json_config: JSON with commands object
            
        Returns:
            List of (command_id, payload) tuples
        """
        if 'commands' not in json_config:
            raise ValueError("JSON config must contain 'commands' field")
        
        commands_data = json_config['commands']
        if not isinstance(commands_data, dict):
            raise ValueError("Commands must be an object")
        
        binary_commands = []
        
        for cmd_name, cmd_params in commands_data.items():
            if cmd_name.startswith('_'):  # Skip documentation fields
                continue
                
            try:
                command_id, payload = CommandParser._parse_single_command(cmd_name, cmd_params)
                binary_commands.append((command_id, payload))
            except Exception as e:
                logger.error(f"Error parsing command {cmd_name}: {e}")
                continue  # Don't fail entire batch for one bad command
        
        return binary_commands
    
    @staticmethod
    def _parse_single_command(cmd_name: str, cmd_params: Dict[str, Any]) -> Tuple[int, bytes]:
        """
        Parse a single command name to binary format
        
        Args:
            cmd_name: Command name (e.g., "led_1_on", "buzzer_success")
            cmd_params: Command parameters dict
            
        Returns:
            Tuple of (command_id, payload)
        """
        # LED Commands (0x10-0x1F range)
        if cmd_name.startswith('led_'):
            if cmd_name.endswith('_on'):
                led_id = int(cmd_name.split('_')[1])
                return (0x10, BinaryProtocol.pack_uint8(led_id))  # LED_ON command
                
            elif cmd_name.endswith('_off'):
                led_id = int(cmd_name.split('_')[1]) 
                return (0x11, BinaryProtocol.pack_uint8(led_id))  # LED_OFF command
                
            elif cmd_name == 'led_all_off':
                return (0x12, b'')  # ALL_LEDS_OFF command
                
            elif cmd_name.startswith('led_rgb_'):
                # RGB modes: led_rgb_red -> led_id=6, etc.
                rgb_colors = {'red': 6, 'green': 7, 'blue': 8, 'yellow': 9}
                color = cmd_name.split('_')[-1]
                if color in rgb_colors:
                    return (0x10, BinaryProtocol.pack_uint8(rgb_colors[color]))  # LED_ON with RGB ID
        
        # Buzzer Commands (0x20-0x2F range)
        elif cmd_name.startswith('buzzer_'):
            if cmd_name in ['buzzer_success', 'buzzer_error', 'buzzer_warning']:
                melody_map = {'success': 0, 'error': 1, 'warning': 2}
                melody = cmd_name.split('_')[1]
                return (0x20, BinaryProtocol.pack_uint8(melody_map[melody]))  # BUZZER_MELODY command
                
            elif cmd_name == 'buzzer_beep':
                duration = cmd_params.get('duration_ms', 200)
                frequency = cmd_params.get('frequency', 1000)
                # Use centralized beep command builder
                payload = BinaryProtocol.pack_uint16_le(duration) + BinaryProtocol.pack_uint16_le(frequency)
                return (0x21, payload)  # BUZZER_BEEP command
                
            elif cmd_name == 'buzzer_stop':
                return (0x22, b'')  # BUZZER_STOP command
        
        # Device Settings (0x30-0x3F range)
        elif cmd_name.startswith('orientation_'):
            orientation_map = {
                'orientation_portrait': 0,
                'orientation_landscape_right': 1,
                'orientation_portrait_inverted': 2,
                'orientation_landscape_left': 3
            }
            if cmd_name in orientation_map:
                orientation = orientation_map[cmd_name]
                return (0x30, BinaryProtocol.pack_uint8(orientation))  # SET_ORIENTATION command
                
        elif cmd_name.startswith('language_'):
            language_code = cmd_params.get('value', '0x0409')
            # Convert hex string to int
            if isinstance(language_code, str) and language_code.startswith('0x'):
                language_code = int(language_code, 16)
            # Use centralized packing
            payload = BinaryProtocol.pack_uint16_le(language_code)
            return (0x31, payload)  # SET_LANGUAGE command
        
        elif cmd_name.startswith('auto_shutdown_'):
            if cmd_name == 'auto_shutdown_enable':
                no_conn_timeout = cmd_params.get('no_connection_timeout_min', 30)
                no_activity_timeout = cmd_params.get('no_activity_timeout_min', 60)
                # Use centralized auto shutdown builder (without command_id since we return it separately)
                payload = BinaryProtocol.pack_uint8(1) + BinaryProtocol.pack_uint16_le(no_conn_timeout) + BinaryProtocol.pack_uint16_le(no_activity_timeout)
                return (0x32, payload)  # SET_AUTO_SHUTDOWN command
                
            elif cmd_name == 'auto_shutdown_disable':
                payload = BinaryProtocol.pack_uint8(0) + BinaryProtocol.pack_uint16_le(0) + BinaryProtocol.pack_uint16_le(0)
                return (0x32, payload)  # SET_AUTO_SHUTDOWN command
        
        # Status Commands (0x40-0x4F range) - read-only
        elif cmd_name == 'device_info':
            return (0x40, b'')  # GET_DEVICE_INFO command
            
        elif cmd_name == 'battery_level':
            return (0x41, b'')  # GET_BATTERY_LEVEL command
        
        # Lua Commands (0x50-0x5F range) 
        elif cmd_name.startswith('lua_'):
            if cmd_name == 'lua_clear':
                return (0x50, b'')  # LUA_CLEAR command
                
            elif cmd_name == 'lua_info':
                return (0x51, b'')  # LUA_INFO command
                
            elif cmd_name == 'lua_deploy':
                script_data = cmd_params.get('script', '')
                if isinstance(script_data, str):
                    script_data = script_data.encode('utf-8')
                return (0x52, script_data)  # LUA_DEPLOY command
        
        # If we reach here, command is not supported
        raise ValueError(f"Unsupported command: {cmd_name}")
    
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