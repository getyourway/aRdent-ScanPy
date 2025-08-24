-- Keyboard Matrix Tester Script
-- Tests all keys with visual and audio feedback

local key_press_count = {}

function on_button(button_id)
    -- Initialize counter if needed
    if not key_press_count[button_id] then
        key_press_count[button_id] = 0
    end
    
    key_press_count[button_id] = key_press_count[button_id] + 1
    local count = key_press_count[button_id]
    
    -- Send key info to output
    key("Key " .. button_id .. " pressed " .. count .. " time(s)\n")
    
    -- Visual feedback pattern based on key position
    if button_id >= 0 and button_id <= 3 then
        -- Top row - LED 1 (green)
        led_on(1)
        beep(100)
    elseif button_id >= 4 and button_id <= 7 then
        -- Second row - LED 2 (green)
        led_on(2) 
        beep(150)
    elseif button_id >= 8 and button_id <= 11 then
        -- Third row - LED 3 (green)
        led_on(3)
        beep(200)
    elseif button_id >= 12 and button_id <= 15 then
        -- Bottom row - LED 4 (red)
        led_on(4)
        beep(250)
    end
    
    -- Turn off LED after delay
    sleep(300)
    led_off(1)
    led_off(2)
    led_off(3)
    led_off(4)
    
    log("Key " .. button_id .. " test - press #" .. count)
end

function on_scan(barcode)
    -- Special command to show statistics
    if barcode == "STATS" then
        show_stats()
    elseif barcode == "RESET" then
        reset_counters()
    else
        key("Scan: " .. barcode .. " (use STATS or RESET)\n")
        beep(50)
    end
end

function show_stats()
    key("\n=== KEY PRESS STATISTICS ===\n")
    
    local total_presses = 0
    for key_id = 0, 15 do
        local count = key_press_count[key_id] or 0
        if count > 0 then
            key("Key " .. key_id .. ": " .. count .. " presses\n")
        end
        total_presses = total_presses + count
    end
    
    key("Total presses: " .. total_presses .. "\n")
    key("============================\n\n")
    
    -- Celebration for reaching milestones
    if total_presses >= 100 then
        buzzer_melody("SUCCESS")
        led_blink(2, 5)
    elseif total_presses >= 50 then
        buzzer_melody("CONFIRM")
        led_blink(3, 3)
    else
        beep(200)
    end
end

function reset_counters()
    key_press_count = {}
    key("Key press counters reset!\n")
    
    -- Visual reset confirmation
    for i = 1, 5 do
        led_on(i)
    end
    buzzer_melody("WARNING")
    sleep(500)
    led_all_off()
    
    log("Key press counters reset")
end

function setup()
    scanner_set_passthrough(false)
    key("\n=== KEYBOARD MATRIX TESTER ===\n")
    key("Press any key to test responsiveness\n")
    key("Scan 'STATS' for statistics\n")
    key("Scan 'RESET' to clear counters\n")
    key("==============================\n\n")
    
    -- Startup LED sequence
    for i = 1, 5 do
        led_on(i)
        sleep(100)
    end
    led_all_off()
    
    buzzer_melody("START")
    log("Keyboard tester initialized")
end

setup()