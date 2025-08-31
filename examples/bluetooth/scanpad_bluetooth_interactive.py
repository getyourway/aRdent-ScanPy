#!/usr/bin/env python3
"""
ScanPad Interactive Terminal - Comprehensive device testing and configuration
A complete interactive demonstration of all aRdent ScanPad features
"""

import asyncio
import sys
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import common utilities
from common import (
    InteractiveBase, JSONBrowser,
    confirm, get_int_input, get_text_input, get_choice_input,
    pause_for_user, display_menu, get_menu_choice
)

from ardent_scanpad import ScanPad
from ardent_scanpad.core.exceptions import (
    ConfigurationError, InvalidParameterError, TimeoutError,
    AuthenticationError, NetworkError, OTAError
)
from ardent_scanpad.utils.constants import (
    KeyIDs, KeyTypes, HIDKeyCodes, HIDModifiers, ConsumerCodes,
    DeviceOrientations, KeyboardLayouts, LEDs
)


class ScanPadInteractive(InteractiveBase):
    """Interactive terminal application for comprehensive ScanPad testing"""
    
    def __init__(self):
        super().__init__(
            "🎮 aRdent ScanPad Interactive Terminal",
            "Comprehensive device testing and configuration tool"
        )
        self.scanpad: Optional[ScanPad] = None
        self.device_info: Dict = {}
        self.key_configs: Dict = {}
        self.pending_key_configs: Dict = {}  # For batch configuration
        self.json_browser = JSONBrowser()  # For loading JSON configurations
        
    async def run(self):
        """Main entry point"""
        self.print_header()  # Use base class method
        
        # Connect to device
        if not await self._connect_to_device():
            return
        
        # Get and display device snapshot
        await self._display_device_snapshot()
        
        # Enter interactive mode
        await self._interactive_menu()
        
        # Cleanup
        await self._disconnect()
    
    async def _connect_to_device(self) -> bool:
        """Interactive device selection and connection"""
        print("🔍 DEVICE CONNECTION")
        print("="*70)
        
        return await self._device_selection_menu()
    
    async def _device_selection_menu(self) -> bool:
        """Interactive device selection with multiple connection options"""
        while True:
            print("\n📋 CONNECTION OPTIONS:")
            print("1. 🚀 Quick connect (auto-discover first device)")
            print("2. 🔍 Scan and select device (5s scan)") 
            print("3. 📍 Connect to specific address")
            print("4. 🏷️  Connect by device name")
            print("6. ⚡ Fast scan (2s timeout)")
            print("5. ❌ Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == "1":
                return await self._quick_connect()
            elif choice == "2":
                return await self._scan_and_select()
            elif choice == "3":
                return await self._connect_by_address()
            elif choice == "4": 
                return await self._connect_by_name()
            elif choice == "6":
                return await self._fast_scan_and_select()
            elif choice == "5":
                print("👋 Goodbye!")
                return False
            else:
                print("❌ Invalid choice. Please select 1-6.")
    
    async def _quick_connect(self) -> bool:
        """Quick connection to first available device"""
        print("\n🚀 Quick Connect Mode")
        print("-" * 30)
        print("🔍 Auto-discovering first available aRdent ScanPad...")
        
        try:
            self.scanpad = ScanPad()  # Auto-discovery mode
            await self.scanpad.connect(timeout=15.0)
            
            # Get device info for confirmation
            info = self.scanpad.device_info
            if info:
                print(f"✅ Connected to: {info['name']}")
                print(f"   📍 Address: {info['address']}")
                # connected_at is available in device_info property
                connected_time = info.get('connected_at', 'Unknown')
                if connected_time != 'Unknown':
                    # Format the ISO timestamp to be more readable
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(connected_time)
                        connected_time = dt.strftime("%H:%M:%S")
                    except:
                        pass
                print(f"   🕒 Connected at: {connected_time}")
            else:
                print("✅ Connected successfully!")
            
            return True
            
        except Exception as e:
            print(f"❌ Quick connect failed: {e}")
            print("💡 Tip: Try 'Scan and select' to see available devices")
            return False
    
    async def _scan_and_select(self) -> bool:
        """Scan for devices and let user select"""
        print("\n🔍 Scan and Select Mode")
        print("-" * 30)
        print("📡 Scanning for aRdent ScanPad devices...")
        
        try:
            # Discover devices with faster timeout
            devices = await ScanPad.discover_devices(timeout=5.0, debug=False)
            
            if not devices:
                print("❌ No aRdent ScanPad devices found")
                print("💡 Make sure your device is powered on and in range")
                return False
            
            print(f"\n📱 Found {len(devices)} device(s):")
            print("-" * 50)
            
            # Display devices with selection numbers
            for i, device in enumerate(devices, 1):
                rssi = device['rssi']
                signal_strength = "📶📶📶" if rssi > -50 else "📶📶" if rssi > -70 else "📶"
                
                print(f"{i}. {device['name']}")
                print(f"   📍 Address: {device['address']}")
                print(f"   📶 Signal: {rssi} dBm {signal_strength}")
                print(f"   🕒 Discovered: {device['discovered_at']}")
                print()
            
            # Let user select device
            while True:
                try:
                    choice = input(f"Select device (1-{len(devices)}) or 'b' for back: ").strip().lower()
                    
                    if choice == 'b':
                        return False
                    
                    device_index = int(choice) - 1
                    if 0 <= device_index < len(devices):
                        selected_device = devices[device_index]
                        break
                    else:
                        print(f"❌ Please enter a number between 1 and {len(devices)}")
                        
                except ValueError:
                    print("❌ Please enter a valid number or 'b' for back")
            
            # Connect to selected device
            print(f"\n🔗 Connecting to {selected_device['name']}...")
            print(f"   📍 Address: {selected_device['address']}")
            
            self.scanpad = ScanPad(device_address=selected_device['address'])
            await self.scanpad.connect(timeout=15.0)
            
            print("✅ Connected successfully!")
            
            # Show updated device info  
            info = await self.scanpad.fetch_device_info()
            if 'battery_level' in info:
                print(f"🔋 Battery: {info['battery_level']}%")
            if 'firmware_version' in info:
                print(f"💻 Firmware: {info['firmware_version']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Scan and select failed: {e}")
            return False
    
    async def _connect_by_address(self) -> bool:
        """Connect to device by specific BLE address"""
        print("\n📍 Connect by Address Mode")
        print("-" * 30)
        
        # Show example format
        print("💡 BLE address format examples:")
        print("   macOS/iOS: 12DE9829-AEC9-E5CD-89AE-10F5CF54DCC9")
        print("   Windows/Linux: AA:BB:CC:DD:EE:FF")
        
        address = input("\nEnter device BLE address: ").strip()
        
        if not address:
            print("❌ No address entered")
            return False
        
        print(f"\n🔗 Connecting to {address}...")
        
        try:
            # Quick availability check first
            print("🔍 Checking device availability...")
            is_available = await ScanPad.is_device_available(address, timeout=2.0)
            
            if not is_available:
                print("⚠️  Device not found or not advertising")
                proceed = input("Continue anyway? (y/n): ").strip().lower()
                if proceed != 'y':
                    return False
            
            self.scanpad = ScanPad(device_address=address)
            await self.scanpad.connect(timeout=15.0)
            
            print("✅ Connected successfully!")
            
            # Show device info
            info = self.scanpad.device_info
            if info:
                print(f"📱 Device: {info['name']}")
                # connected_at is available in device_info property
                connected_time = info.get('connected_at', 'Unknown')
                if connected_time != 'Unknown':
                    # Format the ISO timestamp to be more readable
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(connected_time)
                        connected_time = dt.strftime("%H:%M:%S")
                    except:
                        pass
                print(f"🕒 Connected at: {connected_time}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection by address failed: {e}")
            return False
    
    async def _connect_by_name(self) -> bool:
        """Connect to device by name pattern"""
        print("\n🏷️  Connect by Name Mode")
        print("-" * 30)
        
        print("💡 Examples: 'aRdent ScanPad', 'ScanPad-1234', 'ScanPad'")
        
        name_pattern = input("\nEnter device name or pattern: ").strip()
        
        if not name_pattern:
            print("❌ No name entered")
            return False
        
        print(f"\n🔗 Looking for device with name containing '{name_pattern}'...")
        
        try:
            self.scanpad = ScanPad(device_name=name_pattern)
            await self.scanpad.connect(timeout=15.0)
            
            print("✅ Connected successfully!")
            
            # Show which device was found
            info = self.scanpad.device_info
            if info:
                print(f"📱 Found device: {info['name']}")
                print(f"📍 Address: {info['address']}")
                # connected_at is available in device_info property
                connected_time = info.get('connected_at', 'Unknown')
                if connected_time != 'Unknown':
                    # Format the ISO timestamp to be more readable
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(connected_time)
                        connected_time = dt.strftime("%H:%M:%S")
                    except:
                        pass
                print(f"🕒 Connected at: {connected_time}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection by name failed: {e}")
            print("💡 Tip: Try 'Scan and select' to see available device names")
            return False
    
    async def _fast_scan_and_select(self) -> bool:
        """Fast scan with reduced timeout for quick discovery"""
        print("\n⚡ Fast Scan Mode")
        print("-" * 30)
        print("📡 Quick scanning for aRdent ScanPad devices (2s timeout)...")
        
        try:
            # Fast discovery with short timeout
            devices = await ScanPad.discover_devices(timeout=2.0, debug=False)
            
            if not devices:
                print("❌ No aRdent ScanPad devices found in fast scan")
                print("💡 Try normal scan (option 2) for slower devices")
                return False
            
            print(f"\n📱 Found {len(devices)} device(s) quickly:")
            print("-" * 50)
            
            # Display devices with selection numbers (same as normal scan)
            for i, device in enumerate(devices, 1):
                rssi = device['rssi']
                signal_strength = "📶📶📶" if rssi > -50 else "📶📶" if rssi > -70 else "📶"
                
                print(f"{i}. {device['name']} ⚡")
                print(f"   📍 Address: {device['address']}")
                print(f"   📶 Signal: {rssi} dBm {signal_strength}")
                print()
            
            # Let user select device
            while True:
                try:
                    choice = input(f"Select device (1-{len(devices)}) or 'b' for back: ").strip().lower()
                    
                    if choice == 'b':
                        return False
                    
                    device_index = int(choice) - 1
                    if 0 <= device_index < len(devices):
                        selected_device = devices[device_index]
                        break
                    else:
                        print(f"❌ Please enter a number between 1 and {len(devices)}")
                        
                except ValueError:
                    print("❌ Please enter a valid number or 'b' for back")
            
            # Connect to selected device (fast connection)
            print(f"\n🔗 Quick connecting to {selected_device['name']}...")
            print(f"   📍 Address: {selected_device['address']}")
            
            self.scanpad = ScanPad(device_address=selected_device['address'])
            await self.scanpad.connect(timeout=8.0)  # Faster connection timeout
            
            print("✅ Connected successfully!")
            
            # Show basic device info quickly 
            info = self.scanpad.device_info
            if info:
                print(f"📱 Device: {info['name']}")
                # connected_at is available in device_info property
                connected_time = info.get('connected_at', 'Unknown')
                if connected_time != 'Unknown':
                    # Format the ISO timestamp to be more readable
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(connected_time)
                        connected_time = dt.strftime("%H:%M:%S")
                    except:
                        pass
                print(f"🕒 Connected at: {connected_time}")
            
            return True
            
        except Exception as e:
            print(f"❌ Fast scan failed: {e}")
            print("💡 Try normal scan (option 2) for more reliable discovery")
            return False
    
    async def _display_device_snapshot(self):
        """Display comprehensive device information using new device_info property"""
        print("\n📊 DEVICE SNAPSHOT")
        print("="*70)
        
        # Use new comprehensive device info
        try:
            print("🔄 Fetching comprehensive device information...")
            device_info = await self.scanpad.fetch_device_info()
            self.device_info = device_info
            
            print("\n📱 Device Information:")
            print("-" * 30)
            print(f"Name: {device_info.get('name', 'Unknown')}")
            print(f"Address: {device_info.get('address', 'Unknown')}")
            print(f"Manufacturer: {device_info.get('manufacturer', 'Unknown')}")
            print(f"Firmware: {device_info.get('firmware_version', 'Unknown')}")
            print(f"Hardware: {device_info.get('hardware_version', 'Unknown')}")
            print(f"Serial: {device_info.get('serial_number', 'Unknown')}")
            # connected_at is available in device_info property
            connected_time = device_info.get('connected_at', 'Unknown')
            if connected_time != 'Unknown':
                # Format the ISO timestamp to be more readable
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(connected_time)
                    connected_time = dt.strftime("%H:%M:%S")
                except:
                    pass
            print(f"Connected: {connected_time}")
            
            # Battery info
            battery_level = device_info.get('battery_level')
            if battery_level is not None:
                print(f"\n🔋 Battery Status:")
                print("-" * 30)
                print(f"Level: {battery_level}%")
                
                battery_voltage = device_info.get('battery_voltage')
                if battery_voltage:
                    print(f"Voltage: {battery_voltage}V")
                    
                battery_charging = device_info.get('battery_charging')
                if battery_charging is not None:
                    charging_status = "Yes" if battery_charging else "No"
                    print(f"Charging: {charging_status}")
            
            # Device settings
            current_language = device_info.get('current_language')
            current_orientation = device_info.get('current_orientation')
            
            if current_language or current_orientation:
                print(f"\n⚙️  Current Settings:")
                print("-" * 30)
                if current_language:
                    print(f"Language: {current_language}")
                if current_orientation:
                    print(f"Orientation: {current_orientation}")
            
            # Connection info
            connection_rssi = device_info.get('connection_rssi')
            if connection_rssi:
                print(f"\n📶 Connection:")
                print("-" * 30)  
                print(f"RSSI: {connection_rssi} dBm")
                
        except Exception as e:
            print(f"⚠️  Could not retrieve comprehensive device info: {e}")
            # Fallback to basic info
            basic_info = self.scanpad.device_info
            if basic_info:
                print(f"\n📱 Basic Device Information:")
                print("-" * 30)
                for key, value in basic_info.items():
                    print(f"{key}: {value}")
        
        # 4. LED States (Optimized with bulk retrieval)
        print("\n💡 LED States:")
        print("-" * 30)
        try:
            # Use new optimized bulk LED state retrieval (1 BLE call instead of 5)
            led_states = await self.scanpad.device.led.get_all_states()
            
            # Logical LED names for display (clean API)
            led_names = {
                'led1_green': "LED Position 1 (Green)",
                'led2_red': "LED Position 2 (Red Component)", 
                'led2_green': "LED Position 2 (Green Component)",
                'led2_blue': "LED Position 2 (Blue Component)",
                'led3_green': "LED Position 3 (Green)"
            }
            
            for led_id, state in led_states.items():
                led_name = led_names.get(led_id, f"Unknown LED {led_id}")
                status = "ON ✅" if state else "OFF ⬜"
                print(f"  {led_name}: {status}")
                
        except Exception as e:
            print(f"⚠️  Could not retrieve LED states: {e}")
            print("  (Use LED Control menu for individual LED states)")
        
        # 5. Key Configuration Summary
        print("\n⌨️  Key Configuration Summary:")
        print("-" * 30)
        try:
            all_configs = await self.scanpad.keys.get_all_configs()
            self.key_configs = all_configs
            
            configured_count = len(all_configs)
            total_actions = sum(config.get('action_count', 0) for config in all_configs.values())
            
            print(f"Configured Keys: {configured_count}/20")
            print(f"Total Actions: {total_actions}")
            
            # Show first few configured keys
            if configured_count > 0:
                print("\nConfigured keys:")
                for i, (key_id, config) in enumerate(list(all_configs.items())[:5]):
                    key_name = KeyIDs.NAMES.get(key_id, f"Key {key_id}")
                    action_count = config.get('action_count', 0)
                    enabled = "✓" if config.get('enabled', False) else "✗"
                    print(f"  {enabled} {key_name}: {action_count} action(s)")
                
                if configured_count > 5:
                    print(f"  ... and {configured_count - 5} more")
                    
        except Exception as e:
            print(f"⚠️  Could not retrieve key configurations: {e}")
        
        print("\n" + "="*70 + "\n")
    
    async def _interactive_menu(self):
        """Main interactive menu"""
        while True:
            print("\n🎮 MAIN MENU")
            print("-" * 30)
            print("1. 🔧 Peripheral Control (LEDs, Buzzer, etc.)")
            print("2. ⌨️  Key Configuration")
            print("3. ⚙️  Device Settings")
            print("4. 📋 JSON Commands (Device & Keyboard)")
            print("5. 📊 Refresh Device Snapshot")
            print("6. 🔄 Factory Reset")
            print("7. 🎯 OTA Update")
            print("0. 🚪 Exit")
            
            choice = input("\nSelect option (0-7): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                await self._peripheral_menu()
            elif choice == '2':
                await self._key_configuration_menu()
            elif choice == '3':
                await self._device_settings_menu()
            elif choice == '4':
                await self._json_commands_menu()
            elif choice == '5':
                await self._display_device_snapshot()
            elif choice == '6':
                await self._factory_reset()
            elif choice == '7':
                await self._ota_update()
            else:
                print("❌ Invalid choice")
    
    async def _peripheral_menu(self):
        """Peripheral control submenu"""
        while True:
            print("\n🔧 PERIPHERAL CONTROL")
            print("-" * 30)
            print("1. 💡 LED Control")
            print("2. 🔊 Buzzer Control")
            print("3. 🔋 Battery Info")
            print("0. ⬅️  Back to Main Menu")
            
            choice = input("\nSelect option (0-3): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                await self._led_control_menu()
            elif choice == '2':
                await self._buzzer_control_menu()
            elif choice == '3':
                await self._battery_info()
            else:
                print("❌ Invalid choice")
    
    async def _led_control_menu(self):
        """LED control submenu"""
        while True:
            print("\n💡 LED CONTROL")
            print("-" * 30)
            print("1. Turn LED ON (LEDs 1-2)")
            print("2. Turn LED OFF (LEDs 1-2)")
            print("3. Blink LED")
            print("4. Set RGB Color (Red/Green/Blue/Yellow/Cyan/Magenta/White)")
            print("5. Show All LED States")
            print("6. All LEDs ON")
            print("7. All LEDs OFF")
            print("0. ⬅️  Back")
            
            choice = input("\nSelect option (0-7): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                await self._led_on()
            elif choice == '2':
                await self._led_off()
            elif choice == '3':
                await self._led_blink()
            elif choice == '4':
                await self._led_rgb()
            elif choice == '5':
                await self._show_led_states()
            elif choice == '6':
                await self._all_leds_on()
            elif choice == '7':
                await self._all_leds_off()
            else:
                print("❌ Invalid choice")
    
    async def _led_on(self):
        """Turn specific LED on"""
        print("\n💡 Available LEDs:")
        print("1-2: Individual Green LEDs")
        print("3-9: RGB Color Modes (Red/Green/Blue/Yellow/Cyan/Magenta/White)")
        led_id = input("Enter LED ID (1-9): ").strip()
        try:
            led_id = int(led_id)  # Keep 1-based for API
            if 1 <= led_id <= 9:
                await self.scanpad.device.led.turn_on(led_id)
                print(f"✅ LED {led_id} turned ON")
            else:
                print("❌ Invalid LED ID (must be 1-9)")
        except ValueError:
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def _led_off(self):
        """Turn specific LED off"""
        print("\n💡 Available LEDs:")
        print("1-2: Individual Green LEDs")
        print("3-9: RGB Color Modes (Red/Green/Blue/Yellow/Cyan/Magenta/White)")
        led_id = input("Enter LED ID (1-9): ").strip()
        try:
            led_id = int(led_id)  # Keep 1-based for API
            if 1 <= led_id <= 9:
                await self.scanpad.device.led.turn_off(led_id)
                print(f"✅ LED {led_id} turned OFF")
            else:
                print("❌ Invalid LED ID (must be 1-9)")
        except ValueError:
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def _led_blink(self):
        """Blink specific LED"""
        print("\n💡 Available LEDs:")
        print("1-2: Individual Green LEDs")
        print("3-9: RGB Color Modes (Red/Green/Blue/Yellow/Cyan/Magenta/White)")
        led_id = input("Enter LED ID (1-9): ").strip()
        frequency = input("Enter blink frequency (0.1-20.0 Hz): ").strip()
        
        try:
            led_id = int(led_id)  # Keep 1-based for API
            frequency = float(frequency)
            
            if 1 <= led_id <= 9 and 0.1 <= frequency <= 20.0:
                await self.scanpad.device.led.blink(led_id, frequency)
                print(f"✅ LED {led_id} blinking at {frequency} Hz")
            else:
                print("❌ Invalid LED ID (1-9) or frequency (0.1-20.0)")
        except ValueError:
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def _led_rgb(self):
        """Set RGB LED color using ESP32 RGB LED IDs"""
        print("\n🎨 RGB Color Selection:")
        print("1. Red (LED 3)")
        print("2. Green (LED 4)")
        print("3. Blue (LED 5)")
        print("4. Yellow (LED 6)")
        print("5. Cyan (LED 7)")
        print("6. Magenta (LED 8)")
        print("7. White (LED 9)")
        
        choice = input("\nSelect color (1-7): ").strip()
        
        rgb_led_ids = {
            '1': 3,  # Red
            '2': 4,  # Green
            '3': 5,  # Blue
            '4': 6,  # Yellow
            '5': 7,  # Cyan
            '6': 8,  # Magenta
            '7': 9,  # White
        }
        
        try:
            if choice in rgb_led_ids:
                led_id = rgb_led_ids[choice]
                await self.scanpad.device.led.turn_on(led_id)
                print(f"✅ RGB LED {led_id} turned ON")
            else:
                print("❌ Invalid choice")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def _show_led_states(self):
        """Show all LED states"""
        try:
            # LED names from constants.py (1-based IDs)
            led_names = {
                1: "Green LED 1 (GPIO7)",
                2: "Green LED 2 (GPIO15)", 
                3: "RGB Red Mode",
                4: "RGB Green Mode",
                5: "RGB Blue Mode",
                6: "RGB Yellow Mode",
                7: "RGB Cyan Mode",
                8: "RGB Magenta Mode",
                9: "RGB White Mode"
            }
            
            print("\n💡 Current LED States:")
            for led_id in range(1, 10):  # LED IDs 1-9
                try:
                    state = await self.scanpad.device.led.get_state(led_id)
                    led_name = led_names.get(led_id, f"LED {led_id}")
                    status = "ON ✅" if state else "OFF ⬜"
                    print(f"  {led_name}: {status}")
                except Exception as e:
                    print(f"  LED {led_id}: ERROR ❌ ({e})")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def _all_leds_on(self):
        """Turn all LEDs on"""
        try:
            # Turn on all LEDs individually since all_on doesn't exist
            for led_id in range(1, 6):
                try:
                    await self.scanpad.device.led.turn_on(led_id)
                except:
                    pass
            print("✅ All LEDs turned ON")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def _all_leds_off(self):
        """Turn all LEDs off"""
        try:
            await self.scanpad.device.led.all_off()
            print("✅ All LEDs turned OFF")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def _buzzer_control_menu(self):
        """Buzzer control submenu"""
        while True:
            print("\n🔊 BUZZER CONTROL")
            print("-" * 30)
            print("1. Single Beep")
            print("2. Multiple Beeps")
            print("3. Play Melody")
            print("4. Set Volume")
            print("0. ⬅️  Back")
            
            choice = input("\nSelect option (0-4): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                await self._buzzer_beep()
            elif choice == '2':
                await self._buzzer_multiple()
            elif choice == '3':
                await self._buzzer_melody()
            elif choice == '4':
                await self._buzzer_volume()
            else:
                print("❌ Invalid choice")
    
    async def _buzzer_beep(self):
        """Single beep"""
        try:
            await self.scanpad.device.buzzer.beep()
            print("✅ Beep sent")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def _buzzer_multiple(self):
        """Multiple beeps"""
        count = input("Enter number of beeps (1-10): ").strip()
        try:
            count = int(count)
            if 1 <= count <= 10:
                # Multiple beeps using a loop since beep_multiple doesn't exist
                for i in range(count):
                    await self.scanpad.device.buzzer.beep()
                    if i < count - 1:  # Don't wait after the last beep
                        await asyncio.sleep(0.3)
                print(f"✅ {count} beeps sent")
            else:
                print("❌ Invalid count (must be 1-10)")
        except ValueError:
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def _buzzer_melody(self):
        """Play melody"""
        print("\n🎵 Select Melody:")
        print("1. Success")
        print("2. Error")
        print("3. Warning")
        print("4. Notification")
        
        choice = input("\nSelect melody (1-4): ").strip()
        
        try:
            melodies = {
                '1': 'success',
                '2': 'error',
                '3': 'warning',
                '4': 'notification'
            }
            
            if choice in melodies:
                await self.scanpad.device.buzzer.play_melody(melodies[choice])
                print(f"✅ Playing {melodies[choice]} melody")
            else:
                print("❌ Invalid choice")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def _buzzer_volume(self):
        """Set buzzer volume"""
        volume = input("Enter volume (0-100): ").strip()
        try:
            volume = int(volume)
            if 0 <= volume <= 100:
                await self.scanpad.device.buzzer.set_volume(volume)
                print(f"✅ Volume set to {volume}%")
            else:
                print("❌ Invalid volume (must be 0-100)")
        except ValueError:
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def _battery_info(self):
        """Display detailed battery information"""
        try:
            print("\n🔋 BATTERY INFORMATION")
            print("-" * 30)
            
            # Basic level
            level = await self.scanpad.device.get_battery_level()
            print(f"Battery Level: {level}%")
            
            # Detailed info if available
            try:
                details = await self.scanpad.device.get_battery_status()
                print(f"Voltage: {details.get('voltage', 'N/A')}V")
                print(f"Current: {details.get('current', 'N/A')}mA")
                print(f"Temperature: {details.get('temperature', 'N/A')}°C")
                print(f"Charging: {'Yes' if details.get('is_charging', False) else 'No'}")
                print(f"Time to Empty: {details.get('time_to_empty', 'N/A')} min")
                print(f"Time to Full: {details.get('time_to_full', 'N/A')} min")
            except:
                print("Detailed battery info not available")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    async def _key_configuration_menu(self):
        """Key configuration submenu"""
        while True:
            print("\n⌨️  KEY CONFIGURATION")
            print("-" * 30)
            print("1. 📋 View All Key Configurations")
            print("2. 🔧 Configure Single Key")
            print("3. 🎯 Configure Multiple Keys (Batch)")
            print("4. 📄 Load Configuration from JSON File")
            print("5. 🗑️  Clear Key Configuration")
            print("6. 💾 Save Configuration to Device")
            print("7. 🏭 Factory Reset Keys")
            print("0. ⬅️  Back to Main Menu")
            
            choice = input("\nSelect option (0-7): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                await self._view_all_keys()
            elif choice == '2':
                await self._configure_single_key()
            elif choice == '3':
                await self._configure_batch_keys()
            elif choice == '4':
                await self._load_json_configuration()
            elif choice == '5':
                await self._clear_key()
            elif choice == '6':
                await self._save_key_config()
            elif choice == '7':
                await self._factory_reset_keys()
            else:
                print("❌ Invalid choice")
    
    async def _view_all_keys(self):
        """View all key configurations"""
        try:
            all_configs = await self.scanpad.keys.get_all_configs()
            
            print("\n📋 ALL KEY CONFIGURATIONS")
            print("="*60)
            
            # Matrix keys
            print("\n🔢 Matrix Keys (4x4):")
            print("-" * 30)
            for row in range(4):
                for col in range(4):
                    key_id = row * 4 + col
                    config = all_configs.get(key_id, {})
                    if config:
                        enabled = "✓" if config.get('enabled', False) else "✗"
                        actions = config.get('action_count', 0)
                        print(f"[{row},{col}] {enabled} {actions} action(s)", end="  ")
                    else:
                        print(f"[{row},{col}] - Empty     ", end="  ")
                print()  # New line after each row
            
            # Button actions
            print("\n🔘 Button Actions:")
            print("-" * 30)
            button_ids = {
                16: "Scan Trigger Double",
                17: "Scan Trigger Long",
                18: "Power Single",
                19: "Power Double"
            }
            
            for key_id, name in button_ids.items():
                config = all_configs.get(key_id, {})
                if config:
                    enabled = "✓" if config.get('enabled', False) else "✗"
                    actions = config.get('action_count', 0)
                    print(f"{name}: {enabled} {actions} action(s)")
                else:
                    print(f"{name}: - Empty")
            
            # Show details for configured keys
            if all_configs:
                print("\n📝 Detailed Configurations:")
                print("-" * 30)
                
                view_all = input("\nView detailed info for all configured keys? (y/n): ").lower() == 'y'
                
                if view_all:
                    for key_id, config in all_configs.items():
                        await self._display_key_details(key_id, config)
                else:
                    key_input = input("Enter key to view (e.g., '0,0' for matrix or '18' for button): ").strip()
                    key_id = self._parse_key_input(key_input)
                    if key_id is not None and key_id in all_configs:
                        await self._display_key_details(key_id, all_configs[key_id])
                    else:
                        print("❌ Key not found or not configured")
                        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    async def _display_key_details(self, key_id: int, config: Dict):
        """Display detailed configuration for a key"""
        key_name = KeyIDs.NAMES.get(key_id, f"Key {key_id}")
        print(f"\n🔑 {key_name} (ID: {key_id}):")
        print(f"  Enabled: {'Yes' if config.get('enabled', False) else 'No'}")
        print(f"  Actions: {config.get('action_count', 0)}")
        
        # Debug: show raw config
        if config.get('action_count', 0) == 1:
            print(f"  Debug - Raw config: {config}")
        
        for i, action in enumerate(config.get('actions', [])):
            print(f"\n  Action {i + 1}:")
            action_type = action.get('type', 0)
            
            if action_type == KeyTypes.UTF8:
                # Try to decode UTF-8 text
                text = action.get('text', '')
                if not text and 'data' in action:
                    # Try to decode from data array
                    try:
                        data_bytes = bytes(action['data'][:action.get('data_len', 0)])
                        text = data_bytes.decode('utf-8')
                    except:
                        text = f"<Raw: {action['data']}>"
                print(f"    Type: UTF-8 Text")
                print(f"    Text: '{text}'")
                
            elif action_type == KeyTypes.HID:
                print(f"    Type: HID Key")
                print(f"    Key Code: {action.get('value', 0)} (0x{action.get('value', 0):02X})")
                
                # Show modifier keys
                mask = action.get('mask', 0)
                if mask:
                    mods = []
                    if mask & HIDModifiers.LEFT_CTRL: mods.append("Ctrl")
                    if mask & HIDModifiers.LEFT_SHIFT: mods.append("Shift")
                    if mask & HIDModifiers.LEFT_ALT: mods.append("Alt")
                    if mask & HIDModifiers.LEFT_GUI: mods.append("Win/Cmd")
                    print(f"    Modifiers: {'+'.join(mods)}")
                    
            elif action_type == KeyTypes.CONSUMER:
                print(f"    Type: Consumer Control")
                value = action.get('value', 0) | (action.get('mask', 0) << 8)
                print(f"    Control: {value} (0x{value:04X})")
                
            delay = action.get('delay', 0)
            if delay:
                print(f"    Delay: {delay}ms")
    
    def _parse_key_input(self, key_input: str) -> Optional[int]:
        """Parse key input (matrix notation or direct ID)"""
        key_input = key_input.strip()
        
        # Try direct ID first
        try:
            key_id = int(key_input)
            if 0 <= key_id <= 19:
                return key_id
        except ValueError:
            pass
        
        # Try matrix notation (row,col)
        if ',' in key_input:
            try:
                row, col = map(int, key_input.split(','))
                if 0 <= row <= 3 and 0 <= col <= 3:
                    return row * 4 + col
            except ValueError:
                pass
        
        return None
    
    async def _configure_single_key(self):
        """Configure a single key interactively"""
        print("\n🔧 CONFIGURE SINGLE KEY")
        print("-" * 30)
        
        # Select key
        print("\nKey Selection:")
        print("  Matrix: Enter as 'row,col' (e.g., '0,0' for top-left)")
        print("  Buttons: 16=Scan Double, 17=Scan Long, 18=Power Single")
        
        key_input = input("\nEnter key to configure: ").strip()
        key_id = self._parse_key_input(key_input)
        
        if key_id is None:
            print("❌ Invalid key")
            return
        
        key_name = KeyIDs.NAMES.get(key_id, f"Key {key_id}")
        print(f"\n📝 Configuring {key_name}")
        
        # Build actions
        actions = []
        while len(actions) < 10:  # Max 10 actions
            print(f"\nAction {len(actions) + 1} (or Enter to finish):")
            print("1. UTF-8 Text")
            print("2. HID Key")
            print("3. Consumer Control")
            print("4. Finish")
            
            choice = input("\nAction type (1-4): ").strip()
            
            if choice == '4' or not choice:
                break
            elif choice == '1':
                action = await self._create_utf8_action()
            elif choice == '2':
                action = await self._create_hid_action()
            elif choice == '3':
                action = await self._create_consumer_action()
            else:
                print("❌ Invalid choice")
                continue
            
            if action:
                actions.append(action)
                print(f"✅ Action {len(actions)} added")
        
        if not actions:
            print("❌ No actions configured")
            return
        
        # Preview configuration
        print(f"\n📋 Configuration Preview for {key_name}:")
        print(f"Total actions: {len(actions)}")
        for i, action in enumerate(actions):
            print(f"  {i + 1}. {self._action_summary(action)}")
        
        # Confirm and send
        if input("\nSend configuration? (y/n): ").lower() == 'y':
            try:
                success = await self.scanpad.keys.set_key_config(key_id, actions)
                if success:
                    print(f"✅ {key_name} configured successfully!")
                else:
                    print("❌ Configuration failed")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def _create_utf8_action(self) -> Optional[Dict]:
        """Create UTF-8 text action"""
        text = input("Enter text (max 8 bytes UTF-8): ").strip()
        if not text:
            return None
        
        delay = input("Delay after action (ms, default 0): ").strip()
        try:
            delay = int(delay) if delay else 0
        except ValueError:
            delay = 0
        
        return self.scanpad.keys.create_text_action(text, delay)
    
    async def _create_hid_action(self) -> Optional[Dict]:
        """Create HID key action"""
        print("\nCommon HID Keys:")
        print("  Letters: A=4, B=5, C=6... Z=29")
        print("  Numbers: 1=30, 2=31... 0=39")
        print("  Special: Enter=40, Esc=41, Backspace=42, Tab=43, Space=44")
        print("  Function: F1=58, F2=59... F12=69")
        print("  Arrows: Right=79, Left=80, Down=81, Up=82")
        
        key_code = input("\nEnter HID key code: ").strip()
        try:
            key_code = int(key_code)
        except ValueError:
            print("❌ Invalid key code")
            return None
        
        # Modifiers
        print("\nModifiers (combine with +):")
        print("  1=Ctrl, 2=Shift, 4=Alt, 8=Win/Cmd")
        print("  Example: 3 = Ctrl+Shift")
        print("  Common combinations: 3=Ctrl+Shift, 5=Ctrl+Alt, 6=Shift+Alt")
        
        modifiers = input("Enter modifiers (default 0): ").strip()
        try:
            # Handle mathematical expressions like "1+2"
            if modifiers and ('+' in modifiers or '-' in modifiers or '*' in modifiers):
                print(f"❌ Invalid input: '{modifiers}'")
                print("   Please enter the combined value directly (e.g., 3 for Ctrl+Shift)")
                print("   Don't use mathematical operators like '1+2'")
                return None
            modifiers = int(modifiers) if modifiers else 0
            if modifiers < 0 or modifiers > 255:
                print(f"❌ Modifier value {modifiers} out of range (0-255)")
                return None
        except ValueError:
            print(f"❌ Invalid modifier value: '{modifiers}'. Please enter a number.")
            return None
        
        delay = input("Delay after action (ms, default 0): ").strip()
        try:
            delay = int(delay) if delay else 0
        except ValueError:
            delay = 0
        
        return self.scanpad.keys.create_hid_action(key_code, modifiers, delay)
    
    async def _create_consumer_action(self) -> Optional[Dict]:
        """Create consumer control action"""
        print("\nCommon Consumer Controls:")
        print("  Volume: Up=233, Down=234, Mute=226")
        print("  Media: Play/Pause=205, Stop=183, Next=181, Previous=182")
        print("  System: Power=48, Sleep=50, Wake=51")
        
        control = input("\nEnter consumer control code: ").strip()
        try:
            control = int(control)
        except ValueError:
            print("❌ Invalid control code")
            return None
        
        delay = input("Delay after action (ms, default 0): ").strip()
        try:
            delay = int(delay) if delay else 0
        except ValueError:
            delay = 0
        
        return self.scanpad.keys.create_consumer_action(control, delay)
    
    def _action_summary(self, action: Dict) -> str:
        """Get summary description of an action"""
        action_type = action.get('type', 0)
        
        if action_type == KeyTypes.UTF8:
            text = action.get('text', '')
            return f"Text: '{text}'"
        elif action_type == KeyTypes.HID:
            key = action.get('value', 0)
            mods = action.get('mask', 0)
            desc = f"HID: {key}"
            if mods:
                mod_names = []
                if mods & HIDModifiers.LEFT_CTRL: mod_names.append("Ctrl")
                if mods & HIDModifiers.LEFT_SHIFT: mod_names.append("Shift")
                if mods & HIDModifiers.LEFT_ALT: mod_names.append("Alt")
                if mods & HIDModifiers.LEFT_GUI: mod_names.append("Win")
                desc = f"{'+'.join(mod_names)}+{desc}"
            return desc
        elif action_type == KeyTypes.CONSUMER:
            return f"Consumer: {action.get('value', 0)}"
        else:
            return "Unknown"
    
    async def _configure_batch_keys(self):
        """Configure multiple keys in batch mode"""
        print("\n🎯 BATCH KEY CONFIGURATION")
        print("-" * 30)
        print("Configure multiple keys, then send all at once")
        
        self.pending_key_configs = {}
        
        while True:
            print(f"\n📋 Pending configurations: {len(self.pending_key_configs)}")
            if self.pending_key_configs:
                for key_id in self.pending_key_configs:
                    key_name = KeyIDs.NAMES.get(key_id, f"Key {key_id}")
                    print(f"  - {key_name}")
            
            print("\nOptions:")
            print("1. Add key configuration")
            print("2. Add standard layout (1-9, arrows, ABCD)")
            print("3. View pending configurations")
            print("4. Send all (burst mode)")
            print("5. Send all (sequential)")
            print("6. Clear pending")
            print("0. Cancel and back")
            
            choice = input("\nSelect option (0-6): ").strip()
            
            if choice == '0':
                self.pending_key_configs.clear()
                break
            elif choice == '1':
                await self._add_batch_key()
            elif choice == '2':
                await self._add_standard_layout()
            elif choice == '3':
                self._view_pending_configs()
            elif choice == '4':
                await self._send_batch_burst()
                break
            elif choice == '5':
                await self._send_batch_sequential()
                break
            elif choice == '6':
                self.pending_key_configs.clear()
                print("✅ Pending configurations cleared")
            else:
                print("❌ Invalid choice")
    
    async def _add_batch_key(self):
        """Add a key to batch configuration"""
        key_input = input("\nEnter key to configure: ").strip()
        key_id = self._parse_key_input(key_input)
        
        if key_id is None:
            print("❌ Invalid key")
            return
        
        key_name = KeyIDs.NAMES.get(key_id, f"Key {key_id}")
        
        # Quick action input
        print(f"\nConfiguring {key_name}")
        print("Quick format: 'text:Hello' or 'hid:40' or 'consumer:233'")
        print("Or press Enter for detailed configuration")
        
        quick = input("\nQuick action: ").strip()
        
        if quick:
            actions = self._parse_quick_actions(quick)
            if actions:
                self.pending_key_configs[key_id] = actions
                print(f"✅ {key_name} added to batch")
        else:
            # Detailed configuration (reuse single key logic)
            # ... (similar to _configure_single_key but adds to pending)
            pass
    
    async def _add_standard_layout(self):
        """Add standard keypad layout (1-9, arrows, ABCD)"""
        print("\n🎹 STANDARD LAYOUT")
        print("-" * 30)
        print("This will configure:")
        print("  Row 0: [1] [2] [3] [A]")
        print("  Row 1: [4] [5] [6] [B]")
        print("  Row 2: [7] [8] [9] [C]")
        print("  Row 3: [←] [0] [→] [D]")
        
        if input("\nConfigure standard layout? (y/n): ").lower() != 'y':
            return
        
        # Define the standard layout mapping
        # Matrix position (row * 4 + col) -> action
        standard_layout = {
            # Row 0: 1, 2, 3, A
            0: self.scanpad.keys.create_text_action("1"),
            1: self.scanpad.keys.create_text_action("2"),
            2: self.scanpad.keys.create_text_action("3"),
            3: self.scanpad.keys.create_text_action("A"),
            
            # Row 1: 4, 5, 6, B
            4: self.scanpad.keys.create_text_action("4"),
            5: self.scanpad.keys.create_text_action("5"),
            6: self.scanpad.keys.create_text_action("6"),
            7: self.scanpad.keys.create_text_action("B"),
            
            # Row 2: 7, 8, 9, C
            8: self.scanpad.keys.create_text_action("7"),
            9: self.scanpad.keys.create_text_action("8"),
            10: self.scanpad.keys.create_text_action("9"),
            11: self.scanpad.keys.create_text_action("C"),
            
            # Row 3: Left Arrow, 0, Right Arrow, D
            12: self.scanpad.keys.create_hid_action(HIDKeyCodes.LEFT_ARROW),
            13: self.scanpad.keys.create_text_action("0"),
            14: self.scanpad.keys.create_hid_action(HIDKeyCodes.RIGHT_ARROW),
            15: self.scanpad.keys.create_text_action("D"),
        }
        
        # Add all keys to pending configurations
        added_count = 0
        for key_id, action in standard_layout.items():
            self.pending_key_configs[key_id] = [action]
            added_count += 1
        
        print(f"\n✅ Added {added_count} keys to pending configurations")
        print("Use 'Send all' to apply the layout to your device")
    
    def _parse_quick_actions(self, quick: str) -> Optional[List[Dict]]:
        """Parse quick action format"""
        parts = quick.split(':')
        if len(parts) != 2:
            return None
        
        action_type, value = parts
        action_type = action_type.lower()
        
        if action_type == 'text':
            return [self.scanpad.keys.create_text_action(value)]
        elif action_type == 'hid':
            try:
                key_code = int(value)
                return [self.scanpad.keys.create_hid_action(key_code)]
            except ValueError:
                return None
        elif action_type == 'consumer':
            try:
                control = int(value)
                return [self.scanpad.keys.create_consumer_action(control)]
            except ValueError:
                return None
        
        return None
    
    def _view_pending_configs(self):
        """View pending batch configurations"""
        if not self.pending_key_configs:
            print("\n❌ No pending configurations")
            return
        
        print("\n📋 PENDING CONFIGURATIONS")
        print("="*60)
        
        for key_id, actions in self.pending_key_configs.items():
            key_name = KeyIDs.NAMES.get(key_id, f"Key {key_id}")
            print(f"\n{key_name}:")
            for i, action in enumerate(actions):
                print(f"  {i + 1}. {self._action_summary(action)}")
    
    async def _send_batch_burst(self):
        """Send batch configurations in burst mode"""
        if not self.pending_key_configs:
            print("❌ No configurations to send")
            return
        
        print(f"\n🚀 Sending {len(self.pending_key_configs)} configurations in BURST mode...")
        
        try:
            # Use batch method if available
            # Otherwise, send rapidly without delays
            success_count = 0
            start_time = datetime.now()
            
            for key_id, actions in self.pending_key_configs.items():
                try:
                    if await self.scanpad.keys.set_key_config(key_id, actions):
                        success_count += 1
                except:
                    pass
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"✅ Sent {success_count}/{len(self.pending_key_configs)} configurations in {elapsed:.2f}s")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.pending_key_configs.clear()
    
    async def _send_batch_sequential(self):
        """Send batch configurations sequentially"""
        if not self.pending_key_configs:
            print("❌ No configurations to send")
            return
        
        print(f"\n📡 Sending {len(self.pending_key_configs)} configurations SEQUENTIALLY...")
        
        try:
            success_count = 0
            
            for key_id, actions in self.pending_key_configs.items():
                key_name = KeyIDs.NAMES.get(key_id, f"Key {key_id}")
                print(f"  Configuring {key_name}...", end='', flush=True)
                
                try:
                    if await self.scanpad.keys.set_key_config(key_id, actions):
                        print(" ✅")
                        success_count += 1
                    else:
                        print(" ❌")
                except Exception as e:
                    print(f" ❌ ({e})")
                
                # Small delay between configurations
                await asyncio.sleep(0.1)
            
            print(f"\n✅ Configured {success_count}/{len(self.pending_key_configs)} keys")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.pending_key_configs.clear()
    
    async def _clear_key(self):
        """Clear key configuration"""
        key_input = input("\nEnter key to clear: ").strip()
        key_id = self._parse_key_input(key_input)
        
        if key_id is None:
            print("❌ Invalid key")
            return
        
        key_name = KeyIDs.NAMES.get(key_id, f"Key {key_id}")
        
        if input(f"\nClear configuration for {key_name}? (y/n): ").lower() == 'y':
            try:
                success = await self.scanpad.keys.clear_key(key_id)
                if success:
                    print(f"✅ {key_name} cleared")
                else:
                    print("❌ Clear failed")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def _save_key_config(self):
        """Save key configuration to device"""
        if input("\nSave all key configurations to device memory? (y/n): ").lower() == 'y':
            try:
                success = await self.scanpad.keys.save_config()
                if success:
                    print("✅ Configuration saved to device")
                else:
                    print("❌ Save failed")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def _factory_reset_keys(self):
        """Factory reset all keys"""
        print("\n⚠️  WARNING: This will clear ALL key configurations!")
        if input("Are you sure? (yes/no): ").lower() == 'yes':
            try:
                success = await self.scanpad.keys.factory_reset()
                if success:
                    print("✅ All keys reset to factory defaults")
                else:
                    print("❌ Factory reset failed")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def _device_settings_menu(self):
        """Device settings submenu"""
        while True:
            print("\n⚙️  DEVICE SETTINGS")
            print("-" * 30)
            print("1. 🔄 Change Orientation")
            print("2. 🌐 Change Keyboard Layout")
            print("3. ⏰ Configure Auto-shutdown")
            print("4. 📄 Execute Device Commands from JSON")
            print("5. 📱 Device Information")
            print("0. ⬅️  Back to Main Menu")
            
            choice = input("\nSelect option (0-5): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                await self._change_orientation()
            elif choice == '2':
                await self._change_language()
            elif choice == '3':
                await self._configure_auto_shutdown()
            elif choice == '4':
                await self._load_json_device_commands()
            elif choice == '5':
                await self._show_device_info()
            else:
                print("❌ Invalid choice")
    
    async def _change_orientation(self):
        """Change device orientation"""
        print("\n🔄 CHANGE ORIENTATION")
        print("-" * 30)
        print("1. 0° (Normal)")
        print("2. 90° (Rotated Right)")
        print("3. 180° (Upside Down)")
        print("4. 270° (Rotated Left)")
        
        choice = input("\nSelect orientation (1-4): ").strip()
        
        orientations = {
            '1': DeviceOrientations.PORTRAIT,
            '2': DeviceOrientations.LANDSCAPE,
            '3': DeviceOrientations.REVERSE_PORTRAIT,
            '4': DeviceOrientations.REVERSE_LANDSCAPE
        }
        
        if choice in orientations:
            try:
                success = await self.scanpad.device.set_orientation(orientations[choice])
                if success:
                    print("✅ Orientation changed")
                else:
                    print("❌ Failed to change orientation")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("❌ Invalid choice")
    
    async def _change_language(self):
        """Change keyboard layout"""
        print("\n🌐 CHANGE KEYBOARD LAYOUT")
        print("-" * 30)
        print("1. US English (QWERTY)")
        print("2. French (AZERTY)")
        print("3. Spanish (QWERTY)")
        print("4. Italian (QWERTY)")
        print("5. German (QWERTZ)")
        print("6. UK English (QWERTY)")
        
        choice = input("\nSelect layout (1-6): ").strip()
        
        layouts = {
            '1': KeyboardLayouts.WIN_US_QWERTY,
            '2': KeyboardLayouts.WIN_FR_AZERTY,
            '3': KeyboardLayouts.WIN_ES_QWERTY,
            '4': KeyboardLayouts.WIN_IT_QWERTY,
            '5': KeyboardLayouts.WIN_DE_QWERTZ,
            '6': KeyboardLayouts.MAC_US_QWERTY
        }
        
        if choice in layouts:
            try:
                success = await self.scanpad.device.set_language(layouts[choice])
                if success:
                    print("✅ Keyboard layout changed")
                else:
                    print("❌ Failed to change layout")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("❌ Invalid choice")
    
    async def _configure_auto_shutdown(self):
        """Configure auto-shutdown settings"""
        print("\n⏰ CONFIGURE AUTO-SHUTDOWN")
        print("-" * 30)
        
        try:
            # Get current settings
            current = await self.scanpad.device.get_auto_shutdown()
            if current:
                print(f"Auto-shutdown enabled: {'Yes' if current.get('enabled', False) else 'No'}")
                print(f"Current BLE timeout: {current.get('no_connection_timeout_min', 0)} minutes")
                print(f"Current activity timeout: {current.get('no_activity_timeout_min', 0)} minutes")
            else:
                print("Could not retrieve current auto-shutdown settings")
            
            print("\nEnter new values (0 to disable, Enter to keep current):")
            
            # BLE timeout
            current_ble = current.get('no_connection_timeout_min', 60) if current else 60
            ble_input = input(f"BLE disconnect timeout (minutes) [{current_ble}]: ").strip()
            if ble_input:
                ble_timeout = int(ble_input)
            else:
                ble_timeout = current_ble
            
            # Activity timeout
            current_activity = current.get('no_activity_timeout_min', 30) if current else 30
            activity_input = input(f"Activity timeout (minutes) [{current_activity}]: ").strip()
            if activity_input:
                activity_timeout = int(activity_input)
            else:
                activity_timeout = current_activity
            
            # Send new configuration
            success = await self.scanpad.device.set_auto_shutdown(
                enabled=True,
                no_connection_timeout_min=ble_timeout,
                no_activity_timeout_min=activity_timeout
            )
            
            if success:
                print("✅ Auto-shutdown configuration updated")
            else:
                print("❌ Failed to update configuration")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def _show_device_info(self):
        """Show detailed device information"""
        print("\n📱 DEVICE INFORMATION")
        print("="*60)
        
        try:
            info = await self.scanpad.device.get_device_info()
            
            for key, value in info.items():
                label = key.replace('_', ' ').title()
                print(f"{label}: {value}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    async def _factory_reset(self):
        """Factory reset entire device"""
        print("\n🏭 FACTORY RESET")
        print("="*60)
        print("⚠️  WARNING: This will reset ALL device settings!")
        print("- All key configurations will be cleared")
        print("- Device settings will return to defaults")
        print("- LED states will be reset")
        
        if input("\nAre you absolutely sure? (type 'RESET' to confirm): ").strip() == 'RESET':
            try:
                # Reset keys
                await self.scanpad.keys.factory_reset()
                
                # Reset device settings
                await self.scanpad.device.set_orientation(DeviceOrientations.PORTRAIT)
                await self.scanpad.device.set_language(KeyboardLayouts.WIN_US_QWERTY)
                
                # Reset LEDs
                await self.scanpad.device.led.all_off()
                
                print("✅ Factory reset complete")
            except Exception as e:
                print(f"❌ Error during factory reset: {e}")
        else:
            print("❌ Factory reset cancelled")
    
    async def _ota_update(self):
        """OTA firmware update"""
        print("\n🎯 OTA FIRMWARE UPDATE")
        print("="*60)
        
        try:
            # Get current version from device
            current_version = await self.scanpad.device.ota.check_version()
            if current_version:
                print(f"📱 Current firmware version: {current_version}")
            else:
                print("⚠️  Could not determine current firmware version")
                current_version = "unknown"
            
            print("\nOTA OPTIONS:")
            print("1. Check for updates")
            print("2. Update firmware (automatic)")
            print("3. Start OTA service (manual upload)")
            print("4. Check OTA status")
            print("0. Cancel")
            
            choice = input("\nSelect option (0-4): ").strip()
            
            if choice == '1':
                await self._check_for_updates()
            elif choice == '2':
                await self._update_firmware()
            elif choice == '3':
                await self._manual_ota()
            elif choice == '4':
                await self._check_ota_status()
            elif choice == '0':
                print("OTA cancelled")
            else:
                print("Invalid choice")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def _check_for_updates(self):
        """Check for available firmware updates"""
        try:
            # Get API token
            api_token = self._get_api_token()
            if not api_token:
                return
            
            print("\nChecking for updates...")
            
            # Use integrated OTA controller
            update_info = await self.scanpad.ota.check_for_updates(api_token)
            
            print("\nUPDATE INFORMATION:")
            print(f"  Current: {update_info['current_version']}")
            print(f"  Latest:  {update_info['latest_version']}")
            print(f"  Available: {'Yes' if update_info['update_available'] else 'No'}")
            
            if update_info.get('release_notes'):
                print(f"\nRelease Notes:\n{update_info['release_notes']}")
                
        except AuthenticationError as e:
            print(f"Authentication failed: {e}")
            print("Set ARDENT_OTA_API_KEY environment variable with your GitHub token")
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def _get_api_token(self) -> Optional[str]:
        """Get GitHub API token from user or environment"""
        import os
        
        # Check environment first
        env_token = os.environ.get('ARDENT_OTA_API_KEY')
        if env_token:
            print("Using GitHub token from ARDENT_OTA_API_KEY environment variable")
            return env_token
        
        print("\nGitHub Personal Access Token required for repository access")
        print("Create one at: https://github.com/settings/tokens")
        print("Required permissions: 'repo' (Repository access)")
        
        token = input("\nEnter GitHub token (or set ARDENT_OTA_API_KEY env var): ").strip()
        return token if token else None
    
    async def _update_firmware(self):
        """Update firmware with progress monitoring"""
        try:
            # Get API token
            api_token = self._get_api_token()
            if not api_token:
                return
            
            print("\nStarting firmware update...")
            
            # Progress tracking
            last_progress = -1
            last_status = ""
            
            def progress_callback(progress: int, status: str):
                nonlocal last_progress, last_status
                if progress != last_progress or status != last_status:
                    # Create progress bar
                    bar_length = 30
                    filled = int(bar_length * progress / 100)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    
                    print(f"\rProgress: [{bar}] {progress}% - {status.title()}", end="", flush=True)
                    last_progress = progress
                    last_status = status
            
            # Get user confirmation
            print("\nThis will update your device firmware and restart it.")
            if input("Continue? (y/N): ").lower() != 'y':
                print("Update cancelled")
                return
            
            # Start update (the controller handles WiFi AP creation and prompting)
            result = await self.scanpad.ota.update_firmware(
                api_token=api_token,
                progress_callback=progress_callback
            )
            
            print()  # New line after progress bar
            
            if result['success']:
                print(f"Update completed successfully!")
                print(f"Updated from {result['previous_version']} to {result['new_version']}")
                print(f"Duration: {result['duration']:.1f} seconds")
            else:
                print(f"Update failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"\nUpdate failed: {e}")
        
        input("\nPress Enter to continue...")
    
    async def _manual_ota(self):
        """Start manual OTA service"""
        try:
            print("\nStarting OTA service for manual upload...")
            
            # Use the device controller's OTA service for manual mode
            success = await self.scanpad.device.ota.start()
            if success:
                print("OTA service started")
                print("WiFi AP: 'aRdent ScanPad' (no password)")
                print("Upload URL: http://192.168.4.1/firmware")
                
                input("\nConnect to WiFi and upload firmware, then press Enter...")
            else:
                print("Failed to start OTA service")
                
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    
    async def _check_ota_status(self):
        """Check current OTA status"""
        try:
            print("\n📊 Checking OTA status...")
            status = await self.scanpad.device.ota.get_status()
            
            print(f"  State: {status['state_name'].title()}")
            print(f"  Progress: {status['progress']}%")
            
            if status['state'] == 5:  # Error state
                print("⚠️  OTA is in error state")
            elif status['state'] == 4:  # Success state
                print("✅ OTA completed successfully")
            elif status['state'] in [1, 2, 3]:  # Active states
                print("🔄 OTA is in progress...")
                
        except Exception as e:
            print(f"❌ Error checking status: {e}")
    
    async def _load_json_configuration(self):
        """Load and apply keyboard configuration from JSON file"""
        print("\n📄 LOAD JSON CONFIGURATION")
        print("-" * 30)
        
        # Browse for keyboard configuration files
        file_path = self.json_browser.display_json_menu("keyboard")
        if not file_path:
            return
        
        # Load the JSON
        config = self.json_browser.load_json(file_path)
        if not config:
            return
        
        # Preview the configuration
        print(f"\n🔍 Loading: {file_path.name}")
        if "metadata" in config:
            meta = config["metadata"]
            if meta.get("name"):
                print(f"  Name: {meta['name']}")
            if meta.get("description"):
                print(f"  Description: {meta['description']}")
        
        # Show key count
        if "keys" in config:
            print(f"  Keys configured: {len(config['keys'])}")
        elif "matrix_keys" in config:
            total = len(config.get("matrix_keys", {}))
            total += len(config.get("external_buttons", {}))
            print(f"  Keys configured: {total}")
        
        # Confirm application
        if not confirm("\nApply this configuration?"):
            return
        
        try:
            print("\nApplying configuration...")
            success = await self.scanpad.keys.apply_json_configuration(config)
            if success:
                print("✅ Configuration applied successfully!")
                # Refresh local cache
                await self._get_all_key_configs()
            else:
                print("❌ Failed to apply configuration")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        pause_for_user()
    
    async def _load_json_device_commands(self):
        """Load and execute device commands from JSON file"""
        print("\n📄 LOAD JSON DEVICE COMMANDS")
        print("-" * 30)
        
        # Browse for device command files
        file_path = self.json_browser.display_json_menu("device")
        if not file_path:
            return
        
        # Load the JSON
        config = self.json_browser.load_json(file_path)
        if not config:
            return
        
        # Preview the commands
        print(f"\n🔍 Loading: {file_path.name}")
        if "metadata" in config:
            meta = config["metadata"]
            if meta.get("name"):
                print(f"  Name: {meta['name']}")
            if meta.get("description"):
                print(f"  Description: {meta['description']}")
        
        # Show command count
        if "commands" in config:
            print(f"  Commands to execute: {len(config['commands'])}")
            print("\n  Commands:")
            for i, cmd in enumerate(config["commands"].keys(), 1):
                print(f"    {i}. {cmd}")
        
        # Confirm execution
        if not confirm("\nExecute these commands?"):
            return
        
        try:
            print("\nExecuting commands...")
            success = await self.scanpad.device.execute_commands_from_json(config)
            if success:
                print("✅ All commands executed successfully!")
            else:
                print("❌ Some commands may have failed")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        pause_for_user()
    
    async def _json_commands_menu(self):
        """JSON Commands menu for device commands and keyboard configurations"""
        while True:
            print("\n📋 JSON COMMANDS")
            print("-" * 40)
            print("1. 📁 Load Device Commands JSON")
            print("2. ⌨️  Load Keyboard Configuration JSON")
            print("3. ✏️  Manual JSON Input")
            print("4. 📄 View Available JSON Examples")
            print("0. 🔙 Back to Main Menu")
            
            choice = input("\nSelect option (0-4): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                await self._load_device_commands_json()
            elif choice == '2':
                await self._load_keyboard_config_json()
            elif choice == '3':
                await self._manual_json_input()
            elif choice == '4':
                await self._show_json_examples()
            else:
                print("❌ Invalid choice")
    
    async def _load_device_commands_json(self):
        """Load and execute device commands from JSON file"""
        print("\n📁 LOAD DEVICE COMMANDS JSON")
        print("-" * 40)
        
        # Define the examples directory
        examples_dir = Path(__file__).parent.parent / "json" / "device-commands"
        
        if not examples_dir.exists():
            print("❌ Device commands examples directory not found")
            return
        
        # List available JSON files
        json_files = list(examples_dir.glob("*.json"))
        if not json_files:
            print("❌ No JSON files found in device-commands directory")
            return
        
        print("Available device command files:")
        for i, file_path in enumerate(json_files, 1):
            print(f"{i}. {file_path.name}")
        
        try:
            choice = int(input(f"\nSelect file (1-{len(json_files)}): "))
            if 1 <= choice <= len(json_files):
                selected_file = json_files[choice - 1]
                await self._execute_json_file(selected_file, "device")
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a valid number")
    
    async def _load_keyboard_config_json(self):
        """Load and apply keyboard configuration from JSON file"""
        print("\n⌨️  LOAD KEYBOARD CONFIGURATION JSON")
        print("-" * 40)
        
        # Define the examples directory
        examples_dir = Path(__file__).parent.parent / "json" / "keyboard-configs"
        
        if not examples_dir.exists():
            print("❌ Keyboard configs examples directory not found")
            return
        
        # List available JSON files
        json_files = list(examples_dir.glob("*.json"))
        if not json_files:
            print("❌ No JSON files found in keyboard-configs directory")
            return
        
        print("Available keyboard configuration files:")
        for i, file_path in enumerate(json_files, 1):
            print(f"{i}. {file_path.name}")
        
        try:
            choice = int(input(f"\nSelect file (1-{len(json_files)}): "))
            if 1 <= choice <= len(json_files):
                selected_file = json_files[choice - 1]
                await self._execute_json_file(selected_file, "keyboard")
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a valid number")
    
    async def _execute_json_file(self, file_path: Path, json_type: str):
        """Execute a JSON file (device commands or keyboard config)"""
        try:
            print(f"\n📄 Loading: {file_path.name}")
            
            # Load JSON data
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Preview JSON content
            print(f"📋 JSON Content Preview:")
            print(json.dumps(json_data, indent=2)[:500] + "..." if len(str(json_data)) > 500 else json.dumps(json_data, indent=2))
            
            if not confirm("\n❓ Execute this JSON configuration?"):
                return
            
            # Execute based on type
            if json_type == "device":
                await self._execute_device_commands_json(json_data)
            elif json_type == "keyboard":
                await self._execute_keyboard_config_json(json_data)
            
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON format: {e}")
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
    
    async def _execute_device_commands_json(self, json_data: dict):
        """Execute device commands from JSON data"""
        try:
            print("\n🚀 Executing device commands...")
            result = await self.scanpad.device.execute_commands_from_json(json_data)
            
            if result["success"]:
                print(f"✅ Device commands executed successfully!")
                print(f"📊 Commands executed: {result['executed']}")
            else:
                print(f"❌ Device commands failed!")
                print(f"📊 Commands executed: {result['executed']}")
                if result["errors"]:
                    print("🔴 Errors:")
                    for error in result["errors"]:
                        print(f"   • {error}")
                        
        except Exception as e:
            print(f"❌ Error executing device commands: {e}")
        
        pause_for_user()
    
    async def _execute_keyboard_config_json(self, json_data: dict):
        """Execute keyboard configuration from JSON data"""
        try:
            print("\n⌨️  Applying keyboard configuration...")
            
            # Extract keys from JSON
            keys_data = json_data.get("keys", {})
            if not keys_data:
                print("❌ No 'keys' section found in JSON")
                return
            
            success_count = 0
            error_count = 0
            errors = []
            
            # Apply each key configuration
            for key_id_str, actions in keys_data.items():
                try:
                    # Convert key_id to int (handle both "0" and "0,0" formats)
                    if "," in key_id_str:
                        # Matrix format "row,col"
                        row, col = map(int, key_id_str.split(","))
                        key_id = row * 4 + col  # Convert to linear key ID
                    else:
                        key_id = int(key_id_str)
                    
                    # Convert actions to proper format
                    converted_actions = []
                    for action in actions:
                        if action.get("type") == "text":
                            # Text action
                            converted_actions.append(self.scanpad.keys.create_text_action(action["value"]))
                        elif action.get("type") == "hid":
                            # HID action
                            converted_actions.append(self.scanpad.keys.create_hid_action(
                                action["keycode"], action.get("modifier", 0)
                            ))
                        # Add more action types as needed
                    
                    # Apply to device
                    if converted_actions:
                        await self.scanpad.keys.set_key_config(key_id, converted_actions)
                        success_count += 1
                        print(f"✅ Key {key_id}: {len(converted_actions)} action(s) configured")
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f"Key {key_id_str}: {str(e)}"
                    errors.append(error_msg)
                    print(f"❌ {error_msg}")
            
            # Summary
            if success_count > 0:
                print(f"\n✅ Keyboard configuration completed!")
                print(f"📊 Keys configured: {success_count}")
                if error_count > 0:
                    print(f"❌ Keys failed: {error_count}")
            else:
                print(f"\n❌ Keyboard configuration failed!")
                print(f"📊 All {error_count} keys failed")
                        
        except Exception as e:
            print(f"❌ Error applying keyboard configuration: {e}")
        
        pause_for_user()
    
    async def _manual_json_input(self):
        """Manual JSON input for testing"""
        print("\n✏️  MANUAL JSON INPUT")
        print("-" * 40)
        print("Enter JSON data (type 'END' on a new line to finish):")
        print("Example formats:")
        print('• Device: {"domain": "led_control", "action": "led_on", "parameters": {"led_id": 1}}')
        print('• Keyboard: {"keys": {"0,0": [{"type": "UTF8", "data": "Hello"}]}}')
        print()
        
        lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
        
        json_text = '\n'.join(lines)
        if not json_text.strip():
            print("❌ No JSON data entered")
            return
        
        try:
            json_data = json.loads(json_text)
            print(f"\n📋 Parsed JSON:")
            print(json.dumps(json_data, indent=2))
            
            if not confirm("\n❓ Execute this JSON?"):
                return
            
            # Auto-detect type
            if 'domain' in json_data or 'commands' in json_data:
                await self._execute_device_commands_json(json_data)
            elif 'keys' in json_data:
                await self._execute_keyboard_config_json(json_data)
            else:
                print("❌ Unknown JSON format - must contain 'domain'/'commands' or 'keys'")
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON format: {e}")
        except Exception as e:
            print(f"❌ Error processing JSON: {e}")
    
    async def _show_json_examples(self):
        """Show available JSON examples"""
        print("\n📄 AVAILABLE JSON EXAMPLES")
        print("=" * 50)
        
        # Device Commands
        device_dir = Path(__file__).parent.parent / "json" / "device-commands"
        print("\n🔧 Device Commands:")
        if device_dir.exists():
            for file_path in device_dir.glob("*.json"):
                print(f"   • {file_path.name}")
        else:
            print("   ❌ Directory not found")
        
        # Keyboard Configs
        keyboard_dir = Path(__file__).parent.parent / "json" / "keyboard-configs"
        print("\n⌨️  Keyboard Configurations:")
        if keyboard_dir.exists():
            for file_path in keyboard_dir.glob("*.json"):
                print(f"   • {file_path.name}")
        else:
            print("   ❌ Directory not found")
        
        print(f"\n📂 Paths:")
        print(f"   Device Commands: {device_dir}")
        print(f"   Keyboard Configs: {keyboard_dir}")
        
        pause_for_user()
    
    async def _disconnect(self):
        """Disconnect from device"""
        if self.scanpad:
            print("\n👋 Disconnecting from device...")
            await self.scanpad.disconnect()
            print("✅ Disconnected")


async def main():
    """Main entry point"""
    app = ScanPadInteractive()
    try:
        await app.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())