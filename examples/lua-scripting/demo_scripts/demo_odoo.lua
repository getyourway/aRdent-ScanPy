-- =========================================================
--  GS1 "forgeur" pour Odoo : scan produit -> saisie qty -> GS1(01,30)
--  Comportement LED (nouvelle API):
--    - Saisie quantité active: led2("green") FIXE
--    - Après envoi GS1 (A id=3): FLASH led2("cyan"), puis led2_blink("green", 2)
--    - Au prochain scan: leds_stop_blink() puis led2("green")
-- =========================================================

-- Etat courant
local waiting_qty = false
local last_barcode = nil       -- code produit scanné (EAN/GTIN)
local qty_buf = ""             -- quantité saisie ("", "5", "12", ...)
local MAX_QTY_DIGITS = 8       -- AI (30) supporte 8 chiffres

-- =============== Helpers LED (nouvelle API) ===============
local function led_qty_mode()         -- vert fixe pendant la saisie
    leds_stop_blink()
    led2("green")
end

local function led_after_send()       -- flash cyan puis vert clignotant
    leds_stop_blink()
    led2("cyan")
    sleep(150)
    led2("off")
    led2_blink("green", 2)   -- 2 Hz jusqu'au prochain scan
end

local function led_on_new_scan()      -- stop cligno et vert fixe
    leds_stop_blink()
    led2("green")
end
-- =========================================================

-- Helpers data --------------------------------
local function gtin14_from_ean(code)
    if not code then return nil end
    local numeric = tostring(code):gsub("%D", "")
    local len = #numeric
    if len == 0 or len > 14 then
        return nil
    end
    return string.rep("0", 14 - len) .. numeric
end

local function left_pad(num_str, total)
    local s = tostring(num_str or "")
    if #s >= total then return s end
    return string.rep("0", total - #s) .. s
end

local function map_button_to_digit(button_id)
    -- Mapping exact fourni
    if button_id == 0 then return "1" end
    if button_id == 1 then return "2" end
    if button_id == 2 then return "3" end
    if button_id == 4 then return "4" end
    if button_id == 5 then return "5" end
    if button_id == 6 then return "6" end
    if button_id == 8 then return "7" end
    if button_id == 9 then return "8" end
    if button_id == 10 then return "9" end
    if button_id == 13 then return "0" end
    return nil
end

local function reset_state()
    waiting_qty = false
    last_barcode = nil
    qty_buf = ""
    -- on ne change pas l'état LED ici: il est géré par led_after_send() / led_on_new_scan()
end

local function start_qty_mode(barcode)
    waiting_qty = true
    last_barcode = barcode
    qty_buf = ""
    led_qty_mode()  -- led2 verte fixe = saisie active
    log("Saisie quantité pour code: " .. barcode)
end

local function send_gs1(g14, qty_num)
    -- Construit et envoie: 01<GTIN14>30<qty(8)>
    local qty_str = left_pad(qty_num, MAX_QTY_DIGITS)
    local payload = "01" .. g14 .. "30" .. qty_str
    log("Envoi GS1: " .. payload)
    key(payload)
    keycode(KEY_ENTER, 0)   -- Enter pour valider dans Odoo
end

-- =============== Événements ===============

function on_scan(barcode)
    -- Nouveau scan: stop cligno éventuel, repasse en vert fixe
    led_on_new_scan()

    if not barcode or #barcode == 0 then
        melody("error")
        log("Scan vide")
        return
    end

    if waiting_qty then
        melody("warning")
        log("Nouveau scan reçu pendant saisie, on redémarre la saisie.")
    end

    start_qty_mode(barcode)
end

function on_button(button_id)
    -- Touche A (id=3) = ENVOI GS1
    if button_id == 3 then
        if not waiting_qty or not last_barcode then
            melody("warning")
            return
        end

        local qty_to_use = qty_buf
        if qty_to_use == "" then qty_to_use = "1" end

        if #qty_to_use > MAX_QTY_DIGITS then
            melody("error")
            log("Quantité trop longue: " .. qty_to_use)
            reset_state()
            return
        end

        local g14 = gtin14_from_ean(last_barcode)
        if not g14 then
            melody("error")
            log("Code produit incompatible (attendu <=14 chiffres): " .. tostring(last_barcode))
            reset_state()
            return
        end

        -- Envoi GS1 + feedback LED
        send_gs1(g14, qty_to_use)
        led_after_send()   -- flash cyan puis clignotement vert
        reset_state()
        return
    end

    -- Si pas en mode saisie, ignorer les touches
    if not waiting_qty then
        return
    end

    -- Accumulation chiffres
    local digit = map_button_to_digit(button_id)
    if digit then
        if #qty_buf < MAX_QTY_DIGITS then
            qty_buf = qty_buf .. digit
            log("Quantité en cours: " .. qty_buf)
            -- LED reste verte fixe durant la saisie (pas de blink ici)
        else
            melody("warning")
        end
        return
    end

    -- Autres touches ignorées
end

-- =============== Setup ===============

function setup()
    log("=== Script GS1 Quantité pour Odoo - démarrage ===")
    scanner_enable_lua_processing(true)   -- Intercepter les scans
    for i=0,19 do
        key_enable(i, false)
    end
    -- État visuel au boot: tout off
    leds_stop_blink()
    leds_off()
    log("Prêt: scanne un produit, saisis la quantité (A=id=3 pour envoyer).")
end

setup()