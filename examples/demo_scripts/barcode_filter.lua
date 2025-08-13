-- Barcode Filter - Only allow barcodes starting with "203"
-- Intercepts HID transmission and filters based on prefix

function setup()
    -- Disable HID passthrough - we control transmission
    scanner_set_passthrough(false)
    led_all_off()
end

function on_scan(barcode)
    -- Check if barcode starts with "203"
    if string.sub(barcode, 1, 3) == "203" then
        -- Valid barcode - send to HID
        led_all_off()
        led(3, true)  -- Green LED 3
        key(barcode)
        key("\n")
    else
        -- Invalid barcode - block transmission
        led_all_off()
        led(2, true)  -- Red LED 2
        melody("error")
        -- Don't send barcode to HID
    end
end

function on_key(key_id)
    if key_id == 15 then
        -- Reset filter (re-enable passthrough)
        scanner_set_passthrough(true)
        led_all_off()
    end
end

setup()