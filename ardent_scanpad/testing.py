"""
aRdent ScanPad Testing Interface

Testing Interface - Advanced API for development and testing

This module provides testing interfaces with relaxed validation for 
testing purposes. These methods bypass normal validation and should be
used primarily for testing error handling and boundary conditions.

Example:
    ```python
    from ardent_scanpad.testing import ScanPadTesting
    
    async with ScanPadTesting() as device:
        # Normal API (same as ScanPad)
        await device.device.led.turn_on(1)
        
        # Testing API with bypass validation
        result = await device.testing.led_turn_on_force(-1)
        assert result == False  # ESP32 should reject invalid LED ID
    ```

Warning:
    These methods are for testing and development purposes and may cause unpredictable
    behavior if used incorrectly. The main ScanPad API should be used
    for all production code.
"""

import struct
import logging
from typing import Optional, List, Dict, Any

from .scanpad import ScanPad
from .controllers.base import Commands

logger = logging.getLogger(__name__)


class TestingInterface:
    """Testing interface with force/bypass methods"""
    
    def __init__(self, scanpad_testing: 'ScanPadTesting'):
        self.scanpad = scanpad_testing
        self._logger = logger
    
    # LED Testing Methods
    async def led_turn_on_force(self, led_id: int, bypass_validation: bool = False) -> bool:
        """
        Turn on LED with optional validation bypass for testing
        
        Args:
            led_id: LED ID (can be out of range if bypass_validation=True)
            bypass_validation: If True, bypass validation for testing invalid values
            
        Returns:
            bool: Command success (False expected for invalid IDs)
        """
        if not bypass_validation:
            self.scanpad.device._validate_led_id(led_id)
        
        # Handle out-of-range values for ESP32 validation testing
        if bypass_validation and (led_id < 0 or led_id > 255):
            payload = struct.pack('<Bb', led_id & 0xFF, 1)  # Use byte wrapping
        else:
            payload = bytes([led_id, 1])  # led_id, state=on
            
        success = await self.scanpad.device._send_command(Commands.LED_SET_STATE, payload)
        self._logger.debug(f"🧪 Testing LED {led_id} turn_on (bypass={bypass_validation}): {'✅' if success else '❌'}")
        return success
    
    async def led_turn_off_force(self, led_id: int, bypass_validation: bool = False) -> bool:
        """Turn off LED with optional validation bypass for testing"""
        if not bypass_validation:
            self.scanpad.device._validate_led_id(led_id)
        
        if bypass_validation and (led_id < 0 or led_id > 255):
            payload = struct.pack('<Bb', led_id & 0xFF, 0)
        else:
            payload = bytes([led_id, 0])  # led_id, state=off
            
        success = await self.scanpad.device._send_command(Commands.LED_SET_STATE, payload)
        self._logger.debug(f"🧪 Testing LED {led_id} turn_off (bypass={bypass_validation}): {'✅' if success else '❌'}")
        return success
    
    async def led_blink_force(self, led_id: int, frequency: float = 2.0, bypass_validation: bool = False) -> bool:
        """Blink LED with optional validation bypass for testing"""
        if not bypass_validation:
            self.scanpad.device._validate_led_id(led_id)
        
        # Handle zero frequency for testing (would cause division by zero)
        if frequency <= 0:
            if not bypass_validation:
                raise ValueError("Frequency must be positive")
            period = 255  # Max period for testing
        else:
            # Convert frequency to period (ESP32 expects period in 100ms units)
            period = max(1, int(10.0 / frequency))
        
        if bypass_validation and (led_id < 0 or led_id > 255):
            payload = struct.pack('<BbB', led_id & 0xFF, 2, period)
        else:
            payload = bytes([led_id, 2, period])  # led_id, mode=blink, period
            
        success = await self.scanpad.device._send_command(Commands.LED_SET_STATE, payload)
        self._logger.debug(f"🧪 Testing LED {led_id} blink f={frequency}Hz (bypass={bypass_validation}): {'✅' if success else '❌'}")
        return success
    
    async def led_stop_blink_force(self, led_id: int, bypass_validation: bool = False) -> bool:
        """Stop LED blink with optional validation bypass for testing"""
        if not bypass_validation:
            self.scanpad.device._validate_led_id(led_id)
        
        if bypass_validation and (led_id < 0 or led_id > 255):
            payload = struct.pack('<Bb', led_id & 0xFF, 0)
        else:
            payload = bytes([led_id, 0])  # led_id, state=off (stops blink)
            
        success = await self.scanpad.device._send_command(Commands.LED_SET_STATE, payload)
        self._logger.debug(f"🧪 Testing LED {led_id} stop_blink (bypass={bypass_validation}): {'✅' if success else '❌'}")
        return success
    
    async def led_get_state_force(self, led_id: int, bypass_validation: bool = False) -> Optional[bool]:
        """Get LED state with optional validation bypass for testing"""
        if not bypass_validation:
            self.scanpad.device._validate_led_id(led_id)
        
        if bypass_validation and (led_id < 0 or led_id > 255):
            payload = struct.pack('<B', led_id & 0xFF)
        else:
            payload = bytes([led_id])
            
        response = await self.scanpad.device._send_command_and_wait(Commands.LED_GET_STATE, payload)
        if response and len(response) >= 1:
            state = response[0] == 1
            self._logger.debug(f"🧪 Testing LED {led_id} get_state (bypass={bypass_validation}): {state}")
            return state
        return None
    
    # Buzzer Testing Methods
    async def buzzer_beep_force(self, duration_ms: int = 200, volume: Optional[int] = None, 
                               bypass_validation: bool = False) -> bool:
        """Beep with optional validation bypass for testing"""
        if not bypass_validation and volume is not None:
            if not (0 <= volume <= 100):
                raise ValueError("Volume must be between 0 and 100")
        
        if volume is None:
            payload = struct.pack('<H', duration_ms)  # duration only
        else:
            # Allow invalid volumes for testing if bypass is enabled
            vol = volume if bypass_validation else max(0, min(100, volume))
            payload = struct.pack('<HB', duration_ms, vol)
            
        success = await self.scanpad.device._send_command(Commands.BUZZER_BEEP, payload)
        self._logger.debug(f"🧪 Testing buzzer beep {duration_ms}ms vol={volume} (bypass={bypass_validation}): {'✅' if success else '❌'}")
        return success
    
    async def buzzer_set_volume_force(self, volume: int, enabled: bool = True, 
                                     bypass_validation: bool = False) -> bool:
        """Set buzzer volume with optional validation bypass for testing"""
        if not bypass_validation:
            if not (0 <= volume <= 100):
                raise ValueError("Volume must be between 0 and 100")
        
        # Allow invalid volumes for testing if bypass is enabled
        if bypass_validation:
            # Handle negative volumes by using struct to pack as signed then interpret as unsigned
            if volume < 0:
                vol = (256 + volume) & 0xFF  # Two's complement for negative
            elif volume > 255:
                vol = volume & 0xFF  # Truncate high values
            else:
                vol = volume
        else:
            vol = max(0, min(100, volume))
        payload = bytes([vol, 1 if enabled else 0])
        
        success = await self.scanpad.device._send_command(Commands.BUZZER_SET_CONFIG, payload)
        self._logger.debug(f"🧪 Testing buzzer volume {volume} enabled={enabled} (bypass={bypass_validation}): {'✅' if success else '❌'}")
        return success
    
    # Language Testing Methods  
    async def set_language_force(self, layout_id: int, bypass_validation: bool = False) -> bool:
        """Set language with optional validation bypass for testing"""
        if not bypass_validation:
            # Normal validation would happen here
            pass
        
        # Allow invalid language IDs for testing
        payload = struct.pack('<H', layout_id & 0xFFFF if bypass_validation else layout_id)
        
        success = await self.scanpad.device._send_command(Commands.DEVICE_SET_LANGUAGE, payload)
        self._logger.debug(f"🧪 Testing set_language {layout_id:04X} (bypass={bypass_validation}): {'✅' if success else '❌'}")
        return success
    
    # Key Configuration Testing Methods
    async def set_key_config_force(self, key_id: int, actions: List[Dict[str, Any]], 
                                  bypass_validation: bool = False) -> bool:
        """Set key config with optional validation bypass for testing"""
        if not bypass_validation:
            # Normal validation
            if not (0 <= key_id <= 15):
                raise ValueError(f"Key ID must be 0-15, got {key_id}")
            if len(actions) > 10:
                raise ValueError(f"Maximum 10 actions per key, got {len(actions)}")
        
        # Build payload - allow invalid key_ids for testing
        try:
            payload_data = bytearray()
            payload_data.append(key_id & 0xFF if bypass_validation else key_id)
            payload_data.append(len(actions))
            
            # Add actions (simplified for testing)
            for action in actions:
                action_type = action.get('type', 1)
                action_data = action.get('data', b'test')
                if isinstance(action_data, str):
                    action_data = action_data.encode('utf-8')[:8]
                
                payload_data.append(action_type)
                payload_data.append(len(action_data))
                payload_data.extend(action_data)
            
            success = await self.scanpad.keys._send_config_command(0x80, bytes(payload_data))  # SET_KEY_CONFIG
            self._logger.debug(f"🧪 Testing set_key_config key={key_id} actions={len(actions)} (bypass={bypass_validation}): {'✅' if success else '❌'}")
            return success
            
        except Exception as e:
            self._logger.debug(f"🧪 Testing set_key_config key={key_id} failed: {e}")
            return False


