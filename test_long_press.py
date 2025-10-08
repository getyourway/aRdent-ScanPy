#!/usr/bin/env python3
"""Test long press key support"""

from ardent_scanpad.utils.constants import KeyIDs

print("=" * 60)
print("🧪 Testing Long Press Key Support")
print("=" * 60)

# Test 1: Validate all key ranges
print("\n1️⃣ Key ID Validation:")
test_cases = [
    (0, True, "Matrix short press start"),
    (15, True, "Matrix short press end"),
    (16, True, "Button start"),
    (19, True, "Button end"),
    (20, False, "Reserved range"),
    (99, False, "Reserved range end"),
    (100, True, "Matrix long press start"),
    (115, True, "Matrix long press end"),
    (116, False, "Out of range"),
]

for key_id, expected, desc in test_cases:
    result = KeyIDs.is_valid(key_id)
    status = "✅" if result == expected else "❌"
    print(f"  {status} Key {key_id:3d}: {result:5} (expected {expected:5}) - {desc}")

# Test 2: Helper methods
print("\n2️⃣ Helper Methods:")
print(f"  is_short_press(5): {KeyIDs.is_short_press(5)} (expected True)")
print(f"  is_short_press(105): {KeyIDs.is_short_press(105)} (expected False)")
print(f"  is_long_press(105): {KeyIDs.is_long_press(105)} (expected True)")
print(f"  is_long_press(5): {KeyIDs.is_long_press(5)} (expected False)")
print(f"  is_button(17): {KeyIDs.is_button(17)} (expected True)")
print(f"  is_button(100): {KeyIDs.is_button(100)} (expected False)")

# Test 3: Conversion methods
print("\n3️⃣ Key ID Conversion:")
for base_id in [0, 5, 10, 15]:
    long_id = KeyIDs.get_long_press(base_id)
    back = KeyIDs.get_base_key(long_id)
    status = "✅" if back == base_id else "❌"
    print(f"  {status} {base_id} → {long_id} → {back}")

# Test 4: NAMES dictionary
print("\n4️⃣ Key Names:")
sample_keys = [0, 15, 16, 19, 100, 115]
for key_id in sample_keys:
    name = KeyIDs.NAMES.get(key_id, "NOT FOUND")
    status = "✅" if name != "NOT FOUND" else "❌"
    print(f"  {status} Key {key_id:3d}: {name}")

# Test 5: Collections
print("\n5️⃣ Collections:")
print(f"  ALL_MATRIX_SHORT: {len(KeyIDs.ALL_MATRIX_SHORT)} keys (expected 16)")
print(f"  ALL_MATRIX_LONG: {len(KeyIDs.ALL_MATRIX_LONG)} keys (expected 16)")
print(f"  ALL_MATRIX: {len(KeyIDs.ALL_MATRIX)} keys (expected 32)")
print(f"  ALL_BUTTONS: {len(KeyIDs.ALL_BUTTONS)} keys (expected 4)")
print(f"  ALL_KEYS: {len(KeyIDs.ALL_KEYS)} keys (expected 36)")

print("\n" + "=" * 60)
print("✅ All tests completed!")
print("=" * 60)
