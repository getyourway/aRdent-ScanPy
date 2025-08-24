"""
Base Controller for aRdent ScanPad

Provides unified parameter validation, command sending, and response parsing
for all device controllers.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Union, List

from ..core.exceptions import InvalidParameterError, ConfigurationError, TimeoutError
from ..utils.constants import MAX_ACTIONS_PER_KEY


class BaseController:
    """
    Base controller providing common functionality for all device controllers.
    
    Features:
    - Parameter validation
    - Command sending and response handling
    - Response parsing
    """
    
    def __init__(self, connection, char_name: str, timeout: float = 5.0):
        """
        Args:
            connection: BLEConnection instance
            char_name: BLE characteristic name ('device_commands' or 'config_commands')
            timeout: Response timeout in seconds
        """
        self.connection = connection
        self._char_name = char_name
        self._timeout = timeout
        self._logger = logging.getLogger(self.__class__.__name__)
    
    # ========================================
    # PARAMETER VALIDATION
    # ========================================
    
    def _validate_range(self, name: str, value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> None:
        """Validate value is in range"""
        if not (min_val <= value <= max_val):
            raise InvalidParameterError(name, value, f"Must be {min_val}-{max_val}")
    
    def _validate_choices(self, name: str, value: Any, choices: List[Any]) -> None:
        """Validate value is in allowed choices"""
        if value not in choices:
            raise InvalidParameterError(name, value, f"Must be one of: {choices}")
    
    def _validate_type(self, name: str, value: Any, expected_type: type) -> None:
        """Validate value type"""
        if not isinstance(value, expected_type):
            raise InvalidParameterError(name, value, f"Must be {expected_type.__name__}")
    
    # ========================================
    # DOMAIN-SPECIFIC VALIDATION
    # ========================================
    
    def _validate_key_id(self, key_id: int) -> None:
        """Validate key ID"""
        self._validate_range('key_id', key_id, 0, 19)
    
    def _validate_led_id(self, led_id: int) -> None:
        """Validate LED ID"""
        self._validate_range('led_id', led_id, 1, 9)
    
    def _validate_actions_count(self, actions: List[Any]) -> None:
        """Validate actions count"""
        if len(actions) > MAX_ACTIONS_PER_KEY:
            raise InvalidParameterError('actions', len(actions), f'Maximum {MAX_ACTIONS_PER_KEY} actions allowed')
    
    # ========================================
    # COMMAND SENDING
    # ========================================
    
    async def _send_command(self, command_id: int, payload: bytes = b'') -> bool:
        """Send command and wait for device response, returns success status"""
        try:
            response = await self._send_command_and_wait(command_id, payload)
            # Check device status byte (0x00 = success)
            return response[0] == 0x00
        except (ConfigurationError, TimeoutError) as e:
            self._logger.error(f"Command 0x{command_id:02X} failed: {e}")
            return False
        except Exception as e:
            self._logger.error(f"Unexpected error for command 0x{command_id:02X}: {e}")
            return False
    
    async def _send_command_and_wait(self, command_id: int, payload: bytes = b'') -> bytes:
        """Send command and wait for response"""
        try:
            # Clear previous responses based on domain (polling pattern from existing code)
            if self._char_name == 'config_commands':
                # Config domain (Keys/Buttons) → _received_config_responses
                if hasattr(self.connection, '_received_config_responses'):
                    self.connection._received_config_responses = []
                response_queue_attr = '_received_config_responses'
            else:
                # Device domain (LED/Buzzer/Settings/OTA) → _received_device_responses  
                if hasattr(self.connection, '_received_device_responses'):
                    self.connection._received_device_responses = []
                response_queue_attr = '_received_device_responses'
            
            # Send command via connection (NOT recursive call)
            command_data = bytes([command_id]) + payload
            success = await self.connection.write_char(self._char_name, command_data)
            if not success:
                raise ConfigurationError(f"Failed to send command 0x{command_id:02X}")
            
            # Wait for response using correct queue
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < self._timeout:
                if hasattr(self.connection, response_queue_attr):
                    response_queue = getattr(self.connection, response_queue_attr)
                    if response_queue:
                        response = response_queue[-1]
                        if len(response) >= 2 and response[1] == command_id:
                            self._logger.debug(f"📥 Received response for 0x{command_id:02X}")
                            return response
                await asyncio.sleep(0.01)  # 10ms polling like existing code
            
            raise TimeoutError(f"Command 0x{command_id:02X} timed out after {self._timeout}s")
            
        except Exception as e:
            if not isinstance(e, TimeoutError):
                self._logger.error(f"Failed to execute command 0x{command_id:02X}: {e}")
                raise ConfigurationError(f"Failed to execute command: {e}")
            raise
    
    # ========================================
    # RESPONSE PARSING
    # ========================================
    
    def _parse_uint8_response(self, response: bytes) -> int:
        """Parse UINT8 response"""
        if not response or len(response) < 5:
            raise ConfigurationError("Invalid response length")
        if response[0] != 0:
            raise ConfigurationError(f"Command failed with status 0x{response[0]:02X}")
        if response[2] != 0x01:  # UINT8 type
            raise ConfigurationError("Expected UINT8 response")
        return response[4]
    
    def _parse_struct_response(self, response: bytes, expected_count: int) -> List[int]:
        """Parse STRUCT response"""
        if not response or len(response) < 4:
            raise ConfigurationError("Invalid response length")
        if response[0] != 0:
            raise ConfigurationError(f"Command failed with status 0x{response[0]:02X}")
        if response[3] != expected_count:
            raise ConfigurationError(f"Expected {expected_count} elements, got {response[3]}")
        return list(response[4:])
    
    def _parse_empty_response(self, response: bytes) -> None:
        """Parse EMPTY response"""
        if not response or len(response) < 4:
            raise ConfigurationError("Invalid response length")
        if response[0] != 0:
            raise ConfigurationError(f"Command failed with status 0x{response[0]:02X}")


# COMPLETE Command IDs - Device command definitions
class Commands:
    """
    Centralized command IDs
    Source: main/commands/command_types.h
    """
    
    # =============================================================================
    # CONFIG MANAGER COMMANDS (Config domain - 'config_commands' characteristic)
    # =============================================================================
    
    # Key Configuration Commands (0x10-0x1F)
    SET_KEY_CONFIG = 0x10        # CMD_CONFIG_SET_KEY
    GET_KEY_CONFIG = 0x11        # CMD_CONFIG_GET_KEY  
    CLEAR_KEY_CONFIG = 0x12      # CMD_CONFIG_CLEAR_KEY
    SET_KEY_ENABLED = 0x13       # CMD_CONFIG_SET_ENABLED
    
    # Global Configuration Commands (0x20-0x2F)
    GET_ALL_CONFIGS = 0x20       # CMD_CONFIG_GET_ALL
    SAVE_CONFIG = 0x21           # CMD_CONFIG_SAVE_ALL
    FACTORY_RESET = 0x22         # CMD_CONFIG_FACTORY_RESET
    
    # Bulk Configuration Commands (0x30-0x3F)
    SET_MULTIPLE = 0x30          # CMD_CONFIG_SET_MULTIPLE
    
    # =============================================================================
    # DEVICE CONTROLLER COMMANDS (Device domain - 'device_commands' characteristic)
    # =============================================================================
    
    # LED Control Commands (0x10-0x1F)
    LED_SET_STATE = 0x10         # CMD_LED_SET_STATE
    LED_GET_STATE = 0x11         # CMD_LED_GET_STATE
    LED_START_BLINK = 0x12       # CMD_LED_START_BLINK
    LED_STOP_BLINK = 0x13        # CMD_LED_STOP_BLINK
    LED_ALL_OFF = 0x14           # CMD_LED_ALL_OFF
    LED_SET_PATTERN = 0x15       # CMD_LED_SET_PATTERN
    LED_GET_CONFIG = 0x16        # CMD_LED_GET_CONFIG
    
    # Buzzer Control Commands (0x20-0x2F)
    BUZZER_BEEP = 0x20           # CMD_BUZZER_BEEP
    BUZZER_MELODY = 0x21         # CMD_BUZZER_MELODY
    BUZZER_SET_CONFIG = 0x22     # CMD_BUZZER_SET_CONFIG
    BUZZER_GET_CONFIG = 0x23     # CMD_BUZZER_GET_CONFIG
    BUZZER_STOP = 0x24           # CMD_BUZZER_STOP
    BUZZER_TEST = 0x25           # CMD_BUZZER_TEST
    
    # Device Settings Commands (0x40-0x4F)
    DEVICE_SET_ORIENTATION = 0x40  # CMD_DEVICE_SET_ORIENTATION
    DEVICE_GET_ORIENTATION = 0x41  # CMD_DEVICE_GET_ORIENTATION
    DEVICE_SET_LANGUAGE = 0x42     # CMD_DEVICE_SET_LANGUAGE
    DEVICE_GET_LANGUAGE = 0x43     # CMD_DEVICE_GET_LANGUAGE
    DEVICE_SET_NAME = 0x44         # CMD_DEVICE_SET_NAME
    DEVICE_GET_NAME = 0x45         # CMD_DEVICE_GET_NAME
    
    # Power Management Commands (0x50-0x5F)
    POWER_SET_AUTO_SHUTDOWN = 0x50    # CMD_POWER_SET_AUTO_SHUTDOWN
    POWER_GET_AUTO_SHUTDOWN = 0x51    # CMD_POWER_GET_AUTO_SHUTDOWN
    POWER_SET_ACTIVITY_TIMEOUT = 0x52 # CMD_POWER_SET_ACTIVITY_TIMEOUT
    POWER_GET_ACTIVITY_TIMEOUT = 0x53 # CMD_POWER_GET_ACTIVITY_TIMEOUT
    POWER_RESET_ACTIVITY_TIMER = 0x54 # CMD_POWER_RESET_ACTIVITY_TIMER
    POWER_GET_STATUS = 0x55           # CMD_POWER_GET_STATUS
    
    # OTA Management Commands (0x60-0x6F) - CORRECTED IDs
    OTA_CHECK_VERSION = 0x60      # CMD_OTA_CHECK_VERSION (was wrongly 0x40!)
    OTA_START = 0x61              # CMD_OTA_START (was wrongly 0x41!)
    OTA_GET_STATUS = 0x62         # CMD_OTA_GET_STATUS
    OTA_STATUS = 0x62             # Alias for OTA_GET_STATUS
    OTA_CANCEL = 0x63             # CMD_OTA_CANCEL
    OTA_GET_PROGRESS = 0x64       # CMD_OTA_GET_PROGRESS
    
    # Lua Script Commands (0x68-0x6F)
    LUA_DEPLOY_SCRIPT = 0x68      # CMD_LUA_DEPLOY_SCRIPT
    LUA_GET_SCRIPT_INFO = 0x69    # CMD_LUA_GET_SCRIPT_INFO
    LUA_CLEAR_SCRIPT = 0x6A       # CMD_LUA_CLEAR_SCRIPT
    
    # System Commands (0x70-0x7F)
    SYSTEM_RESTART = 0x70         # CMD_SYSTEM_RESTART
    SYSTEM_SHUTDOWN = 0x71        # CMD_SYSTEM_SHUTDOWN
    SYSTEM_GET_INFO = 0x72        # CMD_SYSTEM_GET_INFO
    SYSTEM_GET_UPTIME = 0x73      # CMD_SYSTEM_GET_UPTIME