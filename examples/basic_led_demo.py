#!/usr/bin/env python3
"""
Basic LED Demo - Simple LED control example
Demonstrates basic LED operations with the aRdent ScanPad
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ardent_scanpad import ScanPad


async def main():
    """Basic LED demonstration"""
    print("🔗 Connecting to aRdent ScanPad...")
    
    # Connect to device
    scanpad = ScanPad()
    await scanpad.connect()
    print("✅ Connected!")
    
    try:
        # Demo 1: Individual LED control
        print("\n💡 Demo 1: Individual LED Control")
        print("Turning LEDs on one by one...")
        
        for led_id in range(1, 6):  # LEDs 1-5
            await scanpad.device.led.turn_on(led_id)
            print(f"  LED {led_id} ON")
            await asyncio.sleep(0.5)
        
        await asyncio.sleep(1)
        
        print("Turning LEDs off one by one...")
        for led_id in range(1, 6):
            await scanpad.device.led.turn_off(led_id)
            print(f"  LED {led_id} OFF")
            await asyncio.sleep(0.5)
        
        # Demo 2: Blinking LEDs
        print("\n✨ Demo 2: Blinking LEDs")
        print("Blinking LED 1 at 2 Hz...")
        await scanpad.device.led.blink(1, frequency=2.0)
        await asyncio.sleep(3)
        await scanpad.device.led.stop_blink(1)
        
        await asyncio.sleep(1)
        
        # Demo 3: RGB Colors (using RGB LED IDs)
        print("\n🎨 Demo 3: RGB Colors")
        rgb_colors = [
            ("Red", 3),
            ("Green", 4),
            ("Blue", 5),
            ("Yellow", 6),
            ("Cyan", 7),
            ("Magenta", 8),
            ("White", 9)
        ]
        
        for name, led_id in rgb_colors:
            print(f"  Setting RGB to {name} (LED {led_id})")
            await scanpad.device.led.turn_on(led_id)
            await asyncio.sleep(1)
            await scanpad.device.led.turn_off(led_id)
            await asyncio.sleep(0.2)
        
        # Demo 4: All LEDs operations
        print("\n🎆 Demo 4: All LEDs Operations")
        print("All LEDs ON...")
        for led_id in range(1, 6):
            try:
                await scanpad.device.led.turn_on(led_id)
            except:
                pass
        await asyncio.sleep(2)
        
        print("All LEDs OFF...")
        await scanpad.device.led.all_off()
        
        print("\n✅ LED demo complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        print("🔌 Disconnecting...")
        await scanpad.disconnect()


if __name__ == "__main__":
    asyncio.run(main())