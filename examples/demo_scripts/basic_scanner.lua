-- Basic Scanner Enhancement Script
-- Adds prefixes and visual feedback to all scanned barcodes

function on_scan(barcode)
    -- Add timestamp and formatting
    local timestamp = os.date("%H:%M:%S")
    key("[" .. timestamp .. "] " .. barcode .. "\n")
    
    -- Visual feedback based on barcode length
    if string.len(barcode) > 15 then
        led_blink(2, 3)  -- Long barcode - green blink
        buzzer_melody("SUCCESS")
    else
        led_on(1)        -- Short barcode - simple LED
        beep(100)
        sleep(200)
        led_off(1)
    end
    
    log("Processed: " .. barcode)
end

function setup()
    scanner_set_passthrough(false)
    key("=== ENHANCED SCANNER ACTIVE ===\n")
    log("Basic scanner enhancement loaded")
end

setup()