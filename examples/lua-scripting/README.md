# 🛠️ Lua Scripting for aRdent ScanPad

Scripts Lua et génération de QR codes pour programmation avancée de l'aRdent ScanPad.

> **Puissance** : Les scripts Lua permettent une logique métier personnalisée directement sur l'appareil !

## 🚀 Scripts de Génération QR

### 📝 **lua_qr_simple.py** - Génération QR Simple
**Génération simple de QR codes depuis fichier Lua**

```bash
python lua_qr_simple.py
```

**Fonctionnalités** :
- Charge automatiquement `lua_script.lua` du même répertoire
- Fragmentation automatique multi-QR si nécessaire
- Compression zlib + base64 optimisée
- Noms de fichiers descriptifs (`lua_script_part_1_of_3.png`)
- Instructions de déploiement intégrées

**Parfait pour** : Tests rapides, développement de scripts

---

### 🔧 **lua_qr_advanced.py** - Génération QR Avancée  
**Génération avancée avec options de customisation**

```bash
python lua_qr_advanced.py
```

**Fonctionnalités avancées** :
- Sélection interactive de fichier Lua
- Options de compression configurables (1-9)
- Taille QR personnalisable pour optimiser lisibilité
- Métadonnées détaillées (compression, fragments, statistiques)
- Sauvegarde batch avec options de nommage
- Preview et validation avant génération

**Parfait pour** : Production, déploiement en masse, optimisation

---

### 🗑️ **generate_clear_lua_qr.py** - Nettoyage Script
**QR code pour effacer le script Lua actuellement chargé**

```bash
python generate_clear_lua_qr.py
```

**Fonctionnalités** :
- Génère QR de commande `$CMD:DEV:60CMD$` (Lua Clear)
- Supprime le script Lua de la mémoire device
- Restaure le comportement par défaut
- Sauvegarde automatique `clear_lua_script.png`

**Parfait pour** : Debugging, reset, changement de script

## 📜 Scripts Lua d'Exemple

### 📁 **demo_scripts/** - Collection de Scripts

#### 🔍 **basic_scanner.lua** - Scanner de Base
**Script fondamental pour traitement des scans**

```lua
function on_scan(data)
    print("Scanned: " .. data)
    led(1, true)  -- LED verte ON
    beep()        -- Feedback audio
    led(1, false) -- LED verte OFF
    return true   -- Continue processing
end
```

**Cas d'usage** : Point de départ, debugging, tests simples

---

#### ⌨️ **keyboard_tester.lua** - Testeur de Clavier
**Validation et test des touches programmables**

```lua
function on_key_press(key_id)
    print("Key " .. key_id .. " pressed")
    
    -- Feedback différent par zone
    if key_id < 4 then
        led(2, true)  -- LED 2 pour ligne du haut
        play_melody("SUCCESS")
    elseif key_id < 8 then  
        led(3, true)  -- LED 3 pour 2ème ligne
        beep(2)
    end
    
    return true
end
```

**Cas d'usage** : Tests hardware, validation layout clavier

---

#### 📊 **barcode_filter.lua** - Filtre Codes-Barres
**Validation et filtrage de codes-barres selon patterns**

```lua
function on_scan(data)
    -- Validation longueur EAN-13
    if string.len(data) == 13 and string.match(data, "^%d+$") then
        led(4, true)   -- LED rouge = valide
        play_melody("CONFIRM")
        print("Valid EAN-13: " .. data)
        return true
    else
        led(5, true)   -- LED bleue = invalide  
        play_melody("ERROR")
        print("Invalid barcode: " .. data)
        return false   -- Reject scan
    end
end
```

**Cas d'usage** : Validation métier, contrôle qualité, filtrage

---

#### 🔄 **duplicate_detector.lua** - Détecteur de Doublons
**Détection et prévention des scans en double**

```lua
local history = {}
local max_history = 10

function on_scan(data)
    -- Vérifier l'historique
    for i = 1, #history do
        if history[i] == data then
            -- Doublon détecté !
            led(4, true)  -- Rouge
            play_melody("WARNING")
            print("DUPLICATE: " .. data)
            return false  -- Rejeter
        end
    end
    
    -- Nouveau scan - ajouter à l'historique
    table.insert(history, 1, data)
    if #history > max_history then
        table.remove(history)  -- Supprimer le plus ancien
    end
    
    led(2, true)  -- Vert = nouveau
    play_melody("SUCCESS") 
    print("NEW: " .. data)
    return true
end
```

**Cas d'usage** : Inventaire, contrôle stock, prévention erreurs

---

#### 🔧 **backslash_filter.lua** - Filtre Backslash
**Nettoyage et normalisation des chemins Windows**

