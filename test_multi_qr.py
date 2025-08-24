#!/usr/bin/env python3

from ardent_scanpad import ScanPad
import os

# Script industriel réaliste - Système d'inventaire avec validation
industrial_script = """-- Industrial Inventory System with Multi-QR Support
-- Realistic size for warehouse/manufacturing applications
print("Industrial inventory system starting...")

local inventory = {}
local session_stats = {scanned = 0, validated = 0, errors = 0}
local batch_mode = false
local current_batch = {}

-- Product validation patterns (realistic industrial codes)
local valid_patterns = {
    "^[A-Z]{2}%d{6}$",        -- Standard product code: AB123456
    "^EAN%d{13}$",           -- EAN barcode: EAN1234567890123
    "^UPC%d{12}$",           -- UPC barcode: UPC123456789012
    "^LOT%d{8}%-[A-Z]{2}$",   -- Lot number: LOT12345678-AB
    "^SN[A-Z0-9]{10}$",      -- Serial number: SN1234567890
    "^WO%d{6}%-[A-Z]{3}$"    -- Work order: WO123456-ABC
}

-- Location validation
local valid_locations = {
    "A01", "A02", "A03", "B01", "B02", "B03", "C01", "C02", "C03",
    "D01", "D02", "D03", "E01", "E02", "E03", "F01", "F02", "F03"
}

function validate_barcode(code)
    for _, pattern in ipairs(valid_patterns) do
        if string.match(code, pattern) then
            return true
        end
    end
    return false
end

function validate_location(loc)
    for _, valid_loc in ipairs(valid_locations) do
        if loc == valid_loc then
            return true
        end
    end
    return false
end

function format_timestamp()
    return os.date("%Y-%m-%d %H:%M:%S")
end

function on_scan(barcode)
    print("Processing: " .. barcode)
    session_stats.scanned = session_stats.scanned + 1
    
    -- Check for special commands
    if string.upper(barcode) == "BATCH_START" then
        batch_mode = true
        current_batch = {}
        key("BATCH MODE ACTIVATED\\n")
        key("Timestamp: " .. format_timestamp() .. "\\n")
        return
    elseif string.upper(barcode) == "BATCH_END" then
        batch_mode = false
        key("BATCH COMPLETED: " .. #current_batch .. " items\\n")
        key("Timestamp: " .. format_timestamp() .. "\\n\\n")
        return
    end
    
    -- Validate barcode format
    if not validate_barcode(barcode) then
        session_stats.errors = session_stats.errors + 1
        key("ERROR: Invalid barcode format: " .. barcode .. "\\n")
        play_error_sound()
        return
    end
    
    -- Process valid barcode
    session_stats.validated = session_stats.validated + 1
    
    if batch_mode then
        table.insert(current_batch, {
            code = barcode,
            timestamp = os.time(),
            sequence = #current_batch + 1
        })
        key("BATCH[" .. #current_batch .. "]: " .. barcode .. "\\n")
    else
        -- Individual item processing
        inventory[barcode] = {
            timestamp = format_timestamp(),
            count = (inventory[barcode] and inventory[barcode].count + 1) or 1
        }
        key("ITEM: " .. barcode .. " (Count: " .. inventory[barcode].count .. ")\\n")
    end
    
    play_confirm_sound()
end

function on_button(button_id)
    if button_id == 15 then
        -- Statistics report
        key("\\n=== INVENTORY REPORT ===\\n")
        key("Session Stats:\\n")
        key("- Scanned: " .. session_stats.scanned .. "\\n")
        key("- Validated: " .. session_stats.validated .. "\\n") 
        key("- Errors: " .. session_stats.errors .. "\\n")
        key("- Success Rate: " .. string.format("%.1f", (session_stats.validated/math.max(session_stats.scanned,1))*100) .. "%\\n")
        key("\\nInventory Items: " .. count_inventory() .. "\\n")
        key("Timestamp: " .. format_timestamp() .. "\\n")
        key("========================\\n\\n")
        
    elseif button_id == 14 then
        -- Location entry mode
        key("LOCATION MODE: Scan location code\\n")
        
    elseif button_id == 13 then
        -- Reset statistics
        session_stats = {scanned = 0, validated = 0, errors = 0}
        key("STATS RESET\\n")
        
    elseif button_id >= 0 and button_id <= 15 then
        -- Quick location shortcut
        local quick_location = valid_locations[button_id + 1]
        if quick_location then
            key("LOCATION SET: " .. quick_location .. "\\n")
        else
            key("Button " .. button_id .. " pressed\\n")
        end
    end
end

function count_inventory()
    local count = 0
    for _ in pairs(inventory) do
        count = count + 1
    end
    return count
end

function play_confirm_sound()
    -- Hardware confirmation (if available)
    led_blink(2, 100)  -- Green LED blink
end

function play_error_sound()
    -- Hardware error indication (if available)  
    led_blink(4, 200)  -- Red LED blink
end

function setup()
    scanner_enable_lua_processing(true)
    key("\\n=== INDUSTRIAL INVENTORY SYSTEM ===\\n")
    key("Multi-QR Lua Script Loaded Successfully\\n")
    key("Version: 1.2.0\\n")
    key("Features:\\n")
    key("- Barcode validation (6 formats)\\n")
    key("- Batch processing (BATCH_START/END)\\n") 
    key("- Location tracking (18 zones)\\n")
    key("- Real-time statistics\\n")
    key("- Error detection & reporting\\n")
    key("\\nControls:\\n")
    key("- Button 15: Full report\\n")
    key("- Button 14: Location mode\\n")
    key("- Button 13: Reset stats\\n")
    key("- Buttons 0-11: Quick locations\\n")
    key("\\nReady for scanning!\\n")
    key("Timestamp: " .. format_timestamp() .. "\\n")
    key("===================================\\n\\n")
    
    print("Industrial inventory system initialized")
    print("Supported patterns: " .. #valid_patterns)
    print("Available locations: " .. #valid_locations)
end

-- Initialize the system
setup()
"""

print(f"Script size: {len(industrial_script)} characters")

# Générer les QR codes
scanpad = ScanPad()
qr_commands = scanpad.qr.create_lua_script_qr(industrial_script, max_qr_size=800, compression_level=9)

print(f"Generated {len(qr_commands)} QR fragments")

# Créer le répertoire de sortie
os.makedirs('output/test_multi', exist_ok=True)

# Sauvegarder les QR codes
for i, qr in enumerate(qr_commands):
    fragment_num = i + 1
    total_fragments = len(qr_commands)
    
    filename = f"test_multi_{fragment_num:02d}_of_{total_fragments:02d}.png"
    filepath = f"output/test_multi/{filename}"
    
    qr.save(filepath, size=400, border=4)
    print(f"Saved: {filepath}")

print(f"\nTest QR codes ready in output/test_multi/")
print(f"Scan them in order: 1 → 2 → ... → {len(qr_commands)}")