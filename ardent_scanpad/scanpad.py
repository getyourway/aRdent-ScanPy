"""
Main ScanPad class for aRdent ScanPad library

Provides the primary interface for controlling aRdent ScanPad devices
with high-level, user-friendly API.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from bleak import BleakScanner

from .core.connection import BLEConnection, DEVICE_NAME, SERVICE_UUID
from .core.exceptions import ConnectionError, ConfigurationError, DeviceNotFoundError
from .controllers.keys import KeyConfigurationController
from .controllers.device import PeripheralController
from .controllers.ota_controller import OTAController
from .controllers.qr_generator import QRGeneratorController

logger = logging.getLogger(__name__)


class DeviceInfo:
    """Device information structure for discovered devices"""
    
    def __init__(self, address: str, name: str, rssi: int, 
                 advertisement_data: Optional[Dict[str, Any]] = None):
        self.address = address
        self.name = name
        self.rssi = rssi
        self.advertisement_data = advertisement_data or {}
        self.discovered_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        result = {
            "address": self.address,
            "name": self.name,
            "rssi": self.rssi,
            "discovered_at": self.discovered_at
        }
        
        # Extract additional info from advertisement data if available
        if self.advertisement_data:
            # Try to extract firmware version from manufacturer data or service data
            manufacturer_data = self.advertisement_data.get('manufacturer_data', {})
            service_data = self.advertisement_data.get('service_data', {})
            
            # Look for firmware version in service data
            if SERVICE_UUID in service_data:
                # Parse service data if it contains version info
                pass  # Could be implemented based on ESP32 advertisement format
            
            # Add any other discoverable info
            result['raw_advertisement'] = self.advertisement_data
        
        return result


class ScanPad:
    """
    Main interface for aRdent ScanPad BLE HID device
    
    Unified architecture with two domains:
    - CONFIG DOMAIN: Key and button configuration (scanpad.keys.*)
    - DEVICE DOMAIN: Hardware control and settings (scanpad.device.*)
    
    Example:
        ```python
        async with ScanPad() as scanpad:
            # KEY CONFIGURATION (config domain)
            text_action = scanpad.keys.create_text_action("Hello")
            await scanpad.keys.set_key_config(0, [text_action])
            
            hid_action = scanpad.keys.create_hid_action(
                HIDKeyCodes.C, HIDModifiers.LEFT_CTRL
            )
            await scanpad.keys.set_key_config(1, [hid_action])
            await scanpad.keys.save_config()
            
            # HARDWARE CONTROL (device domain)
            # LED Control
            await scanpad.device.led.turn_on(1)
            await scanpad.device.led.blink(2, frequency=2.0)
            await scanpad.device.led.all_off()
            
            # Buzzer Control  
            await scanpad.device.buzzer.beep(200)
            await scanpad.device.buzzer.play_success()
            
            # Device Settings
            await scanpad.device.set_orientation("LANDSCAPE")
            await scanpad.device.set_language(0x1220)  # FR_AZERTY
            await scanpad.device.set_auto_shutdown(enabled=True, no_connection_timeout_min=60, no_activity_timeout_min=60)
            
            # OTA Updates
            version = await scanpad.ota.check_for_updates()
            await scanpad.ota.update_firmware()
        ```
    """
    
    def __init__(self, device_address: Optional[str] = None, 
                 device_name: Optional[str] = None,
                 auto_discover: bool = True,
                 auto_reconnect: bool = True, 
                 timeout: float = 30.0):
        """
        Initialize ScanPad controller
        
        Args:
            device_address: Specific BLE device address to connect to
            device_name: Specific device name to connect to (alternative to address)
            auto_discover: Enable auto-discovery if no specific device given
            auto_reconnect: Enable automatic reconnection on disconnection
            timeout: Default timeout for BLE operations (seconds)
        """
        # Connection preferences
        self._preferred_address = device_address
        self._preferred_name = device_name
        self._auto_discover = auto_discover
        
        # Core connection
        self.connection = BLEConnection(auto_reconnect=auto_reconnect, timeout=timeout)
        
        # Controllers (initialized after connection)
        self.keys: Optional[KeyConfigurationController] = None        # Key configuration controller
        self.device: Optional[PeripheralController] = None  # Device control controller
        self.ota: Optional[OTAController] = None            # OTA update controller
        self.qr: QRGeneratorController = QRGeneratorController()      # QR code generator (no connection needed)
        
        # Device info (populated after connection)
        self._device_info: Optional[Dict[str, Any]] = None
        self._connected_at: Optional[str] = None
        
        # State
        self._initialized = False
        
    async def __aenter__(self):
        """Async context manager entry - connects and initializes device"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - disconnects device"""
        await self.disconnect()
    
    # ========================================
    # STATIC DISCOVERY METHODS
    # ========================================
    
    @staticmethod
    async def discover_devices(timeout: float = 10.0, debug: bool = False) -> List[Dict[str, Any]]:
        """
        Scan for available aRdent ScanPad devices without connecting
        
        Args:
            timeout: Scan timeout in seconds
            debug: Enable debug logging for scan process
            
        Returns:
            List of discovered device information dictionaries:
            [
                {
                    "address": "AA:BB:CC:DD:EE:FF",
                    "name": "aRdent ScanPad", 
                    "rssi": -45,
                    "discovered_at": "2025-01-29T10:30:00.123456"
                }
            ]
            
        Raises:
            DeviceNotFoundError: If no devices found
        """
        if debug:
            logging.getLogger('bleak').setLevel(logging.DEBUG)
            
        logger.info(f"🔍 Discovering aRdent ScanPad devices (timeout: {timeout}s)")
        
        discovered_devices = []
        
        try:
            # Use BleakScanner to find all devices advertising our service
            devices = await BleakScanner.discover(timeout=timeout, return_adv=True)
            
            for device, advertisement_data in devices.values():
                # Check if device name matches our target
                device_name = device.name or advertisement_data.local_name or "Unknown"
                
                if DEVICE_NAME in device_name or "ScanPad" in device_name:
                    device_info = DeviceInfo(
                        address=device.address,
                        name=device_name,
                        rssi=advertisement_data.rssi,
                        advertisement_data={
                            'local_name': advertisement_data.local_name,
                            'manufacturer_data': dict(advertisement_data.manufacturer_data) if advertisement_data.manufacturer_data else {},
                            'service_data': dict(advertisement_data.service_data) if advertisement_data.service_data else {},
                            'service_uuids': list(advertisement_data.service_uuids) if advertisement_data.service_uuids else []
                        }
                    )
                    
                    discovered_devices.append(device_info.to_dict())
                    
                    if debug:
                        logger.debug(f"Found device: {device_name} at {device.address} (RSSI: {advertisement_data.rssi} dBm)")
            
            # Sort by RSSI (strongest signal first)
            discovered_devices.sort(key=lambda d: d['rssi'], reverse=True)
            
            logger.info(f"Discovery complete: Found {len(discovered_devices)} aRdent ScanPad device(s)")
            
            if not discovered_devices:
                raise DeviceNotFoundError(f"No aRdent ScanPad devices found during {timeout}s scan")
                
            return discovered_devices
            
        except Exception as e:
            if isinstance(e, DeviceNotFoundError):
                raise
            logger.error(f"Discovery failed: {e}")
            raise DeviceNotFoundError(f"Device discovery failed: {e}")
        finally:
            if debug:
                logging.getLogger('bleak').setLevel(logging.WARNING)
    
    @staticmethod
    async def is_device_available(device_address: str, timeout: float = 3.0) -> bool:
        """
        Quick check if specific device is reachable without full connection
        
        Args:
            device_address: BLE device address to check
            timeout: Check timeout in seconds (shorter than full connection)
            
        Returns:
            True if device is advertising and reachable
        """
        logger.debug(f"🔍 Checking availability of device {device_address} (timeout: {timeout}s)")
        
        try:
            devices = await BleakScanner.discover(timeout=timeout)
            
            for device in devices:
                if device.address.lower() == device_address.lower():
                    logger.debug(f"Device {device_address} is available")
                    return True
                    
            logger.debug(f"Device {device_address} not found during scan")
            return False
            
        except Exception as e:
            logger.warning(f"Availability check failed for {device_address}: {e}")
            return False
    
    @staticmethod
    async def scan_with_callback(
        callback: Callable[[Dict[str, Any]], None],
        timeout: float = 10.0,
        debug: bool = False
    ) -> None:
        """
        Scan with real-time callbacks for discovered devices
        Useful for live UI updates
        
        Args:
            callback: Function called for each discovered device
            timeout: Scan timeout in seconds
            debug: Enable debug logging
            
        Example:
            ```python
            def on_device_found(device_info):
                print(f"Found: {device_info['name']} (RSSI: {device_info['rssi']} dBm)")
            
            await ScanPad.scan_with_callback(on_device_found, timeout=15.0)
            ```
        """
        if debug:
            logging.getLogger('bleak').setLevel(logging.DEBUG)
            
        logger.info(f"🔍 Starting live device scan (timeout: {timeout}s)")
        
        found_addresses = set()  # Track devices we've already reported
        
        def detection_callback(device, advertisement_data):
            """Internal callback for each device detection"""
            try:
                # Avoid duplicate notifications for same device
                if device.address in found_addresses:
                    return
                    
                device_name = device.name or advertisement_data.local_name or "Unknown"
                
                # Check if this is an aRdent ScanPad device
                if DEVICE_NAME in device_name or "ScanPad" in device_name:
                    found_addresses.add(device.address)
                    
                    device_info = DeviceInfo(
                        address=device.address,
                        name=device_name,
                        rssi=advertisement_data.rssi,
                        advertisement_data={
                            'local_name': advertisement_data.local_name,
                            'manufacturer_data': dict(advertisement_data.manufacturer_data) if advertisement_data.manufacturer_data else {},
                            'service_data': dict(advertisement_data.service_data) if advertisement_data.service_data else {},
                            'service_uuids': list(advertisement_data.service_uuids) if advertisement_data.service_uuids else []
                        }
                    )
                    
                    # Call user's callback with device info
                    callback(device_info.to_dict())
                    
                    if debug:
                        logger.debug(f"Live discovery: {device_name} at {device.address} (RSSI: {advertisement_data.rssi} dBm)")
                        
            except Exception as e:
                logger.warning(f"⚠️  Error in live scan callback: {e}")
        
        try:
            # Start scanning with callback
            scanner = BleakScanner(detection_callback)
            await scanner.start()
            
            # Scan for the specified timeout
            await asyncio.sleep(timeout)
            
            await scanner.stop()
            
            logger.info(f"Live scan complete: Found {len(found_addresses)} unique device(s)")
            
        except Exception as e:
            logger.error(f"Live scan failed: {e}")
            raise DeviceNotFoundError(f"Live device scan failed: {e}")
        finally:
            if debug:
                logging.getLogger('bleak').setLevel(logging.WARNING)
    
    async def connect(self, address: Optional[str] = None, timeout: Optional[float] = None) -> None:
        """
        Connect to aRdent ScanPad device with smart device selection
        
        Connection priority:
        1. Explicit address parameter (highest priority)
        2. Preferred address from constructor
        3. Preferred name from constructor  
        4. Auto-discovery (fallback)
        
        Args:
            address: Device BLE address (overrides constructor preferences)
            timeout: Connection timeout in seconds
            
        Raises:
            ConnectionError: If connection fails
            DeviceNotFoundError: If device not found
            TimeoutError: If connection times out
        """
        logger.info("🚀 Connecting to aRdent ScanPad")
        
        # Smart device selection based on preferences
        target_address = address
        
        if not target_address:
            # Check constructor preferences first
            if self._preferred_address:
                logger.info(f"🎯 Using preferred address: {self._preferred_address}")
                target_address = self._preferred_address
                
                # Verify preferred device is available
                if not await self.is_device_available(target_address, timeout=3.0):
                    logger.warning(f"⚠️  Preferred device {target_address} not available, falling back to discovery")
                    target_address = None
                    
            elif self._preferred_name:
                logger.info(f"🎯 Looking for preferred device name: {self._preferred_name}")
                
                # Find device by name
                try:
                    devices = await self.discover_devices(timeout=timeout or 10.0)
                    for device in devices:
                        if self._preferred_name in device['name']:
                            target_address = device['address']
                            logger.info(f"Found preferred device '{self._preferred_name}' at {target_address}")
                            break
                    
                    if not target_address:
                        logger.warning(f"⚠️  Device with name '{self._preferred_name}' not found, falling back to discovery")
                        
                except DeviceNotFoundError:
                    logger.warning(f"⚠️  No devices found during name search, falling back to auto-discovery")
            
            # Fallback to auto-discovery if preferences failed or not set
            if not target_address and self._auto_discover:
                logger.info("🔍 Auto-discovering aRdent ScanPad device")
                # Let connection.connect() handle auto-discovery
                pass
            elif not target_address:
                raise ConnectionError("No device address specified and auto-discovery disabled")
        
        # Connect to device (target_address can be None for auto-discovery)
        await self.connection.connect(target_address, timeout)
        
        # Store connection info for device_info property
        self._connected_at = datetime.now().isoformat()
        
        # Initialize controllers
        await self._initialize_controllers()
        
        # Setup BLE notifications
        await self._setup_notifications()
        
        self._initialized = True
        logger.info("aRdent ScanPad ready")
    
    async def disconnect(self) -> None:
        """Disconnect from device"""
        logger.info("🔌 Disconnecting from aRdent ScanPad")
        
        self._initialized = False
        
        # Cleanup controllers
        self.keys = None
        self.device = None
        self.ota = None
        
        # Disconnect BLE
        await self.connection.disconnect()
        
        logger.info("Disconnected from aRdent ScanPad")
        
        # Clear device info
        self._device_info = None
        self._connected_at = None
    
    # ========================================
    # DEVICE INFORMATION PROPERTY
    # ========================================
    
    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        """
        Get cached device information (fast, no BLE calls)
        
        Returns device information structure with connection details always available
        and BLE service data (DIS/BAS) populated only after fetch_device_info().
        
        Connection info (always available):
        - address, name, connected_at, connection_status
        
        BLE service data (None until fetch_device_info()):
        - manufacturer, firmware_version, serial_number (from Device Information Service)
        - battery_level (from Battery Service)
        
        Returns:
            Dictionary with device information structure or None if not connected
        """
        if not self.connection.is_connected:
            return None
            
        # Return complete device info structure (with cached or None values)
        base_info = {
            "address": self.connection.address or "Unknown",
            "name": "aRdent ScanPad",
            "connected_at": self._connected_at,
            "connection_status": "connected" if self.connection.is_connected else "disconnected",
            # Essential fields filled by fetch_device_info() or None if not fetched yet
            "manufacturer": None,
            "firmware_version": None,
            "serial_number": None,
            "battery_level": None,
        }
        
        # Update with cached values if available
        if self._device_info:
            base_info.update(self._device_info)
            
        return base_info
    
    async def fetch_device_info(self) -> Dict[str, Any]:
        """
        Fetch complete device information from device via BLE
        
        Retrieves fresh information from device including:
        - Device Information Service (DIS): manufacturer, firmware_version, serial_number
        - Battery Service (BAS): battery_level
        - Connection info: address, name, status, connected_at
        
        This method makes multiple BLE calls and updates the device_info cache.
        
        Returns:
            Complete device information dictionary with all fields populated
        """
        if not self.connection.is_connected:
            raise ConnectionError("Device not connected")
            
        logger.debug("Refreshing device information")
        
        info = {
            "address": self.connection.address or "Unknown",
            "name": "aRdent ScanPad",
            "connected_at": self._connected_at,
            "connection_status": "connected"
        }
        
        try:
            # Get device information from controllers if available
            if self.device:
                # Get device info (firmware version, hardware, etc.)
                try:
                    device_details = await self.device.get_device_info()
                    if device_details:
                        info.update({
                            "firmware_version": device_details.get("firmware_rev", "Unknown"),
                            "hardware_version": device_details.get("hardware_rev", "Unknown"),
                            "serial_number": device_details.get("serial_number", "Unknown"),
                            "manufacturer": device_details.get("manufacturer", "Get Your Way")
                        })
                except Exception as e:
                    logger.debug(f"Could not fetch device details: {e}")
                
                # Get battery level
                try:
                    battery_level = await self.device.get_battery_level()
                    if battery_level is not None:
                        info["battery_level"] = battery_level
                except Exception as e:
                    logger.debug(f"Could not fetch battery info: {e}")
                
                # Get current language/orientation settings
                try:
                    current_language = await self.device.get_language()
                    if current_language is not None:
                        info["current_language"] = f"0x{current_language:04X}"
                except Exception as e:
                    logger.debug(f"Could not fetch language: {e}")
                
                try:
                    current_orientation = await self.device.get_orientation()
                    if current_orientation is not None:
                        orientations = {0: "Portrait", 1: "Landscape", 2: "Reverse Portrait", 3: "Reverse Landscape"}
                        info["current_orientation"] = orientations.get(current_orientation, f"Unknown({current_orientation})")
                except Exception as e:
                    logger.debug(f"Could not fetch orientation: {e}")
            
            # Try to get connection RSSI if supported by platform
            try:
                if hasattr(self.connection.client, 'get_rssi'):
                    rssi = await self.connection.client.get_rssi()
                    info["connection_rssi"] = rssi
            except Exception as e:
                logger.debug(f"Could not fetch RSSI: {e}")
            
            # Cache the refreshed info
            self._device_info = info.copy()
            
            logger.debug("Device information refreshed")
            return info
            
        except Exception as e:
            logger.error(f"Failed to refresh device info: {e}")
            # Return basic info even if detailed fetch fails
            self._device_info = info
            return info
    
    async def _initialize_controllers(self) -> None:
        """Initialize device controllers"""
        logger.debug("🔧 Initializing controllers")
        
        # Key/button configuration controller
        self.keys = KeyConfigurationController(self.connection)
        
        # Hardware control controller
        self.device = PeripheralController(self.connection)
        
        # OTA update controller
        self.ota = OTAController(self.device)
        
        logger.debug("Controllers initialized")
        logger.debug("   📋 keys: Key/button configuration")
        logger.debug("   🔧 device: LED/Buzzer/Settings/OTA")
        logger.debug("   🚀 ota: Firmware updates")
        
        logger.debug("Controllers initialized successfully")
    
    async def _setup_notifications(self) -> None:
        """Setup BLE notification handlers"""
        # Use default notification handler which stores responses in connection._received_responses
        await self.connection.setup_notifications()
        logger.debug("BLE notifications configured")
    
    def _handle_config_notification(self, sender, data: bytearray) -> None:
        """Handle config domain notifications"""
        if self.keys:
            self.keys._handle_config_response(bytes(data))
    
    def _handle_device_notification(self, sender, data: bytearray) -> None:
        """Handle device domain notifications"""
        data_bytes = bytes(data)
        
        # Route to device controller
        if self.device:
            # Device controller uses BaseController response handling
            pass
    
    @property
    def is_connected(self) -> bool:
        """Check if device is connected and initialized"""
        return self._initialized and self.connection.is_connected
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get comprehensive device information"""
        if not self.is_connected:
            return {
                'name': 'aRdent ScanPad',
                'connected': False,
                'address': None
            }
        
        # Get basic connection info
        device_info = {
            'name': 'aRdent ScanPad',
            'connected': self.is_connected,
            'address': self.connection.address
        }
        
        # Try to get additional device info from device controller
        if self.device:
            try:
                extended_info = await self.device.get_device_info()
                device_info.update(extended_info)
            except Exception as e:
                logger.debug(f"Could not get extended device info: {e}")
        
        return device_info
    
    
    # CONVENIENCE METHODS (shortcuts to common operations)
    
    async def quick_setup(self, key_configs: Dict[int, str]) -> None:
        """
        Quick setup for common key configurations
        
        Args:
            key_configs: Dictionary mapping key_id to text/action
            
        Example:
            await device.quick_setup({
                0: "Hello",        # UTF-8 text
                1: "World!",       # UTF-8 text  
                2: "ctrl+c",       # Hotkey shortcut
                3: "volume_up"     # Media control
            })
        """
        if not self.is_connected:
            raise ConnectionError("Device not connected")
        
        logger.info(f"⚡ Quick setup for {len(key_configs)} keys")
        
        for key_id, config in key_configs.items():
            try:
                # Parse configuration string
                if config.startswith("ctrl+") or config.startswith("alt+") or config.startswith("shift+"):
                    # Parse hotkey shortcuts - currently treated as text
                    action = self.keys.create_text_action(config)
                    await self.keys.set_key_config(key_id, [action])
                elif config in ["volume_up", "volume_down", "mute", "play_pause"]:
                    # Parse media controls - currently treated as text
                    action = self.keys.create_text_action(config)
                    await self.keys.set_key_config(key_id, [action])
                else:
                    # Treat as UTF-8 text
                    action = self.keys.create_text_action(config)
                    await self.keys.set_key_config(key_id, [action])
                    
            except Exception as e:
                logger.warning(f"Failed to configure key {key_id}: {e}")
        
        # Save configuration
        await self.keys.save_config()
        logger.info("Quick setup completed")
    
    async def backup_config(self) -> Dict[str, Any]:
        """
        Backup current device configuration
        
        Returns:
            Configuration dictionary
        """
        if not self.is_connected:
            raise ConnectionError("Device not connected")
        
        config = {
            'version': '1.0',
            'device': 'aRdent ScanPad',
            'keys': await self.keys.get_all_configs()
        }
        
        logger.info(f"💾 Backed up configuration ({len(config['keys'])} keys)")
        return config

    async def export_complete_configuration(self) -> List[Dict[str, Any]]:
        """
        Export complete keyboard configuration in standard JSON format
        
        Returns list of JSON commands compatible with QR codes and BLE transmission.
        Same format as used by sendJsonCommand and QR generation.
        
        Returns:
            List of JSON command dictionaries in standard format
        
        Example:
            config = await scanpad.export_complete_configuration()
            # Returns: [
            #   {
            #     "domain": "keyboard_config",
            #     "action": "set_key_config",
            #     "parameters": {
            #       "key_id": 0,
            #       "actions": [{"type": 0, "data": "Hello", "delay": 0}]
            #     }
            #   }
            # ]
        """
        if not self.is_connected:
            raise ConnectionError("Device not connected")
        
        return await self.keys.export_complete_configuration()
    
    async def restore_config(self, config: Dict[str, Any]) -> None:
        """
        Restore device configuration from backup
        
        Args:
            config: Configuration dictionary from backup_config()
        """
        if not self.is_connected:
            raise ConnectionError("Device not connected")
        
        if 'keys' not in config:
            raise ConfigurationError("Invalid configuration format")
        
        logger.info(f"📥 Restoring configuration ({len(config['keys'])} keys)")
        
        # Factory reset first
        await self.keys.factory_reset()
        await asyncio.sleep(1.0)
        
        # Restore key configurations
        for key_id, key_config in config['keys'].items():
            try:
                actions = key_config.get('actions', [])
                if actions:
                    await self.keys.set_key_config(int(key_id), actions)
                    
                # Restore enabled state
                enabled = key_config.get('enabled', True)
                await self.keys.set_key_enabled(int(key_id), enabled)
                
            except Exception as e:
                logger.warning(f"Failed to restore key {key_id}: {e}")
        
        # Save restored configuration
        await self.keys.save_config()
        logger.info("Configuration restored")


# Convenience function for simple usage
async def connect_scanpad(auto_reconnect: bool = True, timeout: float = 30.0) -> ScanPad:
    """
    Convenience function to connect to ScanPad device
    
    Args:
        auto_reconnect: Enable automatic reconnection
        timeout: Connection timeout in seconds
        
    Returns:
        Connected ScanPad instance
        
    Example:
        device = await connect_scanpad()
        action = device.keys.create_text_action("Hello")
        await device.keys.set_key_config(0, [action])
        await device.disconnect()
    """
    device = ScanPad(auto_reconnect=auto_reconnect, timeout=timeout)
    await device.connect()
    return device