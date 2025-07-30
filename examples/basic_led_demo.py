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
from ardent_scanpad.utils.constants import LEDs


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
        print("Turning individual LEDs on one by one...")
        
        individual_leds = [LEDs.GREEN_1, LEDs.GREEN_3]  # Only individual LEDs
        for led_id in individual_leds:
            await scanpad.device.led.turn_on(led_id)
            print(f"  LED {led_id} ({LEDs.NAMES[led_id]}) ON")
            await asyncio.sleep(0.5)
        
        await asyncio.sleep(1)
        
        print("Turning individual LEDs off one by one...")
        for led_id in individual_leds:
            await scanpad.device.led.turn_off(led_id)
            print(f"  LED {led_id} ({LEDs.NAMES[led_id]}) OFF")
            await asyncio.sleep(0.5)
        
        # Demo 2: Blinking LEDs
        print("\n✨ Demo 2: Blinking LEDs")
        print(f"Blinking LED {LEDs.GREEN_1} ({LEDs.NAMES[LEDs.GREEN_1]}) at 2 Hz...")
        await scanpad.device.led.blink(LEDs.GREEN_1, frequency=2.0)
        await asyncio.sleep(3)
        await scanpad.device.led.stop_blink(LEDs.GREEN_1)
        
        await asyncio.sleep(1)
        
        # Demo 3: RGB Colors (using correct LED constants)
        print("\n🎨 Demo 3: RGB Colors")
        rgb_colors = [
            ("Red", LEDs.RED),
            ("Green", LEDs.GREEN_2),
            ("Blue", LEDs.BLUE),
            ("Yellow", LEDs.YELLOW),
            ("Cyan", LEDs.CYAN),
            ("Magenta", LEDs.MAGENTA),
            ("White", LEDs.WHITE)
        ]
        
        for name, led_id in rgb_colors:
            print(f"  Setting RGB to {name} (LED {led_id} - {LEDs.NAMES[led_id]})")
            await scanpad.device.led.turn_on(led_id)
            await asyncio.sleep(1)
            await scanpad.device.led.turn_off(led_id)
            await asyncio.sleep(0.2)
        
        # Demo 4: All LEDs operations
        print("\n🎆 Demo 4: All LEDs Operations")
        print("Turning on all available LEDs...")
        for led_id in LEDs.ALL:
            try:
                await scanpad.device.led.turn_on(led_id)
                print(f"  LED {led_id} ({LEDs.NAMES[led_id]}) ON")
            except Exception as e:
                print(f"  Failed to turn on LED {led_id}: {e}")
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