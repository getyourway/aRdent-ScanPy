"""
Key Configuration Controller for aRdent ScanPad

Provides high-level API for configuring matrix keys and button actions
with support for UTF-8 text, HID keys, consumer controls, and sequences.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Union

from .base import BaseController, Commands
from ..core.exceptions import (
    ConfigurationError, InvalidParameterError, TimeoutError
)
from ..utils.constants import (
    KeyIDs, KeyTypes, HIDKeyCodes, HIDModifiers, ConsumerCodes,
    MAX_ACTIONS_PER_KEY
)

logger = logging.getLogger(__name__)


class KeyConfigurationController(BaseController):
    """
    Professional key configuration controller
    
    Supports:
    - Matrix keys (0-15) and button actions (16-19)
    - Multiple action types: UTF-8, HID, Consumer controls
    - Action sequences with timing
    - Batch operations
    - Configuration persistence
    """
    
    def __init__(self, connection):
        """
        Initialize key controller
        
        Args:
            connection: BLEConnection instance
        """
        super().__init__(connection, 'config_commands', timeout=5.0)
    
    # SIMPLIFIED API - Close to ESP32 commands
    
    async def set_key_config(self, key_id: int, actions: List[Dict[str, Any]]) -> bool:
        """
        Set key configuration with multiple actions
        
        Args:
            key_id: Key ID (0-19)
            actions: List of action dictionaries
            
        Raises:
            InvalidParameterError: If parameters are invalid
            ConfigurationError: If configuration fails
            TimeoutError: If operation times out
        """
        self._validate_key_id(key_id)  # Raises exception if invalid
        self._validate_actions_count(actions)  # Raises exception if too many
        
        try:
            # Build command payload
            payload = self._build_set_key_payload(key_id, actions)
            
            # Send command and wait for response
            success = await self._send_command(Commands.SET_KEY_CONFIG, payload)
            
            if not success:
                logger.error(f"Failed to configure key {key_id}")
                return False
            
            key_name = KeyIDs.NAMES.get(key_id, f"Key {key_id}")
            logger.debug(f"📝 Configured {key_name} with {len(actions)} actions")
            return True
        except Exception as e:
            logger.error(f"Exception configuring key {key_id}: {e}")
            return False
    
    async def get_key_config(self, key_id: int) -> Dict[str, Any]:
        """
        Get key configuration
        
        Args:
            key_id: Key ID (0-19)
            
        Returns:
            Configuration dictionary
            
        Raises:
            InvalidParameterError: If key_id is invalid
            ConfigurationError: If key is not configured or operation fails
            TimeoutError: If operation times out
        """
        self._validate_key_id(key_id)  # Raises exception if invalid
        
        payload = bytes([key_id])
        response = await self._send_command_and_wait(
            Commands.GET_KEY_CONFIG, payload
        )
        
        if not response or response[0] != 0:  # Check ESP32 status
            raise ConfigurationError(f"Failed to get configuration for key {key_id}")
            
        return self._parse_key_config_response(response)
    
    async def clear_key(self, key_id: int) -> bool:
        """
        Clear key configuration
        
        Args:
            key_id: Key ID (0-19)
            
        Returns:
            True if successful, False if failed
        """
        self._validate_key_id(key_id)  # Raises exception if invalid
        
        payload = bytes([key_id])
        success = await self._send_command(Commands.CLEAR_KEY_CONFIG, payload)
        
        if not success:
            raise ConfigurationError(f"Failed to clear key {key_id}")
            
        key_name = KeyIDs.NAMES.get(key_id, f"Key {key_id}")
        logger.info(f"🗑️ Cleared {key_name}")
        return True
    
    async def set_key_enabled(self, key_id: int, enabled: bool) -> bool:
        """
        Enable or disable a key
        
        Args:
            key_id: Key ID (0-19)
            enabled: True to enable, False to disable
            
        Returns:
            True if successful, False if failed
        """
        self._validate_key_id(key_id)  # Raises exception if invalid
        
        payload = bytes([key_id, 1 if enabled else 0])
        success = await self._send_command(Commands.SET_KEY_ENABLED, payload)
        
        if not success:
            raise ConfigurationError(f"Failed to {'enable' if enabled else 'disable'} key {key_id}")
            
        state = "enabled" if enabled else "disabled"
        key_name = KeyIDs.NAMES.get(key_id, f"Key {key_id}")
        logger.info(f"Key configuration: {key_name} {state}")
        return True
    
    async def get_all_configs(self) -> Dict[int, Dict[str, Any]]:
        """
        Get all key configurations
        
        Returns:
            Dictionary mapping key_id to configuration
        """
        configs = {}
        
        # Get individual configs (more reliable than bulk)
        for key_id in KeyIDs.ALL_KEYS:
            config = await self.get_key_config(key_id)
            if config and config.get('action_count', 0) > 0:
                configs[key_id] = config
                
        return configs
    
    async def save_config(self) -> bool:
        """
        Save configuration to device storage
        
        Returns:
            True if successful, False if failed
        """
        try:
            success = await self._send_command(Commands.SAVE_CONFIG, bytes())
            
            if not success:
                logger.error("Failed to save configuration to storage")
                return False
                
            logger.info("💾 Configuration saved to device storage")
            return True
        except Exception as e:
            logger.error(f"Exception saving configuration: {e}")
            return False
    
    async def factory_reset(self) -> bool:
        """
        Reset all keys to factory defaults
        
        Returns:
            True if successful, False if failed
        """
        try:
            success = await self._send_command(Commands.FACTORY_RESET, bytes())
            
            if not success:
                logger.error("Factory reset failed")
                return False
                
            logger.info("🏭 Factory reset completed")
            return True
        except Exception as e:
            logger.error(f"Exception during factory reset: {e}")
            return False
    
    # ACTION CREATION HELPERS
    
    def _create_single_char_action(self, char: str, delay: int = 0) -> Dict[str, Any]:
        """
        Internal method to create UTF-8 action for single character (no error logging)
        
        Args:
            char: Single character to type
            delay: Delay after character (ms)
            
        Returns:
            Action dictionary
        """
        # Ensure it's a single character
        if len(char) > 1:
            char = char[0]
        elif len(char) == 0:
            char = 'X'
            
        return {
            'type': KeyTypes.UTF8,
            'text': char,
            'delay': delay
        }
    
    def create_text_action(self, text: str, delay: int = 0) -> Dict[str, Any]:
        """
        Create UTF-8 text action (simplified - handles both single chars and text)
        
        Args:
            text: Text to type (single character or multi-character string)
            delay: Delay after text (ms)
            
        Returns:
            Action dictionary
        """
        if len(text) == 1:
            # Single character - use as-is
            return self._create_single_char_action(text, delay)
        else:
            # Multi-character text - store as UTF-8 text
            return {
                'type': KeyTypes.UTF8,
                'text': text,
                'delay': delay
            }
    
    
    def create_hid_action(self, key_code: int, modifiers: int = 0, 
                         delay: int = 0) -> Dict[str, Any]:
        """
        Create HID key action
        
        Args:
            key_code: HID key code
            modifiers: Modifier keys
            delay: Delay after keypress (ms)
            
        Returns:
            Action dictionary
        """
        return {
            'type': KeyTypes.HID,
            'value': key_code,
            'mask': modifiers,
            'delay': delay
        }
    
    def create_consumer_action(self, consumer_code: int, delay: int = 0) -> Dict[str, Any]:
        """
        Create consumer control action
        
        Args:
            consumer_code: Consumer control code
            delay: Delay after action (ms)
            
        Returns:
            Action dictionary
        """
        return {
            'type': KeyTypes.CONSUMER,
            'value': consumer_code & 0xFF,
            'mask': (consumer_code >> 8) & 0xFF,
            'delay': delay
        }
    
    # BACKWARD COMPATIBILITY (minimal set)
    
    async def clear_key_config(self, key_id: int) -> bool:
        """Alias for clear_key"""
        return await self.clear_key(key_id)
    
    
    # INTERNAL METHODS
    
    
    def _build_set_key_payload(self, key_id: int, actions: List[Dict[str, Any]]) -> bytes:
        """Build payload for SET_KEY_CONFIG command"""
        payload = [key_id, len(actions)]
        logger.debug(f"Building payload for key {key_id} with {len(actions)} actions")
        
        for i, action in enumerate(actions):
            action_type = action.get('type', KeyTypes.UTF8)
            value = action.get('value', 0)
            mask = action.get('mask', 0)
            delay = action.get('delay', 0)
            
            # Basic action data (little-endian)
            payload.extend([
                i,  # action index
                action_type,
                value & 0xFF,
                mask,
                delay & 0xFF,        # delay low byte
                (delay >> 8) & 0xFF  # delay high byte
            ])
            
            # UTF-8 data handling according to ESP32 firmware specification
            # Maximum 8 bytes UTF-8 payload per action (updated implementation)
            if action_type == KeyTypes.UTF8 and 'text' in action:
                text = action['text']
                if text:
                    text_bytes = text.encode('utf-8')
                    if len(text_bytes) <= 8:
                        # UTF-8 fits within 8-byte limit - send complete text
                        payload.extend([len(text_bytes)] + list(text_bytes))
                    else:
                        # UTF-8 exceeds 8-byte limit - truncate and warn
                        truncated_bytes = text_bytes[:8]
                        payload.extend([len(truncated_bytes)] + list(truncated_bytes))
                        logger.debug(f"UTF-8 text '{text}' truncated from {len(text_bytes)} to 8 bytes")
                else:
                    # Empty text
                    payload.extend([0])  # No UTF-8 data
        
        final_payload = bytes(payload)
        logger.debug(f"Final payload: {len(final_payload)} bytes = {final_payload.hex()}")
        return final_payload
    
    def _build_set_multiple_payload(self, configs: Dict[int, List[Dict[str, Any]]]) -> bytes:
        """Build payload for SET_MULTIPLE command"""
        payload = [len(configs)]  # Key count
        
        for key_id, actions in configs.items():
            payload.extend([key_id, len(actions)])  # Key ID and action count
            
            # Add all actions for this key
            for i, action in enumerate(actions):
                action_type = action.get('type', KeyTypes.UTF8)
                value = action.get('value', 0)
                mask = action.get('mask', 0)
                delay = action.get('delay', 0)
                
                # Basic action data (little-endian, consistent with single key format)
                payload.extend([
                    i,  # action index
                    action_type,
                    value & 0xFF,
                    mask,
                    delay & 0xFF,        # delay low byte
                    (delay >> 8) & 0xFF  # delay high byte
                ])
                
                # UTF-8 text strings longer than 8 bytes are not supported in batch mode (ESP32 limitation)
                # The ESP32 handler only processes basic action data for performance reasons
                if action_type == KeyTypes.UTF8 and 'text' in action:
                    logger.warning(f"UTF-8 text '{action['text']}' ignored in batch mode for key {key_id}")
        
        return bytes(payload)
    
    def _parse_key_config_response(self, response: bytes) -> Dict[str, Any]:
        """Parse GET_KEY_CONFIG response"""
        if len(response) < 5:
            return None
            
        logger.debug(f"📥 Parsing key config response: {response.hex()} (length: {len(response)})")
        
        # Parse header: [ble_status, ble_cmd_id, key_id, enabled, action_count]
        key_id = response[2]
        enabled = response[3] == 1
        action_count = response[4]
        
        logger.debug(f"Header: key_id={key_id}, enabled={enabled}, action_count={action_count}")
        logger.debug(f"Raw response bytes: {' '.join(f'{b:02x}' for b in response)}")
        
        actions = []
        offset = 5
        
        for i in range(action_count):
            # Need at least 6 bytes for basic action data
            if offset + 6 > len(response):
                logger.warning(f"Not enough data for action {i}: need {offset + 6} bytes, have {len(response)}")
                break
                
            # Parse action (little-endian)
            action_index = response[offset]
            action_type = response[offset + 1]
            value = response[offset + 2]
            mask = response[offset + 3]
            delay = response[offset + 4] | (response[offset + 5] << 8)
            
            logger.debug(f"Action {i} at offset {offset}: index={action_index}, type={action_type}, value={value}, mask={mask}, delay={delay}")
            offset += 6
            
            action = {
                'index': action_index,
                'type': action_type,
                'value': value,
                'mask': mask,
                'delay': delay
            }
            
            # Parse UTF-8 text data according to ESP32 specification
            # Format: [base_action:6][text_len:1][utf8_text:text_len] (max 8 bytes)
            if action_type == KeyTypes.UTF8 and offset < len(response):
                text_len = response[offset]
                offset += 1
                
                if text_len > 0 and text_len <= 8 and offset + text_len <= len(response):
                    try:
                        text_bytes = response[offset:offset + text_len]
                        text = text_bytes.decode('utf-8')
                        action['text'] = text
                        offset += text_len
                        logger.debug(f"Action {i} UTF-8 text: '{text}' ({text_len} bytes)")
                    except UnicodeDecodeError:
                        logger.warning(f"Failed to decode UTF-8 text for action {i}: {text_bytes.hex()}")
                        action['text'] = f"<INVALID_UTF8_{text_bytes.hex()}>"
                        offset += text_len
                elif text_len > 8:
                    logger.error(f"Action {i} UTF-8: Invalid text_len={text_len} > 8 bytes")
                    action['text'] = "<ERROR_TOO_LONG>"
                elif text_len > 0:
                    logger.warning(f"Action {i} UTF-8: Not enough data for text_len={text_len}")
                    action['text'] = "<TRUNCATED>"
                    offset += min(text_len, len(response) - offset)
                else:
                    action['text'] = ""
                    logger.debug(f"Action {i} UTF-8: Empty text (text_len=0)")
            
            actions.append(action)
        
        return {
            'key_id': key_id,
            'enabled': enabled,
            'action_count': action_count,
            'actions': actions,
            'key_name': KeyIDs.NAMES.get(key_id, f"Key {key_id}")
        }
    
    # ========================================
    # CONFIGURATOR SUPPORT METHODS
    # ========================================
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """
        Get all supported keyboard layouts for configurator applications
        
        Returns:
            Dictionary with layout information for dropdowns and UI
            
        Example:
            layouts = scanpad.keys.get_supported_languages()
            for layout_id, info in layouts['layouts'].items():
                print(f"{info['name']} - {info['description']}")
        """
        from ..utils.constants import KeyboardLayouts
        
        # Organize layouts by categories for UI
        windows_layouts = [
            (KeyboardLayouts.WIN_US_QWERTY, "US English QWERTY", "Windows + QWERTY + US English"),
            (KeyboardLayouts.WIN_FR_AZERTY, "French AZERTY", "Windows + AZERTY + French"),
            (KeyboardLayouts.WIN_BE_AZERTY, "Belgian French AZERTY", "Windows + AZERTY + Belgian French"),
            (KeyboardLayouts.WIN_DE_QWERTZ, "German QWERTZ", "Windows + QWERTZ + German"),
            (KeyboardLayouts.WIN_ES_QWERTY, "Spanish QWERTY", "Windows + QWERTY + Spanish"),
            (KeyboardLayouts.WIN_IT_QWERTY, "Italian QWERTY", "Windows + QWERTY + Italian"),
            (KeyboardLayouts.WIN_PT_QWERTY, "Portuguese QWERTY", "Windows + QWERTY + Portuguese"),
            (KeyboardLayouts.WIN_NL_QWERTY, "Dutch QWERTY", "Windows + QWERTY + Dutch"),
        ]
        
        macos_layouts = [
            (KeyboardLayouts.MAC_US_QWERTY, "US English QWERTY", "macOS + QWERTY + US English"),
            (KeyboardLayouts.MAC_FR_AZERTY, "French AZERTY", "macOS + AZERTY + French"),
            (KeyboardLayouts.MAC_BE_AZERTY, "Belgian French AZERTY", "macOS + AZERTY + Belgian French"),
        ]
        
        # Build comprehensive layout info
        layouts = {}
        categories = {
            "Windows/Linux": windows_layouts,
            "macOS": macos_layouts
        }
        
        for category, layout_list in categories.items():
            for layout_id, name, description in layout_list:
                layouts[layout_id] = {
                    "id": layout_id,
                    "name": name,
                    "description": description,
                    "category": category,
                    "hex_id": f"0x{layout_id:04X}"
                }
        
        return {
            "total_count": len(layouts),
            "categories": list(categories.keys()),
            "layouts": layouts,
            "default": KeyboardLayouts.WIN_US_QWERTY,
            "format_info": {
                "description": "Format: 0x[OS][PHYSICAL][LANGUAGE][RESERVED]",
                "os_codes": {"Windows": 0x1, "macOS": 0x2, "Android": 0x3, "iOS": 0x4, "Linux": 0x5},
                "physical_codes": {"QWERTY": 0x1, "AZERTY": 0x2, "QWERTZ": 0x3, "Dvorak": 0x4, "Colemak": 0x5},
                "language_codes": {"US": 0x1, "French": 0x2, "Belgian": 0x3, "German": 0x4, "Spanish": 0x5}
            }
        }
    
    def get_supported_action_types(self) -> Dict[str, Any]:
        """
        Get all supported action types for configurator applications
        
        Returns:
            Dictionary with action type information for UI builders
        """
        from ..utils.constants import KeyTypes, HIDKeyCodes, HIDModifiers, ConsumerCodes
        
        return {
            "action_types": {
                KeyTypes.UTF8: {
                    "id": KeyTypes.UTF8,
                    "name": "UTF-8 Text",
                    "description": "Type text with international character support",
                    "examples": ["Hello", "Café", "naïve", "Björk"],
                    "supports_delay": True,
                    "max_length": 8  # ESP32 firmware limitation
                },
                KeyTypes.HID: {
                    "id": KeyTypes.HID,
                    "name": "HID Key",
                    "description": "Direct keyboard key with optional modifiers",
                    "examples": [
                        {"key": "ENTER", "code": HIDKeyCodes.ENTER},
                        {"key": "Ctrl+C", "code": HIDKeyCodes.C, "modifiers": HIDModifiers.LEFT_CTRL},
                        {"key": "Alt+F4", "code": HIDKeyCodes.F4, "modifiers": HIDModifiers.LEFT_ALT}
                    ],
                    "supports_delay": True,
                    "supports_modifiers": True
                },
                KeyTypes.CONSUMER: {
                    "id": KeyTypes.CONSUMER,
                    "name": "Consumer Control",
                    "description": "Media and system control keys",
                    "examples": [
                        {"name": "Volume Up", "code": ConsumerCodes.VOLUME_UP},
                        {"name": "Play/Pause", "code": ConsumerCodes.PLAY_PAUSE},
                        {"name": "Home", "code": ConsumerCodes.HOME}
                    ],
                    "supports_delay": True,
                    "supports_modifiers": False
                },
                KeyTypes.API: {
                    "id": KeyTypes.API,
                    "name": "API Call",
                    "description": "Reserved for future API integrations",
                    "examples": [],
                    "supports_delay": True,
                    "supports_modifiers": False,
                    "status": "reserved"
                }
            },
            "constraints": {
                "max_actions_per_key": 10,
                "max_delay_ms": 65535,
                "utf8_max_bytes": 8
            },
            "common_hid_keys": {
                # Letters
                "Letters": {code: chr(ord('A') + code - HIDKeyCodes.A) for code in range(HIDKeyCodes.A, HIDKeyCodes.Z + 1)},
                # Numbers  
                "Numbers": {HIDKeyCodes.NUM_1: "1", HIDKeyCodes.NUM_2: "2", HIDKeyCodes.NUM_3: "3", 
                           HIDKeyCodes.NUM_4: "4", HIDKeyCodes.NUM_5: "5", HIDKeyCodes.NUM_6: "6",
                           HIDKeyCodes.NUM_7: "7", HIDKeyCodes.NUM_8: "8", HIDKeyCodes.NUM_9: "9", HIDKeyCodes.NUM_0: "0"},
                # Function keys
                "Function": {getattr(HIDKeyCodes, f"F{i}"): f"F{i}" for i in range(1, 13)},
                # Special keys
                "Special": {
                    HIDKeyCodes.ENTER: "Enter", HIDKeyCodes.ESCAPE: "Escape", HIDKeyCodes.BACKSPACE: "Backspace",
                    HIDKeyCodes.TAB: "Tab", HIDKeyCodes.SPACE: "Space", HIDKeyCodes.DELETE: "Delete"
                },
                # Arrows
                "Arrows": {
                    HIDKeyCodes.UP_ARROW: "↑", HIDKeyCodes.DOWN_ARROW: "↓", 
                    HIDKeyCodes.LEFT_ARROW: "←", HIDKeyCodes.RIGHT_ARROW: "→"
                }
            },
            "modifiers": {
                "Left": {
                    HIDModifiers.LEFT_CTRL: "Left Ctrl", HIDModifiers.LEFT_SHIFT: "Left Shift",
                    HIDModifiers.LEFT_ALT: "Left Alt", HIDModifiers.LEFT_GUI: "Left GUI/Cmd"
                },
                "Right": {
                    HIDModifiers.RIGHT_CTRL: "Right Ctrl", HIDModifiers.RIGHT_SHIFT: "Right Shift", 
                    HIDModifiers.RIGHT_ALT: "Right Alt", HIDModifiers.RIGHT_GUI: "Right GUI/Cmd"
                }
            }
        }
    
