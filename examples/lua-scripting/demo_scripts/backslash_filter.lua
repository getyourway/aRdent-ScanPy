-- Backslash Filter Script
-- Intercepts barcodes, removes backslash+n sequences, then transmits clean barcode

function setup()
    scanner_set_passthrough(false)  -- We control transmission
    led_all_off()
    led(2, true)  -- Green LED 2 to show filter is active
    print("Backslash filter active - removing \\n sequences")
end

function on_scan(barcode)
    print("Raw barcode: " .. barcode)
    
    -- Remove all occurrences of backslash followed by 'n' (\\n sequences)
    local clean_barcode = string.gsub(barcode, "\\n", "")
    
    -- Also remove literal newline characters if present
    clean_barcode = string.gsub(clean_barcode, "\n", "")
    clean_barcode = string.gsub(clean_barcode, "\r", "")
    
    print("Cleaned barcode: " .. clean_barcode)
    
    -- Visual feedback - flash LED 3 when processing
    led(3, true)
    
    -- Send the cleaned barcode via HID
    key(clean_barcode)
    
    -- Brief LED flash to confirm transmission
    led(3, false)
    led(1, true)  -- Green LED 1 flash for success
    
    -- Reset LED after short delay (simulated with another scan)
    led(1, false)
end