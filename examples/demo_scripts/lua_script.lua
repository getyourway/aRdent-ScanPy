-- aRdent ScanPad Lua Script Example
-- This script demonstrates barcode processing with LED feedback

function on_scan(data)
    print("Barcode scanned: " .. data)
    
    -- Turn on LED 1 for any scan
    led(1, true)
    
    -- Different LED patterns based on barcode content
    if string.match(data, "^%d+$") then
        -- Numeric barcode - green LEDs
        print("Numeric barcode detected")
        led(2, true)
        beep()
    elseif string.len(data) > 10 then
        -- Long barcode - blue LED
        print("Long barcode detected")
        led(5, true)
        beep()
        beep()
    else
        -- Other barcodes - red LED  
        print("Text barcode detected")
        led(4, true)
        beep()
        beep()
        beep()
    end
end

function on_button(button_id)
    print("Button " .. button_id .. " pressed")
    
    -- Turn off all LEDs when any button is pressed
    for i = 1, 5 do
        led(i, false)
    end
    
    -- Quick beep feedback
    beep()
end

-- Initialization
print("Barcode processing script loaded successfully")
print("Ready to scan barcodes and process button presses")