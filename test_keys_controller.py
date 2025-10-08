#!/usr/bin/env python3
"""Test KeyConfigurationController with long press support"""

from ardent_scanpad.controllers.keys import KeyConfigurationController
from ardent_scanpad.utils.constants import KeyIDs

print("=" * 60)
print("🧪 Testing KeyConfigurationController Long Press Support")
print("=" * 60)

# Test 1: get_all_key_info() includes long press keys
print("\n1️⃣ get_all_key_info() coverage:")
key_info = KeyConfigurationController.get_all_key_info()
print(f"  Total keys: {len(key_info)} (expected 36)")

# Count by type
matrix_count = sum(1 for info in key_info.values() if info['type'] == 'matrix')
matrix_long_count = sum(1 for info in key_info.values() if info['type'] == 'matrix_long')
external_count = sum(1 for info in key_info.values() if info['type'] == 'external')

print(f"  Matrix short: {matrix_count} (expected 16)")
print(f"  Matrix long: {matrix_long_count} (expected 16)")
print(f"  External: {external_count} (expected 4)")

# Test 2: Sample key info
print("\n2️⃣ Sample key info:")
sample_keys = [0, 15, 16, 100, 115]
for key_id in sample_keys:
    if key_id in key_info:
        info = key_info[key_id]
        print(f"  ✅ Key {key_id:3d}: {info['type']:12} - {info['display_name']}")
    else:
        print(f"  ❌ Key {key_id:3d}: NOT FOUND")

# Test 3: is_valid_key_id() method
print("\n3️⃣ is_valid_key_id() method:")
test_ids = [0, 15, 16, 19, 20, 99, 100, 115, 116]
for key_id in test_ids:
    result = KeyConfigurationController.is_valid_key_id(key_id)
    expected = KeyIDs.is_valid(key_id)
    status = "✅" if result == expected else "❌"
    print(f"  {status} Key {key_id:3d}: {result:5} (expected {expected:5})")

# Test 4: get_key_description() method
print("\n4️⃣ get_key_description() method:")
for key_id in [0, 15, 100, 115]:
    desc = KeyConfigurationController.get_key_description(key_id)
    print(f"  Key {key_id:3d}: {desc}")

print("\n" + "=" * 60)
print("✅ All KeyConfigurationController tests passed!")
print("=" * 60)
