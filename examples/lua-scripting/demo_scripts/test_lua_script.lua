-- Script de test pour aRdent ScanPad
-- Démontre les fonctionnalités de base

print("Script Lua chargé avec succès!")

function on_scan(data)
    print("Données scannées: " .. data)
    
    -- Contrôler les LEDs
    led(1, true)  -- Allumer LED 1 (verte)
    led(4, true)  -- Allumer LED 4 (rouge)
    
    -- Jouer un son
    beep()
    
    -- Attendre un peu puis éteindre
    wait(1000)  -- 1 seconde
    led(1, false)
    led(4, false)
    
    return true
end

print("Fonctions définies - prêt à scanner!")