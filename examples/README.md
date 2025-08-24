# 📚 aRdent ScanPad Python Examples

Collection complète d'exemples d'utilisation de la librairie Python `ardent_scanpad`, organisée par fonctionnalités.

## 🚀 Démarrage Rapide

```bash
# Installer les dépendances
pip install bleak qrcode[pil]

# Lancer un exemple Bluetooth
cd tools/python-library/examples/bluetooth
python3 scanpad_interactive.py

# Ou générer des QR codes
cd ../qr-commands  
python3 scanpad_qrcode_interactive.py
```

## 📁 Structure par Fonctionnalités

### 📡 **bluetooth/** - Contrôle BLE en Temps Réel
**Exemples nécessitant une connexion Bluetooth avec l'appareil**

```bash
cd bluetooth/
python3 scanpad_interactive.py  # Terminal interactif complet
```

**8 scripts disponibles** :
- 🎮 `scanpad_interactive.py` - Terminal interactif complet avec tous les contrôles
- 🔗 `connection_demo.py` - Démonstration de connexion BLE
- 🔍 `device_discovery_demo.py` - Découverte et sélection d'appareils  
- 📝 `basic_usage.py` - Configuration simple et rapide
- 💡 `basic_led_demo.py` - Contrôle complet des LEDs
- 🔊 `buzzer_demo.py` - Contrôle audio et mélodies
- ⌨️ `simple_key_config.py` - Configuration des touches
- 🧪 `test_clear_functionality.py` - Tests et validation

**Idéal pour** : Développement d'applications, tests en temps réel, debugging

→ [Documentation complète](bluetooth/README.md)

---

### 📱 **qr-commands/** - Génération QR (Sans BLE)
**Génération de QR codes pour configurer l'appareil sans Bluetooth**

```bash
cd qr-commands/
python3 scanpad_qrcode_interactive.py  # Terminal QR interactif
# QR codes générés → qr-commands/output/
```

**4 générateurs disponibles** :
- 🎮 `scanpad_qrcode_interactive.py` - Terminal QR complet avec menus
- 🔧 `generate_backslash_filter_qr.py` - QR pour filtre backslash
- 📊 `generate_barcode_filter_qr.py` - QR pour filtre codes-barres
- 🔄 `generate_duplicate_detector_qr.py` - QR pour détecteur doublons

**Idéal pour** : Applications web, documentation, déploiement à distance

→ [Documentation complète](qr-commands/README.md)

---

### 🛠️ **lua-scripting/** - Scripts Lua Avancés
**Scripts Lua personnalisés et génération QR pour logique métier**

```bash
cd lua-scripting/
python3 lua_qr_simple.py  # QR depuis fichier Lua
# QR codes générés → lua-scripting/output/
```

**3 générateurs + 5 scripts d'exemple** :
- 📝 `lua_qr_simple.py` - Génération QR simple depuis fichier
- 🔧 `lua_qr_advanced.py` - Génération QR avec options avancées  
- 🗑️ `generate_clear_lua_qr.py` - QR pour nettoyer scripts
- 📁 `demo_scripts/` - Collection de scripts Lua prêts à l'emploi

**Idéal pour** : Logique métier complexe, automatisation, workflows spécialisés

→ [Documentation complète](lua-scripting/README.md)

## 🎯 Guide par Cas d'Usage

### 🚀 Je découvre l'aRdent ScanPad
1. `bluetooth/connection_demo.py` → Première connexion
2. `bluetooth/basic_led_demo.py` → Contrôles de base
3. `bluetooth/scanpad_interactive.py` → Exploration complète

### 💻 Je développe une application
1. `bluetooth/simple_key_config.py` → Configuration touches
2. `bluetooth/buzzer_demo.py` → Feedback audio
3. `qr-commands/scanpad_qrcode_interactive.py` → QR pour GUI

### 🏭 Je déploie en production
1. `qr-commands/` → Configuration sans BLE
2. `lua-scripting/` → Logique métier avancée
3. `bluetooth/test_clear_functionality.py` → Validation

## 🔧 Structure des Exemples

Chaque exemple suit la même structure :

```python
import asyncio
from ardent_scanpad import ScanPad

async def main():
    # 1. Connexion
    scanpad = ScanPad()
    await scanpad.connect()
    
    try:
        # 2. Opérations
        await scanpad.device.led.turn_on(1)
        # ...
        
    except Exception as e:
        print(f"Erreur: {e}")
    
    finally:
        # 3. Déconnexion
        await scanpad.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## 📚 API Quick Reference

### Connexion
```python
scanpad = ScanPad()
await scanpad.connect()  # Auto-connect au premier appareil
await scanpad.disconnect()
```

### LEDs
```python
await scanpad.device.led.turn_on(led_id)
await scanpad.device.led.turn_off(led_id)
await scanpad.device.led.blink(led_id, frequency=2.0)
await scanpad.device.led.stop_blink(led_id)
await scanpad.device.led.all_off()
state = await scanpad.device.led.get_state(led_id)
```

### Buzzer
```python
await scanpad.device.buzzer.beep()
await scanpad.device.buzzer.set_volume(0-100)
await scanpad.device.buzzer.play_melody("SUCCESS")
```

### Configuration des Touches
```python
# Créer des actions
text_action = scanpad.keys.create_text_action("Hello")
hid_action = scanpad.keys.create_hid_action(HIDKeyCodes.ENTER)
consumer_action = scanpad.keys.create_consumer_action(ConsumerCodes.VOLUME_UP)

# Configurer une touche
await scanpad.keys.set_key_config(key_id, [action1, action2, ...])
config = await scanpad.keys.get_key_config(key_id)
await scanpad.keys.save_config()
```

### Informations de l'Appareil
```python
info = await scanpad.device.get_device_info()
battery = await scanpad.device.get_battery_level()
orientation = await scanpad.device.get_orientation()
language = await scanpad.device.get_language()
```

## Requirements

- aRdent ScanPad device powered on and discoverable
- Python 3.8+ with `bleak` library installed
- Device should be in pairing mode for first connection

## 💡 Conseils

- **Toujours appeler `disconnect()`** dans un bloc `finally`
- **Gérer les exceptions** pour une expérience utilisateur robuste
- **Utiliser `await asyncio.sleep()`** entre les opérations pour éviter la surcharge
- **Sauvegarder les configurations** avec `save_config()` pour les persister

## 🔗 Liens Utiles

- [Documentation complète de la librairie](../README.md)
- [Constants et codes utiles](../ardent_scanpad/utils/constants.py)
- [Tests de validation](../../test-scripts/)