"""
Unified Device Controller for aRdent ScanPad - CONSOLIDATED VERSION

This replaces separate LED, Buzzer, Device, and OTA controllers with a single
unified controller using composition pattern for clean organization.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Union

import os
import hashlib
import aiohttp
from .base import BaseController, Commands
from ..core.exceptions import (
    ConfigurationError, OTAError, AuthenticationError, NetworkError
)
from ..utils.constants import DeviceOrientations, BuzzerMelodies

logger = logging.getLogger(__name__)

class LEDSubController:
    """LED control sub-component of DeviceController"""
    
    def __init__(self, parent_controller):
        self.parent = parent_controller
        self._logger = parent_controller._logger
    
    async def turn_on(self, led_id: int) -> bool:
        """
        Turn on an LED
        
        Args:
            led_id: LED ID (1-9)
        """
        self.parent._validate_led_id(led_id)  # Raises exception if invalid
        payload = bytes([led_id, 1])  # led_id, state=on
        success = await self.parent._send_command(Commands.LED_SET_STATE, payload)
        if success:
            self._logger.debug(f"💡 LED {led_id} turned ON")
        return success
    
    async def turn_off(self, led_id: int) -> bool:
        """
        Turn off an LED
        
        Args:
            led_id: LED ID (1-9)
        """
        self.parent._validate_led_id(led_id)  # Raises exception if invalid
        payload = bytes([led_id, 0])  # led_id, state=off
        success = await self.parent._send_command(Commands.LED_SET_STATE, payload)
        if success:
            self._logger.debug(f"💡 LED {led_id} turned OFF")
        return success
    
    async def blink(self, led_id: int, frequency: float = 2.0) -> bool:
        """
        Start LED blinking
        
        Args:
            led_id: LED ID (1-9)
            frequency: Blink frequency in Hz (0.1-20.0)
        """
        self.parent._validate_led_id(led_id)  # Raises exception if invalid
        self.parent._validate_range('frequency', frequency, 0.1, 20.0)  # Raises exception if invalid
        
        freq_hz = int(frequency)
        payload = bytes([led_id, freq_hz & 0xFF, (freq_hz >> 8) & 0xFF])
        
        success = await self.parent._send_command(Commands.LED_START_BLINK, payload)
        if success:
            self._logger.debug(f"💡 LED {led_id} blinking at {frequency}Hz")
        return success
    
    async def stop_blink(self, led_id: int) -> bool:
        """Stop LED blinking"""
        self.parent._validate_led_id(led_id)  # Raises exception if invalid
        
        payload = bytes([led_id])
        success = await self.parent._send_command(Commands.LED_STOP_BLINK, payload)
        if success:
            self._logger.debug(f"💡 LED {led_id} stopped blinking")
        return success
    
    async def get_state(self, led_id: int) -> bool:
        """Get LED current state"""
        self.parent._validate_range('led_id', led_id, 1, 9)  # LEDs 1-9: LED1, LED2_RGB(R,G,B,combinations), LED3
        
        payload = bytes([led_id])
        response = await self.parent._send_command_and_wait(Commands.LED_GET_STATE, payload)
        state = self.parent._parse_uint8_response(response)
        return bool(state)
    
    async def get_all_states(self) -> Dict[int, bool]:
        """
        Get all LED states in one BLE call (optimized for device snapshot)
        
        Returns:
            Dictionary mapping LED ID to state: {1: True, 2: False, ...}
            Returns states for available LEDs based on ESP32 implementation
        """
        # Use special led_id = 0 to get all states from ESP32
        payload = bytes([0])
        response = await self.parent._send_command_and_wait(Commands.LED_GET_STATE, payload)
        
        # ESP32 returns 5 hardware GPIO states: LED1_G, LED2_R, LED2_G, LED2_B, LED3_G
        states_data = self.parent._parse_struct_response(response, expected_count=5)
        
        # Return hardware LED states with logical names (not GPIO details):
        # states[0] = LED Position 1: Green
        # states[1] = LED Position 2: Red component  
        # states[2] = LED Position 2: Green component
        # states[3] = LED Position 2: Blue component
        # states[4] = LED Position 3: Green
        led_states = {
            'led1_green': bool(states_data[0]),      # LED Position 1: Green
            'led2_red': bool(states_data[1]),        # LED Position 2: Red component
            'led2_green': bool(states_data[2]),      # LED Position 2: Green component  
            'led2_blue': bool(states_data[3]),       # LED Position 2: Blue component
            'led3_green': bool(states_data[4])       # LED Position 3: Green
        }
        
        self._logger.debug(f"💡 All LED states retrieved: {led_states}")
        return led_states
    
    async def all_off(self) -> bool:
        """Turn off all LEDs"""
        success = await self.parent._send_command(Commands.LED_ALL_OFF, bytes())
        if success:
            self._logger.debug("💡 All LEDs turned OFF")
        return success

class BuzzerSubController:
    """Buzzer control sub-component of DeviceController"""
    
    def __init__(self, parent_controller):
        self.parent = parent_controller
        self._logger = parent_controller._logger
    
    async def beep(self, duration_ms: int = 200, volume: int = None) -> bool:
        """
        Play a beep sound
        
        Args:
            duration_ms: Beep duration in milliseconds (50-5000)
            volume: Optional volume override (0-100)
        """
        self.parent._validate_range('duration_ms', duration_ms, 50, 5000)  # Raises exception if invalid
        
        # Two-step process: set volume if specified, then beep
        if volume is not None:
            self.parent._validate_range('volume', volume, 0, 100)  # Raises exception if invalid
            self._logger.debug(f"Playing beep: {duration_ms}ms at {volume}% volume")
            
            if not await self.set_volume(volume):
                return False
            await asyncio.sleep(0.1)
        else:
            self._logger.debug(f"Playing beep: {duration_ms}ms at current volume")
        
        duration_low = duration_ms & 0xFF
        duration_high = (duration_ms >> 8) & 0xFF
        
        payload = bytes([duration_low, duration_high])
        success = await self.parent._send_command(Commands.BUZZER_BEEP, payload)
        if success:
            self._logger.debug(f"🔊 Beep: {duration_ms}ms")
        return success
    
    async def play_melody(self, melody_name: str, volume: int = None) -> bool:
        """
        Play a predefined melody
        
        Args:
            melody_name: Name of melody to play
            volume: Optional volume override (0-100)
                    """
        melody_map = {
            'KEY': BuzzerMelodies.KEY,
            'START': BuzzerMelodies.START,
            'STOP': BuzzerMelodies.STOP,
            'NOTIF_UP': BuzzerMelodies.NOTIF_UP,
            'NOTIF_DOWN': BuzzerMelodies.NOTIF_DOWN,
            'CONFIRM': BuzzerMelodies.CONFIRM,
            'WARNING': BuzzerMelodies.WARNING,
            'ERROR': BuzzerMelodies.ERROR,
            'SUCCESS': BuzzerMelodies.SUCCESS
        }
        
        melody_choices = list(melody_map.keys())
        self.parent._validate_choices('melody_name', melody_name.upper(), melody_choices)  # Raises exception if invalid
        
        melody_id = melody_map[melody_name.upper()]
        if volume is not None:
            self.parent._validate_range('volume', volume, 0, 100)  # Raises exception if invalid
            self._logger.debug(f"Playing melody: {melody_name} at {volume}% volume")
            
            if not await self.set_volume(volume):
                return False
            await asyncio.sleep(0.1)
        else:
            self._logger.debug(f"Playing melody: {melody_name} at current volume")
        
        payload = bytes([melody_id])
        success = await self.parent._send_command(Commands.BUZZER_MELODY, payload)
        if success:
            self._logger.debug(f"🎵 Playing {melody_name}")
        return success
    
    async def set_volume(self, volume: int, enabled: bool = True) -> bool:
        """
        Set buzzer volume
        
        Args:
            volume: Volume level 0-100
            enabled: Enable/disable buzzer
                    """
        self.parent._validate_range('volume', volume, 0, 100)  # Raises exception if invalid
        
        self._logger.debug(f"Setting buzzer volume to {volume}%")
        payload = bytes([1 if enabled else 0, volume])
        success = await self.parent._send_command(Commands.BUZZER_SET_CONFIG, payload)
        if success:
            self._logger.debug(f"🔊 Buzzer volume set to {volume}%")
        return success
    
    async def get_config(self) -> dict:
        """Get current buzzer configuration"""
        response = await self.parent._send_command_and_wait(Commands.BUZZER_GET_CONFIG, bytes())
        struct_data = self.parent._parse_struct_response(response, expected_count=2)
        
        return {
            'enabled': bool(struct_data[0]),
            'volume': struct_data[1]
        }
    
    async def stop(self) -> bool:
        """Stop all buzzer output immediately"""
        self._logger.debug("Stopping buzzer")
        success = await self.parent._send_command(Commands.BUZZER_STOP, bytes())
        if success:
            self._logger.debug("🔇 Buzzer stopped")
        return success
    
    # Convenience methods
    async def play_success(self, volume: int = None) -> bool:
        """Play success melody"""
        return await self.play_melody('SUCCESS', volume)
    
    async def play_error(self, volume: int = None) -> bool:
        """Play error melody"""
        return await self.play_melody('ERROR', volume)
    
    async def play_warning(self, volume: int = None) -> bool:
        """Play warning melody"""
        return await self.play_melody('WARNING', volume)
    
    async def play_confirm(self, volume: int = None) -> bool:
        """Play confirmation melody"""
        return await self.play_melody('CONFIRM', volume)

class OTASubController:
    """
    Secure OTA update sub-component of DeviceController
    
    Provides device firmware update functionality with authentication.
    Requires proper credentials for accessing update binaries.
    
    Note:
        This functionality requires authentication credentials.
        Public users will not be able to use OTA without proper API keys.
    """
    
    def __init__(self, parent_controller):
        self.parent = parent_controller
        self._logger = parent_controller._logger
        self._api_key = None
        self._firmware_source = None
    
    def configure_auth(self, api_key: Optional[str] = None, 
                      firmware_source: Optional[str] = None) -> None:
        """
        Configure authentication for OTA updates
        
        Args:
            api_key: GitHub Personal Access Token for repository access
            firmware_source: Base URL for firmware downloads (optional)
            
        Note:
            For authenticated repository access, you MUST provide a GitHub Personal Access Token:
            1. Create token at: https://github.com/settings/tokens
            2. Required permissions: 'repo' (Repository access)
            3. Set via parameter or environment variable ARDENT_OTA_API_KEY
            
            Environment variables:
            - ARDENT_OTA_API_KEY: GitHub Personal Access Token
            - ARDENT_FIRMWARE_SOURCE: GitHub API endpoint (optional)
        """
        # API key from parameter or environment
        self._api_key = api_key or os.environ.get('ARDENT_OTA_API_KEY')
        
        # Update source from parameter or environment
        self._firmware_source = firmware_source or os.environ.get(
            'ARDENT_UPDATE_SOURCE',
            'https://api.github.com/repos/getyourway/aRdent-ScanPy'  # GitHub API endpoint
        )
        
        if not self._api_key:
            self._logger.warning("No GitHub token configured. Private repository access will fail.")
            self._logger.warning("Create a Personal Access Token at: https://github.com/settings/tokens")
            self._logger.warning("Required permissions: 'repo' (Repository access)")
    
    async def check_version(self) -> Optional[str]:
        """Get current firmware version from device"""
        response = await self.parent._send_command_and_wait(Commands.OTA_CHECK_VERSION, bytes())
        
        if not response or len(response) < 4:
            return None
            
        if response[0] == 0 and response[2] == 0x05 and response[3] == 2:
            if len(response) >= 5:
                version_bytes = response[5:]
                try:
                    version = version_bytes.decode('utf-8')
                    return version
                except UnicodeDecodeError:
                    pass
        
        return None
    
    async def check_for_update(self, current_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if firmware update is available
        
        Args:
            current_version: Current version (auto-detected if not provided)
            
        Returns:
            Update information dict with keys:
            - available: bool
            - latest_version: str
            - download_url: str (if authenticated)
            - changelog: str
            
        Raises:
            AuthenticationError: If API key is invalid
            NetworkError: If network request fails
        """
        # Auto-detect current version if not provided    
        if current_version is None:
            current_version = await self.check_version()
            if not current_version:
                raise ConfigurationError("Could not determine current firmware version")
        
        headers = {
            'User-Agent': 'aRdent-ScanPy/1.0'
        }
        
        # Add authorization if API key is configured
        if self._api_key:
            headers['Authorization'] = f'Bearer {self._api_key}'
        
        try:
            async with aiohttp.ClientSession() as session:
                # Use GitHub releases API
                url = f"{self._firmware_source}/releases/latest"
                
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 404:
                        if self._api_key:
                            raise NetworkError("Repository not found or no releases available")
                        else:
                            raise AuthenticationError("Private repository requires GitHub Personal Access Token")
                    elif resp.status == 401:
                        raise AuthenticationError("Invalid GitHub Personal Access Token")
                    elif resp.status == 403:
                        raise AuthenticationError("GitHub token lacks repository permissions")
                    elif resp.status != 200:
                        raise NetworkError(f"GitHub API returned {resp.status}: {await resp.text()}")
                        
                    release_data = await resp.json()
                    
                    # Parse GitHub release data
                    latest_version = release_data['tag_name']
                    download_url = None
                    
                    # Find ble_hid.bin asset
                    for asset in release_data.get('assets', []):
                        if asset['name'] == 'ble_hid.bin':
                            # For authenticated repos, use API URL instead of browser download URL
                            if self._api_key:
                                download_url = asset['url']  # API URL for authenticated download
                            else:
                                download_url = asset['browser_download_url']  # Public download URL
                            break
                    
                    # Simple version comparison
                    is_newer = latest_version != current_version
                    
                    return {
                        'available': is_newer,
                        'latest_version': latest_version,
                        'current_version': current_version,
                        'download_url': download_url,
                        'changelog': release_data.get('body', 'No changelog available'),
                        'release_notes': release_data.get('name', latest_version)
                    }
                    
        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error: {e}")
    
    async def start_update(self, firmware_url: Optional[str] = None,
                          progress_callback: Optional[callable] = None) -> bool:
        """
        Start secure OTA update process
        
        Args:
            firmware_url: Direct firmware URL (optional, uses check_for_update if not provided)
            progress_callback: Callback for progress updates (0-100)
            
        Returns:
            True if update successful
            
        Raises:
            OTAError: If update fails
            AuthenticationError: If not authenticated
        """
        # Send CHECK_VERSION command first (required by device)
        self._logger.info("Checking device OTA readiness...")
        check_response = await self.parent._send_command_and_wait(
            Commands.OTA_CHECK_VERSION, bytes()
        )
        
        if not check_response or check_response[0] != 0:
            raise OTAError("Device not ready for OTA update")
            
        # Send START_OTA command
        self._logger.info("Starting OTA service on device...")
        start_response = await self.parent._send_command_and_wait(
            Commands.OTA_START, bytes()
        )
        
        if not start_response or start_response[0] != 0:
            raise OTAError("Failed to start OTA service")
            
        # Device creates WiFi AP "aRdent ScanPad"
        self._logger.info("Device OTA service started. WiFi AP: 'aRdent ScanPad'")
        
        # Monitor OTA progress
        return await self._monitor_ota_progress(progress_callback)
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current OTA status from device"""
        response = await self.parent._send_command_and_wait(
            Commands.OTA_STATUS, bytes()
        )
        
        try:
            # Parse STRUCT response with 3 elements
            elements = self.parent._parse_struct_response(response, expected_count=3)
            
            # Elements are: [state, progress, reserved]
            state = elements[0]
            progress = elements[1]
            
            state_names = {
                0: "idle", 1: "checking", 2: "downloading", 
                3: "installing", 4: "success", 5: "error"
            }
            
            return {
                'state': state,
                'state_name': state_names.get(state, "unknown"),
                'progress': progress
            }
        except Exception:
            return {'state': 5, 'progress': 0, 'state_name': 'error'}  # OTA_STATE_ERROR
    
    async def cancel_update(self) -> bool:
        """Cancel ongoing OTA update"""
        success = await self.parent._send_command(Commands.OTA_CANCEL, bytes())
        if success:
            self._logger.info("OTA update cancelled")
        return success
    
    async def _monitor_ota_progress(self, progress_callback: Optional[callable] = None) -> bool:
        """Monitor OTA progress until completion"""
        last_progress = -1
        error_count = 0
        
        while True:
            try:
                status = await self.get_status()
                state = status['state']
                progress = status['progress']
                
                # Report progress if changed
                if progress != last_progress:
                    last_progress = progress
                    if progress_callback:
                        progress_callback(progress)
                    self._logger.info(f"OTA Progress: {progress}% - {status['state_name']}")
                
                # Check terminal states
                if state == 4:  # OTA_STATE_SUCCESS
                    self._logger.info("OTA update completed successfully")
                    return True
                elif state == 5:  # OTA_STATE_ERROR
                    raise OTAError("OTA update failed on device")
                    
                # Reset error count on successful status
                error_count = 0
                
            except Exception as e:
                error_count += 1
                if error_count > 5:
                    raise OTAError(f"Lost communication during OTA: {e}")
                    
            await asyncio.sleep(2)  # Check every 2 seconds
    
    async def start(self) -> bool:
        """
        Start basic OTA process (legacy method)
        
        For secure updates, use start_update() instead.
        """
        success = await self.parent._send_command(Commands.OTA_START, bytes())
        
        if success:
            self._logger.info("OTA update process started")
            self._logger.info("Device should create WiFi AP: 'aRdent ScanPad'")
            self._logger.info("Upload firmware to: http://192.168.4.1/firmware")
        else:
            self._logger.error("Failed to start OTA process")
        
        return success

class PeripheralController(BaseController):
    """
    Peripheral Controller - All Hardware Control
    
    This controller handles ALL device hardware operations via device_commands:
    - LED control (via .led sub-controller)
    - Buzzer control (via .buzzer sub-controller)  
    - Device settings (direct methods)
    - OTA updates (via .ota sub-controller)
    
    Architecture aligns with device firmware domains:
    - Config Domain (0x10-0x2F) → KeyConfigurationController (config_commands characteristic)
    - Device Domain (0x10-0x7F) → PeripheralController (device_commands characteristic)
    Command IDs can be reused in different domains due to BLE characteristic separation
    """
    
    def __init__(self, connection):
        """Initialize peripheral controller"""
        super().__init__(connection, 'device_commands', timeout=5.0)
        
        # Sub-controllers for organized functionality
        self.led = LEDSubController(self)
        self.buzzer = BuzzerSubController(self)
        self.ota = OTASubController(self)
    
    # DEVICE SETTINGS (Direct methods)
    
    async def set_orientation(self, orientation: int) -> bool:
        """Set device orientation (0=Portrait, 1=Landscape, 2=Reverse Portrait, 3=Reverse Landscape)"""
        self._validate_type('orientation', orientation, int)
        self._validate_choices('orientation', orientation, [0, 1, 2, 3])  # Raises exception if invalid
        
        self._logger.debug(f"Setting orientation to {orientation}")
        
        payload = bytes([orientation])
        success = await self._send_command(Commands.DEVICE_SET_ORIENTATION, payload)
        
        if success:
            self._logger.debug(f"Orientation set to {orientation}")
        return success
    
    async def get_orientation(self) -> Optional[int]:
        """Get current device orientation (returns 0-3)"""
        response = await self._send_command_and_wait(Commands.DEVICE_GET_ORIENTATION, bytes())
        
        try:
            orientation_code = self._parse_uint8_response(response)
            if orientation_code in [0, 1, 2, 3]:
                return orientation_code
            return None
        except:
            return None
    
    async def set_language(self, layout_id: int) -> bool:
        """
        Set device keyboard layout
        
        Args:
            layout_id: Keyboard layout ID (0-65535)
                    """
        self._validate_range('layout_id', layout_id, 0, 65535)  # Raises exception if invalid
        
        self._logger.debug(f"Setting keyboard layout to 0x{layout_id:04X}")
        
        # Send as 16-bit little-endian and wait for response to check status
        payload = bytes([layout_id & 0xFF, (layout_id >> 8) & 0xFF])
        
        try:
            response = await self._send_command_and_wait(Commands.DEVICE_SET_LANGUAGE, payload)
            
            # Check response status (first byte)
            if not response or len(response) < 1:
                return False
                
            if response[0] == 0x00:  # Success
                self._logger.debug(f"Language set to 0x{layout_id:04X}")
                return True
            else:  # Error status
                self._logger.error(f"Device rejected layout 0x{layout_id:04X} (status: 0x{response[0]:02X})")
                return False
                
        except Exception as e:
            self._logger.error(f"Failed to set language 0x{layout_id:04X}: {e}")
            return False
    
    async def get_language(self) -> Optional[int]:
        """Get current device keyboard layout ID"""
        response = await self._send_command_and_wait(Commands.DEVICE_GET_LANGUAGE, bytes())
        
        try:
            # Parse as uint16 little-endian
            if len(response) >= 6 and response[2] == 0x02:  # UINT16 type
                layout_id = response[4] | (response[5] << 8)
                self._logger.debug(f"Current layout: 0x{layout_id:04X}")
                return layout_id
        except:
            pass
        return None
    
    # Lua Script Management Methods
    
    async def clear_lua_script(self) -> bool:
        """
        Clear/delete the currently loaded Lua script
        
        Returns:
            bool: True if script was cleared successfully
        """
        try:
            success = await self._send_command(Commands.LUA_CLEAR_SCRIPT, bytes())
            if success:
                self._logger.info("✅ Lua script cleared successfully")
            else:
                self._logger.warning("❌ Failed to clear Lua script")
            return success
        except Exception as e:
            self._logger.error(f"Error clearing Lua script: {e}")
            return False
    
    async def get_lua_script_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the currently loaded Lua script
        
        Returns:
            Dictionary with script info or None if no script loaded
        """
        try:
            response = await self._send_command_and_wait(Commands.LUA_GET_SCRIPT_INFO, bytes())
            if response and len(response) > 4:
                # Parse script info response (implementation depends on ESP32 response format)
                return {
                    "loaded": True,
                    "size": len(response) - 4,  # Approximate
                    "status": "active"
                }
        except Exception as e:
            self._logger.debug(f"No Lua script info available: {e}")
        
        return None
    
    async def set_auto_shutdown(self, enabled: bool = True, 
                               no_connection_timeout_min: int = 60, 
                               no_activity_timeout_min: int = 30) -> bool:
        """Set auto shutdown configuration - KISS version"""
        
        # Simple validation
        self._validate_range('no_connection_timeout_min', no_connection_timeout_min, 1, 1440)
        self._validate_range('no_activity_timeout_min', no_activity_timeout_min, 1, 1440)
        
        # Create payload: [enabled, no_conn_low, no_conn_high, no_activity_low, no_activity_high]
        payload = bytes([
            1 if enabled else 0,
            no_connection_timeout_min & 0xFF,
            (no_connection_timeout_min >> 8) & 0xFF,
            no_activity_timeout_min & 0xFF,
            (no_activity_timeout_min >> 8) & 0xFF
        ])
        
        self._logger.debug(f"Auto shutdown: enabled={enabled}, no_conn={no_connection_timeout_min}min, no_act={no_activity_timeout_min}min")
        
        return await self._send_command(Commands.POWER_SET_AUTO_SHUTDOWN, payload)
    
    async def get_auto_shutdown(self) -> Optional[Dict[str, Any]]:
        """Get auto shutdown configuration"""
        response = await self._send_command_and_wait(Commands.POWER_GET_AUTO_SHUTDOWN, bytes())
        
        try:
            struct_data = self._parse_struct_response(response, expected_count=3)
            if len(struct_data) >= 5:
                return {
                    'enabled': bool(struct_data[0]),
                    'no_connection_timeout_min': struct_data[1] | (struct_data[2] << 8),
                    'no_activity_timeout_min': struct_data[3] | (struct_data[4] << 8)
                }
        except:
            pass
        return None
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get comprehensive device information using DIS and BAS services"""
        device_info = {
            'name': 'aRdent ScanPad',
            'connected': self.connection.is_connected if hasattr(self.connection, 'is_connected') else True,
            'address': getattr(self.connection, 'address', 'Unknown')
        }
        
        # Get DIS (Device Information Service) data
        try:
            device_info['manufacturer'] = await self.get_manufacturer_name()
            device_info['model'] = await self.get_model_number()
            device_info['serial_number'] = await self.get_serial_number()
            device_info['hardware_rev'] = await self.get_hardware_revision()
            device_info['firmware_rev'] = await self.get_firmware_revision()
            device_info['software_rev'] = await self.get_software_revision()
        except Exception as e:
            self._logger.debug(f"Failed to read DIS data: {e}")
        
        # Get Battery level from BAS service
        try:
            device_info['battery_level'] = await self.get_battery_level()
        except Exception as e:
            self._logger.debug(f"Failed to read battery level: {e}")
        
        # Try to get current settings
        try:
            orientation = await self.get_orientation()
            if orientation:
                device_info['orientation'] = orientation
                
            language = await self.get_language()
            if language is not None:
                device_info['language'] = language
                
            auto_shutdown = await self.get_auto_shutdown()
            if auto_shutdown:
                device_info['auto_shutdown'] = auto_shutdown
        except Exception as e:
            self._logger.debug(f"Some device info unavailable: {e}")
        
        return device_info
    
    # ========================================
    # JSON BATCH COMMANDS
    # ========================================
    
    async def execute_commands_from_json(self, json_config: dict) -> Dict[str, Any]:
        """Execute device commands from JSON using shared parser"""
        from ..utils.command_parser import CommandParser
        
        results = {"success": True, "executed": 0, "errors": []}
        
        try:
            # Parse JSON to binary commands using shared utility
            commands = CommandParser.parse_json_commands(json_config)
            
            # Execute each command via Bluetooth
            for command_id, payload in commands:
                try:
                    await self._send_command(command_id, payload)
                    results["executed"] += 1
                except Exception as e:
                    results["errors"].append(f"Command {command_id}: {str(e)}")
                    results["success"] = False
                    
        except Exception as e:
            results["errors"].append(f"Parse error: {str(e)}")
            results["success"] = False
        
        return results
    
    # ========================================
    # CONFIGURATOR SUPPORT METHODS  
    # ========================================
    
    def get_supported_orientations(self) -> Dict[str, Any]:
        """
        Get all supported device orientations for configurator applications
        
        Returns:
            Dictionary with orientation information for UI dropdowns
        """
        from ..utils.constants import DeviceOrientations
        
        orientations = {
            DeviceOrientations.PORTRAIT: {
                "id": DeviceOrientations.PORTRAIT,
                "name": "Portrait",
                "description": "0° rotation - Normal vertical orientation",
                "icon": "portrait",
                "rotation_degrees": 0
            },
            DeviceOrientations.LANDSCAPE: {
                "id": DeviceOrientations.LANDSCAPE,
                "name": "Landscape",
                "description": "90° clockwise rotation - Horizontal orientation",
                "icon": "landscape",
                "rotation_degrees": 90
            },
            DeviceOrientations.REVERSE_PORTRAIT: {
                "id": DeviceOrientations.REVERSE_PORTRAIT,
                "name": "Reverse Portrait",
                "description": "180° rotation - Upside down vertical",
                "icon": "reverse_portrait",
                "rotation_degrees": 180
            },
            DeviceOrientations.REVERSE_LANDSCAPE: {
                "id": DeviceOrientations.REVERSE_LANDSCAPE,
                "name": "Reverse Landscape",
                "description": "270° clockwise rotation - Reverse horizontal",
                "icon": "reverse_landscape",
                "rotation_degrees": 270
            }
        }
        
        return {
            "total_count": len(orientations),
            "orientations": orientations,
            "default": DeviceOrientations.PORTRAIT,
            "valid_range": [0, 1, 2, 3]
        }
    
    def get_supported_led_colors(self) -> Dict[str, Any]:
        """
        Get all supported LED configurations for configurator applications
        
        Returns:
            Dictionary with LED information for UI builders
        """
        from ..utils.constants import LEDs
        
        individual_leds = {}
        for led_id in LEDs.ALL:
            individual_leds[led_id] = {
                "id": led_id,
                "name": LEDs.NAMES[led_id],
                "type": "individual",
                "description": f"Individual control for {LEDs.NAMES[led_id]}",
                "supports_blink": True,
                "supports_state_query": True
            }
        
        rgb_colors = {}
        for led_id in LEDs.ALL_RGB:
            rgb_colors[led_id] = {
                "id": led_id,
                "name": LEDs.NAMES[led_id],
                "type": "rgb_mode",
                "description": f"RGB color mode: {LEDs.NAMES[led_id]}",
                "supports_blink": True,
                "supports_state_query": False  # RGB modes don't support state query
            }
        
        return {
            "total_count": len(LEDs.ALL_WITH_RGB),
            "individual_leds": individual_leds,
            "rgb_colors": rgb_colors,
            "all_leds": {**individual_leds, **rgb_colors},
            "capabilities": {
                "individual_control": LEDs.ALL,
                "rgb_modes": LEDs.ALL_RGB,
                "supports_blink": LEDs.ALL_WITH_RGB,
                "supports_all_off": True,
                "max_blink_frequency": 20.0,
                "min_blink_frequency": 0.1
            },
            "device_mapping": {
                "description": "LED IDs map directly to device LED commands",
                "individual_leds": {
                    1: "Green LED 1",
                    2: "Green LED 2"
                },
                "rgb_central_led": "Central RGB LED with 7 color modes (IDs 3-9)"
            }
        }
    
    def get_supported_buzzer_melodies(self) -> Dict[str, Any]:
        """
        Get all supported buzzer melodies for configurator applications
        
        Returns:
            Dictionary with melody information for UI dropdowns
        """
        from ..utils.constants import BuzzerMelodies
        
        melodies = {}
        for melody_id, name in BuzzerMelodies.NAMES.items():
            melodies[melody_id] = {
                "id": melody_id,
                "name": name,
                "description": f"Play {name.lower()} melody",
                "category": "system" if melody_id in [BuzzerMelodies.START, BuzzerMelodies.STOP] else "notification"
            }
        
        # Organize by categories for UI
        categories = {
            "system": [BuzzerMelodies.START, BuzzerMelodies.STOP],
            "notification": [BuzzerMelodies.NOTIF_UP, BuzzerMelodies.NOTIF_DOWN],
            "feedback": [BuzzerMelodies.KEY, BuzzerMelodies.CONFIRM, BuzzerMelodies.SUCCESS],
            "alert": [BuzzerMelodies.WARNING, BuzzerMelodies.ERROR]
        }
        
        return {
            "total_count": len(melodies),
            "melodies": melodies,
            "categories": categories,
            "capabilities": {
                "supports_custom_beep": True,
                "min_duration_ms": 50,
                "max_duration_ms": 5000,
                "volume_range": [0, 100],
                "supports_volume_per_call": True,
                "supports_stop": True
            },
            "common_melodies": {
                "startup": BuzzerMelodies.START,
                "success": BuzzerMelodies.SUCCESS,
                "error": BuzzerMelodies.ERROR,
                "key_press": BuzzerMelodies.KEY
            }
        }
    
    def get_device_capabilities(self) -> Dict[str, Any]:
        """
        Get comprehensive device capabilities for configurator applications
        
        Returns:
            Complete device capability information for advanced UI builders
        """
        return {
            "device_info": {
                "name": "aRdent ScanPad",
                "manufacturer": "aRdent",
                "type": "BLE HID Keypad",
                "matrix_size": "4×4",
                "total_keys": 20,  # 16 matrix + 4 button actions
                "connectivity": ["BLE", "WiFi (OTA only)"]
            },
            "hardware_capabilities": {
                "leds": self.get_supported_led_colors(),
                "buzzer": self.get_supported_buzzer_melodies(),
                "orientations": self.get_supported_orientations(),
                "battery": {
                    "monitoring": True,
                    "fuel_gauge": "Integrated",
                    "auto_shutdown": True,
                    "configurable_timeouts": True
                },
                "ota_updates": {
                    "supported": True,
                    "method": "WiFi AP + HTTP",
                    "github_integration": True,
                    "version_checking": True
                }
            },
            "key_configuration": {
                "matrix_keys": 16,
                "button_actions": 4,
                "max_actions_per_key": 10,
                "supported_action_types": ["UTF8", "HID", "Consumer", "API (reserved)"],
                "utf8_max_length": 8,
                "supports_delays": True,
                "supports_sequences": True
            },
            "communication": {
                "ble_services": {
                    "config_domain": "Key/button configuration",
                    "device_domain": "Hardware control (LED/Buzzer/Settings/OTA)"
                },
                "command_response": "All commands return device status confirmation",
                "async_operations": True,
                "batch_operations": "Limited support"
            },
            "power_management": {
                "auto_shutdown": {
                    "configurable": True,
                    "min_timeout_minutes": 1,
                    "max_timeout_minutes": 1440,
                    "separate_connection_activity_timeouts": True
                },
                "activity_tracking": True,
                "battery_monitoring": True
            }
        }
    
    # BLE Device Information Service (DIS) Methods
    
    async def get_manufacturer_name(self) -> str:
        """Get manufacturer name from DIS service"""
        return await self._read_dis_characteristic("manufacturer_name") or "aRdent"
    
    async def get_model_number(self) -> str:
        """Get model number from DIS service"""
        return await self._read_dis_characteristic("model_number") or "ScanPad"
    
    async def get_serial_number(self) -> str:
        """Get serial number from DIS service"""
        return await self._read_dis_characteristic("serial_number") or "Unknown"
    
    async def get_hardware_revision(self) -> str:
        """Get hardware revision from DIS service"""
        return await self._read_dis_characteristic("hardware_revision") or "Unknown"
    
    async def get_firmware_revision(self) -> str:
        """Get firmware revision from DIS service"""
        return await self._read_dis_characteristic("firmware_revision") or "Unknown"
    
    async def get_software_revision(self) -> str:
        """Get software revision from DIS service"""
        return await self._read_dis_characteristic("software_revision") or "Unknown"
    
    async def get_battery_level(self) -> int:
        """Get battery level from BAS service (0-100)"""
        try:
            # Battery Service UUID: 0x180F
            # Battery Level Characteristic UUID: 0x2A19
            battery_level_uuid = "00002a19-0000-1000-8000-00805f9b34fb"
            
            client = self.connection.client
            if not client or not client.is_connected:
                return 0
            
            data = await client.read_gatt_char(battery_level_uuid)
            return int(data[0]) if data else 0
            
        except Exception as e:
            self._logger.debug(f"Failed to read battery level: {e}")
            return 0
    
    async def _read_dis_characteristic(self, char_name: str) -> str:
        """Read a DIS characteristic by name"""
        try:
            # DIS Service UUID: 0x180A
            char_uuids = {
                "manufacturer_name": "00002a29-0000-1000-8000-00805f9b34fb",
                "model_number": "00002a24-0000-1000-8000-00805f9b34fb", 
                "serial_number": "00002a25-0000-1000-8000-00805f9b34fb",
                "hardware_revision": "00002a27-0000-1000-8000-00805f9b34fb",
                "firmware_revision": "00002a26-0000-1000-8000-00805f9b34fb",
                "software_revision": "00002a28-0000-1000-8000-00805f9b34fb"
            }
            
            if char_name not in char_uuids:
                return None
            
            char_uuid = char_uuids[char_name]
            client = self.connection.client
            
            if not client or not client.is_connected:
                return None
            
            data = await client.read_gatt_char(char_uuid)
            return data.decode('utf-8').strip() if data else None
            
        except Exception as e:
            self._logger.debug(f"Failed to read DIS characteristic {char_name}: {e}")
            return None