class ScanPadTesting(ScanPad):
    """
    Testing version of ScanPad with access to force/bypass methods
    
    This class extends the main ScanPad class with additional testing methods
    that can bypass validation for testing ESP32 error handling.
    
    Usage:
        ```python
        from ardent_scanpad.testing import ScanPadTesting
        
        async with ScanPadTesting() as device:
            # Normal API (same as ScanPad)
            await device.device.led.turn_on(1)
            
            # Testing API
            result = await device.testing.led_turn_on_force(-1, bypass_validation=True)
            assert result == False  # ESP32 should reject
        ```
    """
    
    def __init__(self, auto_reconnect: bool = True, timeout: float = 30.0):
        super().__init__(auto_reconnect, timeout)
        self.testing: Optional[TestingInterface] = None
    
    async def connect(self, address: Optional[str] = None, timeout: Optional[float] = None) -> None:
        """Connect and initialize testing interface"""
        await super().connect(address, timeout)
        
        # Initialize testing interface after connection
        self.testing = TestingInterface(self)
        logger.info("🧪 Testing interface initialized")
    
    async def disconnect(self) -> None:
        """Disconnect and cleanup testing interface"""
        self.testing = None
        await super().disconnect()
        logger.info("🧪 Testing interface disconnected")


# For backward compatibility with existing test scripts
class ScanPadForceAPI(ScanPadTesting):
    """Deprecated: Use ScanPadTesting instead"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.warning("⚠️  ScanPadForceAPI is deprecated. Use ScanPadTesting instead.")