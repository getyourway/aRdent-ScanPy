#!/usr/bin/env python3
"""
Script to clean _force parameters from the public API
"""

import re

def clean_device_controller():
    """Remove all _force logic from device.py"""
    
    with open('ardent_scanpad/controllers/device.py', 'r') as f:
        content = f.read()
    
    # Remove _force validation bypass patterns
    patterns_to_replace = [
        # Pattern 1: Simple validation bypass
        (r'        if not _force:\n            self\.parent\._validate_led_id\(led_id\).*?\n\n.*?if _force.*?\n.*?else:\n            payload = bytes\(\[led_id\]\)', 
         '        self.parent._validate_led_id(led_id)\n        payload = bytes([led_id])'),
        
        # Pattern 2: Complex validation bypass
        (r'        if not _force:\n.*?# Handle out-of-range values.*?\n.*?else:\n            payload = bytes\([^)]+\)', 
         '        self.parent._validate_led_id(led_id)\n        payload = bytes([led_id])'),
        
        # Pattern 3: Buzzer validation
        (r'        if not _force:\n            if duration_ms.*?\n.*?if volume.*?\n\n.*?else:\n            payload = struct\.pack.*?', 
         '        if duration_ms < 50 or duration_ms > 5000:\n            raise ValueError("Duration must be 50-5000ms")\n        if volume is not None and not (0 <= volume <= 100):\n            raise ValueError("Volume must be 0-100")\n        \n        if volume is None:\n            payload = struct.pack("<H", duration_ms)\n        else:\n            payload = struct.pack("<HB", duration_ms, volume)'),
        
        # Clean any remaining _force references
        (r'if not _force:\n', ''),
        (r'if _force.*?\n.*?\n.*?else:\n', ''),
        (r'# Handle out-of-range values when _force=True.*?\n', ''),
        (r'# Use byte wrapping for negative values.*?\n', ''),
    ]
    
    # Apply replacements
    for pattern, replacement in patterns_to_replace:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Clean up documentation references to _force
    content = re.sub(r'            _force: Internal parameter.*?\n', '', content)
    
    # Write back
    with open('ardent_scanpad/controllers/device.py', 'w') as f:
        f.write(content)
    
    print("✅ Cleaned device.py from _force parameters")

if __name__ == '__main__':
    clean_device_controller()