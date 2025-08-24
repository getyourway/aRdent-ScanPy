#!/usr/bin/env python3
"""
aRdent ScanPad - Advanced Lua Script QR Generation

This example demonstrates advanced Lua script deployment features:
- Complex inventory management system
- Multi-fragment QR codes for large scripts
- Error handling and validation
- Complete workflow from script to deployment
"""

import sys
from pathlib import Path
from ardent_scanpad import ScanPad

def create_inventory_script():
    """Create a complete inventory management Lua script"""
    
    script = '''
-- Advanced Inventory Management System
-- Supports SKU tracking, item counting, reporting, and data export

local inventory = {}
local session_stats = {
    total_scans = 0,
    sku_items = 0,
    regular_items = 0,
    session_start = os.time(),
    last_scan_time = 0
}

local config = {
    sku_prefix = "SKU:",
    export_key = 15,    -- Bottom-right key for export
    clear_key = 14,     -- Key 14 for clear
    stats_key = 13,     -- Key 13 for stats
    beep_on_scan = true,
    led_feedback = true
}

-- Utility Functions
local function log_with_timestamp(message)
    local timestamp = os.date("%H:%M:%S")
    log("[" .. timestamp .. "] " .. message)
end

local function format_duration(seconds)
    local hours = math.floor(seconds / 3600)
    local minutes = math.floor((seconds % 3600) / 60)
    local secs = seconds % 60
    
    if hours > 0 then
        return string.format("%dh %dm %ds", hours, minutes, secs)
    elseif minutes > 0 then
        return string.format("%dm %ds", minutes, secs)
    else
        return string.format("%ds", secs)
    end
end

local function update_led_status()
    if not config.led_feedback then return end
    
    -- LED pattern based on inventory size
    local total_items = 0
    for sku, count in pairs(inventory) do
        total_items = total_items + count
    end
    
    if total_items == 0 then
        led_all_off()
    elseif total_items < 10 then
        led_on(2)  -- Green for low count
    elseif total_items < 50 then
        led_blink(2, 2)  -- Blinking green for medium
    else
        led_on(3)  -- LED 3 for high count
    end
end

local function provide_feedback(scan_type)
    if config.beep_on_scan then
        if scan_type == "sku" then
            buzzer_melody("SUCCESS")
        elseif scan_type == "regular" then
            beep(100)
        else
            buzzer_melody("ERROR")
        end
    end
    
    update_led_status()
end

-- Main Scanning Logic
function on_scan(barcode)
    session_stats.total_scans = session_stats.total_scans + 1
    session_stats.last_scan_time = os.time()
    
    log_with_timestamp("Scan #" .. session_stats.total_scans .. ": " .. barcode)
    
    -- Check if it's an SKU item
    if string.sub(barcode, 1, string.len(config.sku_prefix)) == config.sku_prefix then
        -- SKU inventory item
        local sku = barcode
        inventory[sku] = (inventory[sku] or 0) + 1
        session_stats.sku_items = session_stats.sku_items + 1
        
        key("INVENTORY: " .. sku .. " (Count: " .. inventory[sku] .. ")\\n")
        log_with_timestamp("SKU added: " .. sku .. " -> " .. inventory[sku])
        
        provide_feedback("sku")
        
        -- Special handling for high quantities
        if inventory[sku] >= 10 then
            key("  -> HIGH QUANTITY WARNING: " .. inventory[sku] .. " items\\n")
            led_blink(4, 5)  -- Red blinking warning
        end
        
    elseif string.sub(barcode, 1, 6) == "REMOVE" then
        -- Remove item command: REMOVE:SKU:12345
        local sku_to_remove = "SKU:" .. string.sub(barcode, 8)
        
        if inventory[sku_to_remove] and inventory[sku_to_remove] > 0 then
            inventory[sku_to_remove] = inventory[sku_to_remove] - 1
            
            if inventory[sku_to_remove] == 0 then
                inventory[sku_to_remove] = nil
                key("REMOVED: " .. sku_to_remove .. " (DEPLETED)\\n")
            else
                key("REMOVED: " .. sku_to_remove .. " (Remaining: " .. inventory[sku_to_remove] .. ")\\n")
            end
            
            log_with_timestamp("Item removed: " .. sku_to_remove)
            provide_feedback("sku")
        else
            key("ERROR: Cannot remove " .. sku_to_remove .. " (not in inventory)\\n")
            provide_feedback("error")
        end
        
    else
        -- Regular barcode passthrough
        session_stats.regular_items = session_stats.regular_items + 1
        key("ITEM: " .. barcode .. "\\n")
        log_with_timestamp("Regular item: " .. barcode)
        
        provide_feedback("regular")
    end
end

-- Button Functions
function on_button(button_id)
    log_with_timestamp("Button " .. button_id .. " pressed")
    
    if button_id == config.export_key then
        -- Export inventory report
        export_inventory_report()
        
    elseif button_id == config.clear_key then
        -- Clear inventory with confirmation
        clear_inventory()
        
    elseif button_id == config.stats_key then
        -- Show session statistics
        show_session_stats()
        
    elseif button_id >= 0 and button_id <= 9 then
        -- Number keys 0-9 for quick actions
        handle_number_key(button_id)
        
    else
        -- Generic button feedback
        beep(50)
        log_with_timestamp("Button " .. button_id .. " (no action assigned)")
    end
end

function export_inventory_report()
    key("\\n===== INVENTORY REPORT =====\\n")
    key("Generated: " .. os.date("%Y-%m-%d %H:%M:%S") .. "\\n")
    key("\\n")
    
    local total_items = 0
    local unique_skus = 0
    
    for sku, count in pairs(inventory) do
        total_items = total_items + count
        unique_skus = unique_skus + 1
        key(sku .. ": " .. count .. "\\n")
    end
    
    key("\\n--- SUMMARY ---\\n")
    key("Unique SKUs: " .. unique_skus .. "\\n")
    key("Total Items: " .. total_items .. "\\n")
    
    local session_duration = os.time() - session_stats.session_start
    key("Session Duration: " .. format_duration(session_duration) .. "\\n")
    key("Total Scans: " .. session_stats.total_scans .. "\\n")
    key("SKU Scans: " .. session_stats.sku_items .. "\\n")
    key("Regular Scans: " .. session_stats.regular_items .. "\\n")
    
    key("=============================\\n\\n")
    
    -- Audio feedback
    buzzer_melody("SUCCESS")
    led_blink(2, 3)
    
    log_with_timestamp("Inventory report exported")
end

function clear_inventory()
    local item_count = 0
    for sku, count in pairs(inventory) do
        item_count = item_count + count
    end
    
    if item_count == 0 then
        key("Inventory already empty\\n")
        beep(100)
        return
    end
    
    -- Clear all data
    inventory = {}
    session_stats.sku_items = 0
    session_stats.regular_items = 0
    session_stats.total_scans = 0
    session_stats.session_start = os.time()
    
    key("INVENTORY CLEARED (" .. item_count .. " items removed)\\n")
    
    -- Visual feedback
    led_on(4)  -- Red LED
    buzzer_melody("WARNING")
    sleep(500)
    led_off(4)
    update_led_status()
    
    log_with_timestamp("Inventory cleared - " .. item_count .. " items removed")
end

function show_session_stats()
    local session_duration = os.time() - session_stats.session_start
    local current_time = os.date("%H:%M:%S")
    
    key("\\n--- SESSION STATS ---\\n")
    key("Current Time: " .. current_time .. "\\n")
    key("Session Duration: " .. format_duration(session_duration) .. "\\n")
    key("Total Scans: " .. session_stats.total_scans .. "\\n")
    key("  SKU Items: " .. session_stats.sku_items .. "\\n")
    key("  Regular Items: " .. session_stats.regular_items .. "\\n")
    
    if session_stats.last_scan_time > 0 then
        local time_since_last = os.time() - session_stats.last_scan_time
        key("Last Scan: " .. format_duration(time_since_last) .. " ago\\n")
    end
    
    local unique_skus = 0
    local total_inventory = 0
    for sku, count in pairs(inventory) do
        unique_skus = unique_skus + 1
        total_inventory = total_inventory + count
    end
    
    key("Inventory: " .. unique_skus .. " SKUs, " .. total_inventory .. " items\\n")
    key("--------------------\\n\\n")
    
    beep(200)
    led_blink(3, 2)
    
    log_with_timestamp("Session stats displayed")
end

function handle_number_key(number)
    -- Number keys for quick inventory queries
    local sku_search = config.sku_prefix .. string.format("%05d", number)
    
    if inventory[sku_search] then
        key("QUERY: " .. sku_search .. " = " .. inventory[sku_search] .. " items\\n")
        led_blink(2, 2)
    else
        key("QUERY: " .. sku_search .. " = NOT FOUND\\n")
        led_blink(4, 1)
    end
    
    beep(100)
    log_with_timestamp("Quick query: " .. sku_search)
end

-- System Setup
function setup()
    scanner_enable_lua_processing(true)  -- Take full control of scanner
    
    -- Startup sequence
    key("\\n*** INVENTORY SYSTEM READY ***\\n")
    key("SKU Format: " .. config.sku_prefix .. "XXXXX\\n")
    key("Remove Format: REMOVE:XXXXX\\n")
    key("\\n")
    key("Controls:\\n")
    key("  Key " .. config.export_key .. ": Export Report\\n")
    key("  Key " .. config.clear_key .. ": Clear Inventory\\n")
    key("  Key " .. config.stats_key .. ": Session Stats\\n")
    key("  Keys 0-9: Quick SKU Query\\n")
    key("\\n")
    
    -- LED startup sequence
    for i = 1, 5 do
        led_on(i)
        sleep(100)
    end
    
    sleep(200)
    led_all_off()
    update_led_status()
    
    -- Audio confirmation
    buzzer_melody("START")
    
    log_with_timestamp("=== INVENTORY SYSTEM INITIALIZED ===")
    log_with_timestamp("Session started: " .. os.date("%Y-%m-%d %H:%M:%S"))
end

-- Initialize the system
setup()
'''
    
    return script

