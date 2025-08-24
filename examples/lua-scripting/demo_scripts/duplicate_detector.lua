-- Reference Barcode Validator
local reference = nil

function setup()
    led_all_off()  -- Start with all LEDs off
end

function on_scan(barcode)
    -- Send barcode to HID (normal behavior)
    key(barcode)
    key("\n")
    
    if reference == nil then
        -- First scan: set as reference
        led_all_off()
        led(3, true)  -- Green LED 3 for reference set
        reference = barcode
        return
    end
    
    -- Second scan: compare with reference
    if barcode == reference then
        -- Match: all green LEDs (1, 3, 9) + success sound
        led_all_off()
        led(1, true)  -- Green LED 1
        led(3, true)  -- Green LED 3  
        led(9, true)  -- Green LED 9
        melody("confirm")
    else
        -- Different: red LED (2) + warning sound
        led_all_off()
        led(2, true)  -- Red LED 2
        melody("error")
    end
    
    -- Reset reference for next cycle
    reference = nil
end

function on_key(key_id)
    if key_id == 15 then
        -- Clear reference and all LEDs
        reference = nil
        led_all_off()
    end
end

setup()