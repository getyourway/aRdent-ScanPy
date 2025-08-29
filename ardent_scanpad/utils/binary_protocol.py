"""
Binary Protocol Utilities

Centralized utilities for all binary protocol operations used across the library.
Handles packing, unpacking, command building, and response parsing.
"""

import struct
from typing import List, Tuple, Optional, Union
from ..core.exceptions import ConfigurationError


class BinaryProtocol:
    """
    Centralized binary protocol utilities
    
    All binary operations for the aRdent ScanPad protocol in one place.
    Used by controllers, QR generators, and command parsers.
    """
    
    # ========================================
    # BASIC PACKING (most common operations)
    # ========================================
    
    @staticmethod
    def pack_uint8(value: int) -> bytes:
        """Pack single byte (0-255)"""
        return bytes([value & 0xFF])
    
    @staticmethod
    def pack_uint16_le(value: int) -> bytes:
        """Pack 16-bit little endian (0-65535)"""
        return struct.pack('<H', value & 0xFFFF)
    
    @staticmethod
    def pack_uint16_be(value: int) -> bytes:
        """Pack 16-bit big endian (0-65535)"""
        return struct.pack('>H', value & 0xFFFF)
    
    @staticmethod
    def pack_bytes(*values: int) -> bytes:
        """Pack multiple bytes"""
        return bytes([v & 0xFF for v in values])
    
    # ========================================
    # COMMON COMMAND PATTERNS
    # ========================================
    
    @staticmethod
    def build_command(command_id: int, payload: bytes = b'') -> bytes:
        """Build complete command: [command_id] + payload"""
        return bytes([command_id & 0xFF]) + payload
    
    @staticmethod
    def build_led_command(command_id: int, led_id: int, state: int = 1) -> bytes:
        """Build LED command: [command_id][led_id][state]"""
        return BinaryProtocol.pack_bytes(command_id, led_id, state)
    
    @staticmethod
    def build_buzzer_melody_command(command_id: int, melody_id: int) -> bytes:
        """Build buzzer melody command: [command_id][melody_id]"""
        return BinaryProtocol.pack_bytes(command_id, melody_id)
    
    @staticmethod
    def build_buzzer_beep_command(command_id: int, duration_ms: int, frequency_hz: int = 1000) -> bytes:
        """Build buzzer beep command: [command_id][duration_low][duration_high][freq_low][freq_high]"""
        duration_bytes = BinaryProtocol.pack_uint16_le(duration_ms)
        frequency_bytes = BinaryProtocol.pack_uint16_le(frequency_hz)
        return BinaryProtocol.pack_uint8(command_id) + duration_bytes + frequency_bytes
    
    @staticmethod
    def build_settings_command(command_id: int, value: Union[int, bytes]) -> bytes:
        """Build device settings command with various payload types"""
        if isinstance(value, int):
            if value <= 255:
                return BinaryProtocol.pack_bytes(command_id, value)
            else:
                return BinaryProtocol.pack_uint8(command_id) + BinaryProtocol.pack_uint16_le(value)
        else:
            return BinaryProtocol.pack_uint8(command_id) + value
    
    @staticmethod
    def build_auto_shutdown_command(command_id: int, enabled: bool, 
                                  no_conn_timeout: int = 30, no_activity_timeout: int = 60) -> bytes:
        """Build auto shutdown command: [command_id][enabled][conn_timeout_le][activity_timeout_le]"""
        payload = BinaryProtocol.pack_uint8(1 if enabled else 0)
        payload += BinaryProtocol.pack_uint16_le(no_conn_timeout)
        payload += BinaryProtocol.pack_uint16_le(no_activity_timeout)
        return BinaryProtocol.pack_uint8(command_id) + payload
    
    # ========================================
    # BATCH COMMANDS
    # ========================================
    
    @staticmethod
    def build_batch_command(commands: List[Tuple[int, bytes]]) -> bytes:
        """
        Build batch command format: [count][len1][cmd1][len2][cmd2]...
        
        Args:
            commands: List of (command_id, payload) tuples
            
        Returns:
            Binary batch data
        """
        if not commands:
            raise ValueError("No commands to batch")
        
        # Start with command count
        batch_binary = struct.pack('B', len(commands))
        
        # Add each command: [length][command_id][payload]
        for command_id, payload in commands:
            cmd_binary = bytes([command_id]) + payload
            batch_binary += struct.pack('B', len(cmd_binary)) + cmd_binary
        
        return batch_binary
    
    @staticmethod
    def parse_batch_command(batch_data: bytes) -> List[Tuple[int, bytes]]:
        """
        Parse batch command format back to individual commands
        
        Args:
            batch_data: Binary batch data
            
        Returns:
            List of (command_id, payload) tuples
        """
        if len(batch_data) < 1:
            raise ValueError("Invalid batch data")
        
        commands = []
        count = batch_data[0]
        offset = 1
        
        for i in range(count):
            if offset >= len(batch_data):
                raise ValueError("Truncated batch data")
                
            cmd_len = batch_data[offset]
            if offset + 1 + cmd_len > len(batch_data):
                raise ValueError("Invalid command length in batch")
                
            cmd_data = batch_data[offset + 1:offset + 1 + cmd_len]
            if len(cmd_data) < 1:
                raise ValueError("Empty command in batch")
                
            command_id = cmd_data[0]
            payload = cmd_data[1:]
            commands.append((command_id, payload))
            offset += 1 + cmd_len
        
        return commands
    
    # ========================================
    # RESPONSE PARSING
    # ========================================
    
    @staticmethod
    def check_status_response(response: bytes) -> bool:
        """Check if response indicates success (status byte 0x00)"""
        if not response or len(response) < 1:
            return False
        return response[0] == 0x00
    
    @staticmethod
    def parse_status_response(response: bytes) -> None:
        """Parse status response, raise exception if failed"""
        if not response or len(response) < 1:
            raise ConfigurationError("Empty response")
        if response[0] != 0x00:
            raise ConfigurationError(f"Command failed with status 0x{response[0]:02X}")
    
    @staticmethod
    def parse_uint8_response(response: bytes) -> int:
        """Parse single uint8 value from response (after status check)"""
        if len(response) < 2:
            raise ConfigurationError("Response too short for uint8")
        BinaryProtocol.parse_status_response(response)
        return response[1]
    
    @staticmethod
    def parse_uint16_le_response(response: bytes) -> int:
        """Parse single uint16 little endian from response (after status check)"""
        if len(response) < 3:
            raise ConfigurationError("Response too short for uint16")
        BinaryProtocol.parse_status_response(response)
        return struct.unpack('<H', response[1:3])[0]
    
    @staticmethod
    def parse_struct_response(response: bytes, expected_count: int) -> List[int]:
        """Parse structured response with multiple values"""
        BinaryProtocol.parse_status_response(response)
        if len(response) < 1 + expected_count:
            raise ConfigurationError(f"Response too short, expected {expected_count} bytes")
        return list(response[1:1 + expected_count])
    
    @staticmethod
    def parse_empty_response(response: bytes) -> None:
        """Parse response that should only contain status"""
        BinaryProtocol.parse_status_response(response)
        # No additional data expected
    
    # ========================================
    # KEY CONFIGURATION SPECIFIC
    # ========================================
    
    @staticmethod
    def build_key_action(action_type: int, data: bytes, delay: int = 10) -> bytes:
        """
        Build key action payload: [type][delay][length][data]
        
        Args:
            action_type: Action type (1=UTF8, 2=HID, 3=Consumer)
            data: Action data (max 8 bytes)
            delay: Delay in ms (default 10)
            
        Returns:
            Binary action data
        """
        if len(data) > 8:
            raise ValueError("Action data too long (max 8 bytes)")
        
        action_bytes = BinaryProtocol.pack_bytes(action_type, delay, len(data))
        action_bytes += data
        
        # Pad to fixed size if needed (total 11 bytes: type+delay+len+8data)
        while len(action_bytes) < 11:
            action_bytes += b'\x00'
            
        return action_bytes
    
    @staticmethod
    def build_key_config(key_id: int, actions: List[bytes]) -> bytes:
        """
        Build complete key configuration: [key_id][action_count][actions...]
        
        Args:
            key_id: Key ID (0-19)
            actions: List of action bytes (max 10)
            
        Returns:
            Binary key configuration
        """
        if len(actions) > 10:
            raise ValueError("Too many actions (max 10)")
        
        config_bytes = BinaryProtocol.pack_bytes(key_id, len(actions))
        for action in actions:
            config_bytes += action
        
        return config_bytes
    
    # ========================================
    # UTILITIES
    # ========================================
    
    @staticmethod
    def bytes_to_hex(data: bytes) -> str:
        """Convert bytes to hex string for debugging"""
        return ' '.join(f'{b:02X}' for b in data)
    
    @staticmethod
    def validate_command_id(command_id: int) -> None:
        """Validate command ID is in valid range"""
        if not (0 <= command_id <= 255):
            raise ValueError(f"Invalid command ID: {command_id} (must be 0-255)")
    
    @staticmethod
    def validate_payload_size(payload: bytes, max_size: int = 255) -> None:
        """Validate payload size"""
        if len(payload) > max_size:
            raise ValueError(f"Payload too large: {len(payload)} bytes (max {max_size})")
    
    # ========================================
    # COMMON PROTOCOL CONSTANTS
    # ========================================
    
    # Status codes
    STATUS_SUCCESS = 0x00
    STATUS_ERROR_INVALID_PARAM = 0x01
    STATUS_ERROR_INVALID_STATE = 0x02
    STATUS_ERROR_TIMEOUT = 0x03
    STATUS_ERROR_UNKNOWN = 0xFF
    
    # Action types for key configuration
    ACTION_TYPE_UTF8 = 1
    ACTION_TYPE_HID = 2 
    ACTION_TYPE_CONSUMER = 3
    
    # Maximum sizes
    MAX_PAYLOAD_SIZE = 255
    MAX_ACTION_DATA_SIZE = 8
    MAX_ACTIONS_PER_KEY = 10
    MAX_BATCH_COMMANDS = 50