```lua
function on_scan(data)
    -- Remplacer backslashes par forward slashes
    local cleaned = string.gsub(data, "\\", "/")
    
    if cleaned ~= data then
        print("Cleaned path: " .. cleaned)
        led(3, true)  -- Jaune = modifié
        beep()
        
        -- Envoyer la version nettoyée
        send_hid_text(cleaned)
        return false  -- Ne pas envoyer l'original
    else
        print("Path OK: " .. data)  
        led(2, true)  -- Vert = OK
        return true   -- Envoyer tel quel
    end
end
```

**Cas d'usage** : Intégration Windows/Unix, normalisation paths

## 🔧 API Lua Disponible

### Contrôle LEDs
```lua
led(id, state)              -- LED ON/OFF (id: 1-9, state: true/false)
led_blink(id, frequency)    -- LED Blink (frequency: 0.1-20.0 Hz)
led_stop_blink(id)          -- Arrêter blink
all_leds_off()             -- Toutes LEDs OFF
```

### Contrôle Audio  
```lua
beep()                     -- Beep simple
beep(count)               -- Beeps multiples  
play_melody(name)         -- Mélodies ("SUCCESS", "ERROR", "WARNING", etc.)
set_volume(level)         -- Volume 0-100
```

### Interaction Clavier
```lua
send_hid_text(text)       -- Envoyer texte via HID
send_hid_key(keycode, modifiers)  -- Envoyer touche HID
send_consumer_key(code)   -- Contrôles media/consumer
```

### Fonctions Système
```lua
print(message)            -- Debug output
wait(milliseconds)        -- Pause/delay
get_battery_level()       -- Niveau batterie (%)
```

### Callbacks Événements
```lua
function on_scan(data)           -- Scan reçu
function on_key_press(key_id)    -- Touche pressée (0-19)
function on_button_press(btn_id) -- Bouton externe (power, scan trigger)
function on_battery_low()        -- Batterie faible
function on_startup()           -- Démarrage script
```

## 📋 Guide de Développement

### 1. Structure de Script Recommandée
```lua
-- Script Lua pour aRdent ScanPad
-- Description et cas d'usage

-- Variables globales
local config = {
    max_history = 10,
    led_feedback = true
}

-- Fonctions utilitaires  
function validate_data(data)
    -- Logique de validation
    return true/false
end

-- Callbacks principaux
function on_startup()
    print("Script loaded successfully")
    led(2, true)  -- LED verte = ready
end

function on_scan(data)
    if validate_data(data) then
        -- Traitement normal
        return true
    else
        -- Rejet
        return false  
    end
end
```

### 2. Gestion des Erreurs
```lua
function on_scan(data)
    -- Protection contre erreurs
    local success, result = pcall(function()
        -- Code potentiellement dangereux
        return process_complex_data(data)
    end)
    
    if success then
        print("Processed: " .. result)
        return true
    else
        print("Error processing: " .. data)
        led(4, true)  -- Rouge = erreur
        return false
    end
end
```

### 3. Configuration Persistante
```lua
-- Simuler persistence avec variables globales
local settings = {
    filter_enabled = true,
    max_length = 50,
    pattern = "^%d+$"
}

function on_scan(data)
    if settings.filter_enabled then
        -- Appliquer filtre
    end
    -- ...
end
```

## 🚀 Déploiement

### Via QR Code (Recommandé)
```bash
# 1. Développer script
vim my_script.lua

# 2. Générer QR codes
python lua_qr_simple.py

# 3. Scanner QR codes dans l'ordre
#    Fragment 1, 2, ..., Final (Execute)
```

### Via Bluetooth (Development)
```python
# Déploiement direct via BLE (développement uniquement)
import asyncio
from ardent_scanpad import ScanPad

async def deploy_script():
    async with ScanPad() as scanpad:
        with open('script.lua', 'r') as f:
            script_content = f.read()
        
        await scanpad.device.lua.deploy_script(script_content)
        print("Script deployed via BLE")

asyncio.run(deploy_script())
```

## 💡 Conseils de Développement

- **Testez graduellement** : Commencez par `basic_scanner.lua`
- **Gérez les erreurs** : Utilisez `pcall()` pour code complexe  
- **Feedback utilisateur** : LEDs + audio pour status visuel
- **Optimisez la taille** : Scripts < 5KB se déploient en 1 QR
- **Documentez les callbacks** : Précisez quelles fonctions sont utilisées
- **Utilisez print()** : Pour debugging et logs développement

## 🔗 Liens Utiles

- [API Lua complète](../../main/components/lua_engine/)
- [Constantes HID/Consumer](../../ardent_scanpad/utils/constants.py)
- [Génération QR](../qr-commands/)
- [Tests Bluetooth](../bluetooth/)