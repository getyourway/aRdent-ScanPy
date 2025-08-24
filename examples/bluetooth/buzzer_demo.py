#!/usr/bin/env python3
"""
Buzzer Demo - Audio feedback demonstration
Shows various buzzer capabilities of the aRdent ScanPad
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ardent_scanpad import ScanPad


async def main():
    """Buzzer demonstration"""
    print("🔗 Connecting to aRdent ScanPad...")
    
    # Connect to device
    scanpad = ScanPad()
    await scanpad.connect()
    print("✅ Connected!")
    
    try:
        print("\n🔊 BUZZER DEMONSTRATION")
        print("="*50)
        
        # Demo 1: Basic beeps
        print("\n🎵 Demo 1: Basic Beeps")
        print("Single beep...")
        await scanpad.device.buzzer.beep()
        await asyncio.sleep(1)
        
        print("Three quick beeps...")
        for _ in range(3):
            await scanpad.device.buzzer.beep()
            await asyncio.sleep(0.3)
        await asyncio.sleep(1)
        
        # Demo 2: Volume control
        print("\n🔉 Demo 2: Volume Control")
        volumes = [25, 50, 75, 100]
        
        for volume in volumes:
            print(f"Setting volume to {volume}% and beeping...")
            await scanpad.device.buzzer.set_volume(volume)
            await scanpad.device.buzzer.beep()
            await asyncio.sleep(1)
        
        # Demo 3: Melodies
        print("\n🎶 Demo 3: Predefined Melodies")
        melodies = [
            ("Success", "SUCCESS"),
            ("Error", "ERROR"),
            ("Warning", "WARNING"),
            ("Confirm", "CONFIRM")
        ]
        
        for name, melody_id in melodies:
            print(f"Playing {name} melody...")
            try:
                await scanpad.device.buzzer.play_melody(melody_id)
                await asyncio.sleep(2)
            except Exception as e:
                print(f"  Melody '{melody_id}' not available: {e}")
                # Fallback to beeps
                if melody_id == "SUCCESS":
                    for _ in range(2):
                        await scanpad.device.buzzer.beep()
                        await asyncio.sleep(0.2)
                elif melody_id == "ERROR":
                    for _ in range(3):
                        await scanpad.device.buzzer.beep()
                        await asyncio.sleep(0.1)
                elif melody_id == "WARNING":
                    await scanpad.device.buzzer.beep()
                    await asyncio.sleep(0.2)
                    await scanpad.device.buzzer.beep()
                elif melody_id == "CONFIRM":
                    await scanpad.device.buzzer.beep()
                
                await asyncio.sleep(1)
        
        # Demo 4: Rhythm patterns
        print("\n🥁 Demo 4: Custom Rhythm Patterns")
        
        print("Pattern 1: Short-Short-Long")
        await scanpad.device.buzzer.beep()
        await asyncio.sleep(0.2)
        await scanpad.device.buzzer.beep()
        await asyncio.sleep(0.2)
        await scanpad.device.buzzer.beep()
        await asyncio.sleep(0.8)
        
        print("Pattern 2: Morse Code SOS (...---...)")
        # S (...)
        for _ in range(3):
            await scanpad.device.buzzer.beep()
            await asyncio.sleep(0.1)
        await asyncio.sleep(0.3)
        
        # O (---)
        for _ in range(3):
            await scanpad.device.buzzer.beep()
            await asyncio.sleep(0.3)
        await asyncio.sleep(0.3)
        
        # S (...)
        for _ in range(3):
            await scanpad.device.buzzer.beep()
            await asyncio.sleep(0.1)
        
        await asyncio.sleep(1)
        
        # Demo 5: Interactive feedback simulation
        print("\n📱 Demo 5: Interactive Feedback Simulation")
        
        print("Simulating user interactions...")
        
        # Button press feedback
        print("  Button press...")
        await scanpad.device.buzzer.beep()
        await asyncio.sleep(0.5)
        
        # Success feedback
        print("  Operation successful...")
        for _ in range(2):
            await scanpad.device.buzzer.beep()
            await asyncio.sleep(0.2)
        await asyncio.sleep(1)
        
        # Error feedback
        print("  Error occurred...")
        await scanpad.device.buzzer.set_volume(80)
        for _ in range(3):
            await scanpad.device.buzzer.beep()
            await asyncio.sleep(0.1)
        await asyncio.sleep(1)
        
        # Completion feedback
        print("  Task completed...")
        await scanpad.device.buzzer.set_volume(60)
        await scanpad.device.buzzer.beep()
        await asyncio.sleep(0.3)
        await scanpad.device.buzzer.beep()
        
        # Reset volume to moderate level
        await scanpad.device.buzzer.set_volume(50)
        
        print("\n✅ Buzzer demo complete!")
        print("💡 Tip: Use different volumes and patterns to create")
        print("    distinct audio feedback for your application")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        print("\n🔌 Disconnecting...")
        await scanpad.disconnect()


if __name__ == "__main__":
    asyncio.run(main())