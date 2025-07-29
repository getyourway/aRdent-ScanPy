"""
OTA Controller for aRdent ScanPad
Firmware update management with progress tracking
"""

import asyncio
import os
from typing import Optional, Dict, Any, Callable
import aiohttp
import logging

from .base import BaseController
from ..core.exceptions import OTAError, AuthenticationError, NetworkError


class OTAController:
    """
    OTA controller for firmware updates
    
    Provides:
    - Version checking
    - Firmware download from GitHub
    - Progress monitoring
    - Error handling
    """
    
    def __init__(self, device_controller):
        """
        Initialize OTA controller
        
        Args:
            device_controller: Parent PeripheralController instance
        """
        self.device = device_controller
        self.ota = device_controller.ota
        self._logger = logging.getLogger(__name__)
        
        # Default GitHub repository configuration
        self._github_repo = "getyourway/aRdent-ScanPad"
        self._github_api_base = "https://api.github.com"
        
    async def update_firmware(self,
                            api_token: Optional[str] = None,
                            firmware_url: Optional[str] = None,
                            progress_callback: Optional[Callable[[int, str], None]] = None,
                            verify_version: bool = True) -> Dict[str, Any]:
        """
        Execute complete firmware update process
        
        Args:
            api_token: GitHub Personal Access Token (uses ARDENT_OTA_API_KEY env var if not provided)
            firmware_url: Direct firmware URL (optional, auto-fetches latest if not provided)
            progress_callback: Function(progress: int, status: str) for progress updates
            verify_version: Check if update is needed before proceeding
            
        Returns:
            dict: Update result with keys:
                - success: bool
                - previous_version: str
                - new_version: str
                - duration: float (seconds)
                - error: str (if failed)
                
        Raises:
            OTAError: If update fails
            AuthenticationError: If GitHub authentication fails
            NetworkError: If network operations fail
        """
        import time
        start_time = time.time()
        
        # Get API token from parameter or environment
        token = api_token or os.environ.get('ARDENT_OTA_API_KEY')
        if not token and not firmware_url:
            raise AuthenticationError(
                "GitHub Personal Access Token required. "
                "Set ARDENT_OTA_API_KEY environment variable or provide api_token parameter."
            )
        
        result = {
            'success': False,
            'previous_version': None,
            'new_version': None,
            'duration': 0,
            'error': None
        }
        
        try:
            # Step 1: Get current version
            self._logger.info("Checking current firmware version...")
            current_version = await self.ota.check_version()
            if not current_version:
                raise OTAError("Failed to read current firmware version")
            
            result['previous_version'] = current_version
            
            # Step 2: Check for updates or use provided URL
            if not firmware_url:
                self._logger.info("Checking for available updates...")
                update_info = await self._check_github_updates(token, current_version)
                
                if verify_version and not update_info['update_available']:
                    self._logger.info(f"Firmware is up to date (v{current_version})")
                    result['success'] = True
                    result['new_version'] = current_version
                    result['duration'] = time.time() - start_time
                    return result
                
                firmware_url = update_info['download_url']
                result['new_version'] = update_info['latest_version']
                
            # Step 3: Download firmware (silently for now)
            self._logger.info("Downloading firmware...")
            firmware_data = await self._download_firmware(firmware_url, token)
            
            # Step 4: Start OTA process on device
            self._logger.info("Starting OTA service on device...")
            if not await self.ota.start():
                raise OTAError("Failed to start OTA service on device")
            
            # Step 4.5: Inform user to connect to WiFi (WiFi AP is creating in background)
            print("\n⚠️  IMPORTANT:")
            print("  1. Connect to WiFi network 'aRdent ScanPad'")
            print("  2. Password: none (open network)")
            print("  3. Device IP: 192.168.4.1")
            
            input("\n👆 Press Enter once connected to WiFi...")
            
            # Now we can start showing progress
            if progress_callback:
                progress_callback(10, "uploading")
            
            # Step 5: Upload firmware with monitoring
            self._logger.info("Uploading firmware to device...")
            upload_success = await self._upload_with_monitoring(
                firmware_data, 
                progress_callback
            )
            
            if not upload_success:
                raise OTAError("Firmware upload failed")
            
            result['success'] = True
            result['duration'] = time.time() - start_time
            
            self._logger.info(
                f"Firmware update completed successfully in {result['duration']:.1f}s"
            )
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            result['duration'] = time.time() - start_time
            self._logger.error(f"Firmware update failed: {e}")
            raise
    
    async def check_for_updates(self, api_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if firmware update is available
        
        Args:
            api_token: GitHub Personal Access Token
            
        Returns:
            dict: Update information with keys:
                - update_available: bool
                - current_version: str
                - latest_version: str
                - download_url: str
                - release_notes: str
                - published_at: str
        """
        # Get current version
        current_version = await self.ota.check_version()
        if not current_version:
            raise OTAError("Failed to read current firmware version")
        
        # Check GitHub for updates
        token = api_token or os.environ.get('ARDENT_OTA_API_KEY')
        if not token:
            raise AuthenticationError("GitHub Personal Access Token required")
        
        return await self._check_github_updates(token, current_version)
    
    async def get_update_status(self) -> Dict[str, Any]:
        """
        Get current update status
        
        Returns:
            dict: Current status with keys:
                - state: str ('idle', 'checking', 'downloading', 'installing', 'success', 'error')
                - progress: int (0-100)
                - message: str
        """
        status = await self.ota.get_status()
        
        # Map internal state to user-friendly message
        messages = {
            'idle': "No update in progress",
            'checking': "Checking firmware...",
            'downloading': f"Downloading firmware... {status['progress']}%",
            'installing': f"Installing firmware... {status['progress']}%",
            'success': "Update completed successfully",
            'error': "Update failed"
        }
        
        return {
            'state': status['state_name'],
            'progress': status['progress'],
            'message': messages.get(status['state_name'], "Unknown status")
        }
    
    async def _check_github_updates(self, token: str, current_version: str) -> Dict[str, Any]:
        """Check GitHub for available updates"""
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"{self._github_api_base}/repos/{self._github_repo}/releases/latest"
            
            async with session.get(url, headers=headers) as response:
                if response.status == 401:
                    raise AuthenticationError("Invalid GitHub Personal Access Token")
                elif response.status == 404:
                    raise NetworkError("Repository not found or no releases available")
                elif response.status != 200:
                    raise NetworkError(f"GitHub API error: {response.status}")
                
                data = await response.json()
                
                # Find firmware asset
                firmware_asset = None
                for asset in data.get('assets', []):
                    if asset['name'] == 'ble_hid.bin':
                        firmware_asset = asset
                        break
                
                if not firmware_asset:
                    raise OTAError("Firmware file not found in release")
                
                latest_version = data['tag_name']
                
                return {
                    'update_available': latest_version != current_version,
                    'current_version': current_version,
                    'latest_version': latest_version,
                    'download_url': firmware_asset['url'],
                    'release_notes': data.get('body', ''),
                    'published_at': data.get('published_at', '')
                }
    
    async def _download_firmware(self, url: str, token: Optional[str]) -> bytes:
        """Download firmware from URL"""
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
            headers['Accept'] = 'application/octet-stream'
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise NetworkError(f"Failed to download firmware: HTTP {response.status}")
                
                firmware_data = await response.read()
                
                # Verify ESP32 magic byte
                if not firmware_data or firmware_data[0] != 0xE9:
                    raise OTAError("Invalid firmware file (ESP32 magic byte check failed)")
                
                self._logger.info(f"Downloaded firmware: {len(firmware_data):,} bytes")
                return firmware_data
    
    async def _upload_with_monitoring(self, 
                                    firmware_data: bytes,
                                    progress_callback: Optional[Callable[[int, str], None]]) -> bool:
        """Upload firmware with progress monitoring"""
        upload_done = False
        ota_success = False
        
        async def monitor_progress():
            """Monitor OTA progress via BLE"""
            nonlocal ota_success
            last_progress = -1
            
            while not upload_done:
                try:
                    status = await self.ota.get_status()
                    progress = status['progress']
                    state_name = status['state_name']
                    
                    # Update progress if changed
                    if progress != last_progress:
                        last_progress = progress
                        if progress_callback:
                            progress_callback(progress, state_name)
                        
                        if state_name == 'success':
                            ota_success = True
                            break
                        elif state_name == 'error':
                            break
                    
                    await asyncio.sleep(1.0)
                    
                except Exception:
                    # Connection may be lost during reboot
                    if upload_done:
                        ota_success = True
                    break
            
            return ota_success
        
        async def upload_firmware():
            """Upload firmware via HTTP"""
            nonlocal upload_done
            
            try:
                async with aiohttp.ClientSession() as session:
                    data = aiohttp.FormData()
                    data.add_field('firmware',
                                 firmware_data,
                                 filename='firmware.bin',
                                 content_type='application/octet-stream')
                    
                    async with session.post('http://192.168.4.1/firmware',
                                          data=data,
                                          timeout=aiohttp.ClientTimeout(total=300)) as response:
                        
                        upload_done = True
                        return response.status == 200
                        
            except Exception as e:
                upload_done = True
                self._logger.error(f"Upload error: {e}")
                return False
        
        # Start monitoring first
        monitor_task = asyncio.create_task(monitor_progress())
        
        # Wait a moment for monitoring to start
        await asyncio.sleep(1.0)
        
        # Start upload
        upload_task = asyncio.create_task(upload_firmware())
        
        # Wait for both tasks
        upload_result, monitor_result = await asyncio.gather(
            upload_task, monitor_task, return_exceptions=True
        )
        
        if isinstance(upload_result, Exception):
            raise OTAError(f"Upload failed: {upload_result}")
        
        return upload_result and (ota_success or upload_done)