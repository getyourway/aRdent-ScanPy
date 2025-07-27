"""
BLE Connection Manager for aRdent ScanPad library

Provides robust BLE connection handling with auto-reconnection,
error handling, and async context manager support.
"""

import asyncio
import logging
import platform
from typing import Optional, Dict, Any, Callable
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

from .exceptions import ConnectionError, DeviceNotFoundError, TimeoutError, NotificationError

logger = logging.getLogger(__name__)

# Device Configuration
DEVICE_NAME = "aRdent ScanPad"
SERVICE_UUID = "f0debc9a-7856-3412-f0de-bc9a78560000"

# BLE Characteristics
CHAR_UUIDS = {
    # Key/Button Configuration
    'config_commands': "f0debc9a-7856-3412-f0de-bc9a78560020",   # Write config commands
    'config_response': "f0debc9a-7856-3412-f0de-bc9a78560021",   # Read/Notify config responses
    
    # Device Control - LED, Buzzer, Settings, OTA
    'device_commands': "f0debc9a-7856-3412-f0de-bc9a78560010",   # Write device commands
    'device_response': "f0debc9a-7856-3412-f0de-bc9a78560011",   # Read/Notify device responses
}


class BLEConnection:
    """
    Professional BLE connection manager for aRdent ScanPad
    
    Features:
    - Auto-discovery and connection
    - Auto-reconnection on disconnection
    - Async context manager support
    - Robust error handling
    - Notification management
    """
    
    def __init__(self, auto_reconnect: bool = True, timeout: float = 30.0):
        """
        Initialize BLE connection manager
        
        Args:
            auto_reconnect: Enable automatic reconnection on disconnection
            timeout: Default timeout for operations in seconds
        """
        self.client: Optional[BleakClient] = None
        self.address: Optional[str] = None
        self.characteristics: Dict[str, BleakGATTCharacteristic] = {}
        self._notification_handlers: Dict[str, Callable] = {}
        self.auto_reconnect = auto_reconnect
        self.timeout = timeout
        self._connected = False
        self._reconnect_task: Optional[asyncio.Task] = None
        
        # Response handling for controllers - CLEAR DOMAIN SEPARATION
        self._received_device_responses = []  # Device domain responses (LED/Buzzer/Settings/OTA)
        self._received_config_responses = []  # Config domain responses (Keys/Buttons)
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
        
    async def find_device(self, timeout: Optional[float] = None) -> str:
        """
        Find aRdent ScanPad device with platform-optimized scanning
        
        Args:
            timeout: Scan timeout in seconds
            
        Returns:
            Device address/identifier (UUID on macOS, MAC address on Windows)
            
        Raises:
            DeviceNotFoundError: If device not found
            TimeoutError: If scan times out
        """
        scan_timeout = timeout or self.timeout
        is_macos = platform.system() == "Darwin"
        
        logger.info(f"🔍 Scanning for {DEVICE_NAME} (timeout: {scan_timeout}s, platform: {platform.system()})")
        
        try:
            # Phase 1: Fast scanning with early exit (1-3 seconds typical)
            logger.debug("Phase 1: Fast device discovery with early exit")
            
            # Use find_device_by_name for immediate response when device is available
            device = await asyncio.wait_for(
                BleakScanner.find_device_by_name(DEVICE_NAME, timeout=min(scan_timeout, 5.0)),
                timeout=min(scan_timeout, 5.0) + 1.0
            )
            
            if device:
                logger.info(f"✅ Found device (fast): {device.name} ({device.address})")
                return device.address
                
        except (asyncio.TimeoutError, Exception) as e:
            logger.debug(f"Phase 1 fast scan completed, no immediate match: {e}")
            
        try:
            # Phase 2: Comprehensive scan with partial name matching
            logger.debug("Phase 2: Comprehensive device scan")
            
            # Adjust timeout for remaining time
            remaining_timeout = max(scan_timeout - 5.0, 2.0)
            
            devices = await asyncio.wait_for(
                BleakScanner.discover(timeout=remaining_timeout),
                timeout=remaining_timeout + 2.0
            )
            
            # Primary search: exact name match
            for device in devices:
                if device.name == DEVICE_NAME:
                    logger.info(f"✅ Found device: {device.name} ({device.address})")
                    return device.address
                    
            # Secondary search: partial name match (robust fallback)
            for device in devices:
                if device.name and "aRdent ScanPad" in device.name:
                    logger.info(f"✅ Found device (partial): {device.name} ({device.address})")
                    return device.address
            
            # Platform-specific additional searches
            if is_macos:
                # On macOS, also try searching by service UUID
                logger.debug("macOS: Searching by service UUID")
                for device in devices:
                    # Check if device advertises our service UUID
                    if hasattr(device, 'metadata') and device.metadata:
                        service_uuids = device.metadata.get('uuids', [])
                        if SERVICE_UUID.lower() in [uuid.lower() for uuid in service_uuids]:
                            logger.info(f"✅ Found device by service UUID: {device.address}")
                            return device.address
                            
            raise DeviceNotFoundError(f"No {DEVICE_NAME} device found in {len(devices)} scanned devices")
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"Device scan timed out after {scan_timeout}s")
        except Exception as e:
            raise ConnectionError(f"Error during device discovery: {e}")
    
    async def connect(self, address: Optional[str] = None, timeout: Optional[float] = None) -> None:
        """
        Connect to aRdent ScanPad device
        
        Args:
            address: Device address (auto-discovered if None)
            timeout: Connection timeout in seconds
            
        Raises:
            DeviceNotFoundError: If device not found
            ConnectionError: If connection fails
            TimeoutError: If connection times out
        """
        connect_timeout = timeout or self.timeout
        
        # Find device if address not provided
        if not address:
            address = await self.find_device(connect_timeout / 2)
            
        self.address = address
        logger.info(f"🔌 Connecting to {address}")
        
        try:
            self.client = BleakClient(address)
            
            # Connect with timeout
            await asyncio.wait_for(
                self.client.connect(),
                timeout=connect_timeout
            )
            
            if not self.client.is_connected:
                raise ConnectionError("Client reports not connected after connection attempt")
                
            logger.info(f"✅ Connected to {DEVICE_NAME}")
            self._connected = True
            
            # Discover and cache characteristics
            await self._discover_characteristics()
            
            # Setup disconnect callback for auto-reconnect (modern bleak API)
            if self.auto_reconnect and hasattr(self.client, 'set_disconnected_callback'):
                # Use old API if available for compatibility
                self.client.set_disconnected_callback(self._on_disconnect)
                
        except asyncio.TimeoutError:
            raise TimeoutError(f"Connection timed out after {connect_timeout}s")
        except Exception as e:
            self._connected = False
            if self.client:
                try:
                    await self.client.disconnect()
                except:
                    pass
                self.client = None
            raise ConnectionError(f"Failed to connect to device: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from device"""
        if self._reconnect_task:
            self._reconnect_task.cancel()
            self._reconnect_task = None
            
        self._connected = False
        
        if self.client and self.client.is_connected:
            logger.info("🔌 Disconnecting from device")
            try:
                await self.client.disconnect()
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
                
        self.client = None
        self.characteristics.clear()
        self._notification_handlers.clear()
        logger.info("✅ Disconnected from device")
    
    async def _discover_characteristics(self) -> None:
        """Discover and cache BLE characteristics"""
        if not self.client or not self.client.is_connected:
            raise ConnectionError("Not connected to device")
            
        logger.debug("🔍 Discovering characteristics")
        
        for name, uuid in CHAR_UUIDS.items():
            try:
                services = self.client.services
                for service in services:
                    for char in service.characteristics:
                        if char.uuid == uuid:
                            self.characteristics[name] = char
                            logger.debug(f"📡 Found characteristic: {name} ({uuid})")
                            break
                            
                if name not in self.characteristics:
                    logger.warning(f"⚠️ Characteristic not found: {name} ({uuid})")
                    
            except Exception as e:
                logger.warning(f"Error discovering characteristic {name}: {e}")
        
        logger.info(f"✅ Discovered {len(self.characteristics)} characteristics")
    
    def _on_disconnect(self, client: BleakClient) -> None:
        """Handle unexpected disconnection"""
        logger.warning("🔌 Device disconnected unexpectedly")
        self._connected = False
        
        if self.auto_reconnect and not self._reconnect_task:
            logger.info("🔄 Starting auto-reconnection")
            self._reconnect_task = asyncio.create_task(self._auto_reconnect())
    
    async def _auto_reconnect(self, max_attempts: int = 5) -> None:
        """Auto-reconnection loop"""
        attempt = 1
        
        while attempt <= max_attempts and not self._connected:
            try:
                logger.info(f"🔄 Reconnection attempt {attempt}/{max_attempts}")
                await asyncio.sleep(2.0 * attempt)  # Exponential backoff
                
                await self.connect(self.address, timeout=10.0)
                
                if self._connected:
                    logger.info("✅ Auto-reconnection successful")
                    return
                    
            except Exception as e:
                logger.warning(f"Reconnection attempt {attempt} failed: {e}")
                
            attempt += 1
        
        logger.error(f"❌ Auto-reconnection failed after {max_attempts} attempts")
        self._reconnect_task = None
    
    async def setup_notifications(self, handlers: Dict[str, Callable] = None) -> None:
        """
        Setup BLE notifications
        
        Args:
            handlers: Dictionary mapping characteristic names to handler functions
            
        Raises:
            NotificationError: If notification setup fails
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to device")
            
        handlers = handlers or {}
        
        # Setup notifications for response characteristics
        response_chars = ['config_response', 'device_response']
        
        for char_name in response_chars:
            if char_name in self.characteristics:
                try:
                    handler = handlers.get(char_name, self._default_notification_handler)
                    await self.client.start_notify(self.characteristics[char_name], handler)
                    self._notification_handlers[char_name] = handler
                    logger.debug(f"📬 Notifications enabled for {char_name}")
                    
                except Exception as e:
                    raise NotificationError(f"Failed to setup notifications for {char_name}: {e}")
        
        logger.info("✅ BLE notifications configured")
        
        # Clear response queues when notifications are setup
        self._received_device_responses = []
        self._received_config_responses = []
    
    def _default_notification_handler(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Default notification handler - handles responses like test_scripts_v2"""
        logger.debug(f"📬 Notification from {sender.uuid}: {data.hex()}")
        
        # Store responses based on characteristic like test_scripts_v2 ScanPadController
        char_uuid = str(sender.uuid).lower()
        
        # Device domain responses (LED, Buzzer, Device settings, OTA)
        if char_uuid == CHAR_UUIDS['device_response'].lower():
            self._received_device_responses.append(bytes(data))
            logger.debug(f"📥 Device response stored: {data.hex()}")
        
        # Config domain responses (Key/Button configuration)
        elif char_uuid == CHAR_UUIDS['config_response'].lower():
            self._received_config_responses.append(bytes(data))
            logger.debug(f"📥 Config response stored: {data.hex()}")
    
    @property
    def is_connected(self) -> bool:
        """Check if device is connected"""
        return self._connected and self.client and self.client.is_connected
    
    def get_characteristic(self, name: str) -> Optional[BleakGATTCharacteristic]:
        """Get characteristic by name"""
        return self.characteristics.get(name)
    
    async def write_char(self, char_name: str, data: bytes, response: bool = True) -> bool:
        """
        Write data to characteristic - MATCHES test_scripts_v2 BLEConnection.write_char
        
        Args:
            char_name: Characteristic name
            data: Data to write
            response: Whether to wait for response
            
        Returns:
            True if write successful, False otherwise
        """
        if not self.is_connected:
            logger.error("❌ Not connected to device")
            return False
            
        char = self.characteristics.get(char_name)
        if not char:
            logger.error(f"❌ Characteristic '{char_name}' not available")
            return False
            
        try:
            await self.client.write_gatt_char(char, data, response=response)
            logger.debug(f"✅ Written to {char_name}: {data.hex()}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Write failed to {char_name}: {e}")
            return False
    
    
    async def read_characteristic(self, char_name: str) -> bytes:
        """
        Read data from characteristic
        
        Args:
            char_name: Characteristic name
            
        Returns:
            Data read from characteristic
            
        Raises:
            ConnectionError: If not connected
            ValueError: If characteristic not found
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to device")
            
        char = self.characteristics.get(char_name)
        if not char:
            raise ValueError(f"Characteristic not found: {char_name}")
            
        try:
            data = await self.client.read_gatt_char(char)
            logger.debug(f"📥 Read from {char_name}: {data.hex()}")
            return data
            
        except Exception as e:
            raise ConnectionError(f"Failed to read from {char_name}: {e}")