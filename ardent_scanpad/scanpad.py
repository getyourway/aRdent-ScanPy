"""
Main ScanPad class for aRdent ScanPad library

Provides the primary interface for controlling aRdent ScanPad devices
with high-level, user-friendly API.
"""

import asyncio
import logging
from typing import Optional, Dict, Any

from .core.connection import BLEConnection
from .core.exceptions import ConnectionError, ConfigurationError
from .controllers.keys import KeyConfigurationController
from .controllers.device import PeripheralController
from .controllers.ota_controller import OTAController

logger = logging.getLogger(__name__)


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
            await scanpad.device.set_auto_shutdown(60)
            
            # OTA Updates
            version = await scanpad.ota.check_for_updates()
            await scanpad.ota.update_firmware()
        ```
    """
    
    def __init__(self, auto_reconnect: bool = True, timeout: float = 30.0):
        """
        Initialize ScanPad controller
        
        Args:
            auto_reconnect: Enable automatic reconnection on disconnection
            timeout: Default timeout for BLE operations (seconds)
        """
        # Core connection
        self.connection = BLEConnection(auto_reconnect=auto_reconnect, timeout=timeout)
        
        # Controllers (initialized after connection)
        self.keys: Optional[KeyConfigurationController] = None        # Key configuration controller
        self.device: Optional[PeripheralController] = None  # Device control controller
        self.ota: Optional[OTAController] = None            # OTA update controller
        
        # State
        self._initialized = False
        
    async def __aenter__(self):
        """Async context manager entry - connects and initializes device"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - disconnects device"""
        await self.disconnect()
    
    async def connect(self, address: Optional[str] = None, timeout: Optional[float] = None) -> None:
        """
        Connect to aRdent ScanPad device
        
        Args:
            address: Device BLE address (auto-discovered if None)
            timeout: Connection timeout in seconds
            
        Raises:
            ConnectionError: If connection fails
            DeviceNotFoundError: If device not found
            TimeoutError: If connection times out
        """
        logger.info("🚀 Connecting to aRdent ScanPad")
        
        # Connect to device
        await self.connection.connect(address, timeout)
        
        # Initialize controllers
        await self._initialize_controllers()
        
        # Setup BLE notifications
        await self._setup_notifications()
        
        self._initialized = True
        logger.info("✅ aRdent ScanPad ready")
    
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
        
        logger.info("✅ Disconnected from aRdent ScanPad")
    
    async def _initialize_controllers(self) -> None:
        """Initialize device controllers"""
        logger.debug("🔧 Initializing controllers")
        
        # Key/button configuration controller
        self.keys = KeyConfigurationController(self.connection)
        
        # Hardware control controller
        self.device = PeripheralController(self.connection)
        
        # OTA update controller
        self.ota = OTAController(self.device)
        
        logger.debug("✅ Controllers initialized")
        logger.debug("   📋 keys: Key/button configuration")
        logger.debug("   🔧 device: LED/Buzzer/Settings/OTA")
        logger.debug("   🚀 ota: Firmware updates")
    
    async def _setup_notifications(self) -> None:
        """Setup BLE notification handlers"""
        # Use default notification handler which stores responses in connection._received_responses
        await self.connection.setup_notifications()
        logger.debug("✅ BLE notifications configured")
    
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
    
    @property
    def device_info(self) -> Dict[str, Any]:
        """Get basic device information - synchronous version"""
        return {
            'name': 'aRdent ScanPad',
            'connected': self.is_connected,
            'address': self.connection.address,
            'auto_reconnect': self.connection.auto_reconnect,
            'timeout': self.connection.timeout
        }
    
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
        logger.info("✅ Quick setup completed")
    
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
        logger.info("✅ Configuration restored")


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