def main():
    print("🔧 aRdent ScanPad - Advanced Lua Script QR Generation")
    print("=" * 60)
    
    # Create ScanPad instance
    scanpad = ScanPad()
    
    print("📝 Generating advanced inventory management script...")
    
    try:
        # Create the complex script
        inventory_script = create_inventory_script()
        
        print(f"📊 Script size: {len(inventory_script)} characters")
        print(f"📊 Script lines: {len(inventory_script.split())}")
        
        # Generate QR codes with different fragment sizes for demonstration
        print("\n🔗 Generating QR codes with optimal fragmentation...")
        
        qr_commands = scanpad.qr.create_lua_script_qr(
            inventory_script,
            max_qr_size=800,  # Smaller fragments for better scanning
            compression_level=9  # Maximum compression
        )
        
        # Display detailed information
        first_qr = qr_commands[0]
        metadata = first_qr.metadata
        
        print(f"\n📈 Compression Analysis:")
        print(f"   Original size: {metadata['original_size_bytes']} bytes")
        print(f"   Compressed: {metadata['compressed_size_bytes']} bytes")
        print(f"   Base64: {metadata['base64_size_chars']} characters")
        print(f"   Compression ratio: {metadata['compression_ratio_percent']}%")
        print(f"   Fragments needed: {len(qr_commands)}")
        
        # Create output directory
        output_dir = Path("output/advanced_inventory")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n💾 Saving {len(qr_commands)} QR codes...")
        
        # Save QR codes with detailed information
        for i, qr in enumerate(qr_commands):
            fragment_num = i + 1
            total_fragments = len(qr_commands)
            
            if total_fragments == 1:
                filename = "inventory_system.png"
                print(f"   📱 Single QR: {filename}")
            else:
                is_final = qr.metadata['is_final_fragment']
                filename = f"inventory_system_{fragment_num:02d}_of_{total_fragments:02d}.png"
                
                if is_final:
                    print(f"   📱 Fragment {fragment_num}/{total_fragments} (FINAL): {filename}")
                else:
                    print(f"   📱 Fragment {fragment_num}/{total_fragments}: {filename}")
            
            filepath = output_dir / filename
            qr.save(filepath, size=500, border=8)
            
            # Show fragment details
            qr_size = qr.metadata['qr_size_chars']
            fragment_size = qr.metadata['fragment_size_chars']
            print(f"       └─ QR size: {qr_size} chars, Fragment: {fragment_size} chars")
        
        print(f"\n✅ QR codes saved in: {output_dir.absolute()}")
        
        # Deployment instructions
        print(f"\n📖 Deployment Instructions:")
        print(f"=" * 40)
        print(f"1. Flash the latest firmware to your aRdent ScanPad")
        
        if len(qr_commands) == 1:
            print(f"2. Scan the QR code to deploy the script")
        else:
            print(f"2. Scan QR codes IN ORDER:")
            for i in range(len(qr_commands)):
                fragment_num = i + 1
                is_final = qr_commands[i].metadata['is_final_fragment']
                status = " (EXECUTE)" if is_final else ""
                print(f"   - Fragment {fragment_num}{status}")
        
        print(f"3. The inventory system will start automatically")
        print(f"4. Use the scanner to process SKU: items")
        print(f"5. Use buttons for reports and control")
        
        # Feature summary
        print(f"\n🎯 System Features:")
        print(f"- SKU inventory tracking (SKU:XXXXX format)")
        print(f"- Item removal (REMOVE:XXXXX format)")
        print(f"- Real-time counting and validation")
        print(f"- Export reports (Key 15)")
        print(f"- Clear inventory (Key 14)")
        print(f"- Session statistics (Key 13)")
        print(f"- Quick SKU lookup (Keys 0-9)")
        print(f"- LED status indicators")
        print(f"- Audio feedback system")
        print(f"- Timestamped logging")
        
        # Testing recommendations
        print(f"\n🧪 Testing Recommendations:")
        print(f"1. Test with sample SKU barcodes: SKU:00001, SKU:00002")
        print(f"2. Try removal commands: REMOVE:00001")
        print(f"3. Use buttons to test reporting features")
        print(f"4. Check logs via ESP-IDF monitor")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()