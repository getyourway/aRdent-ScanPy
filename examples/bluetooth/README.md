# 📡 Bluetooth Live Control Examples

Exemples pour contrôler l'aRdent ScanPad en temps réel via Bluetooth Low Energy (BLE).

> **Prérequis** : Appareil allumé et découvrable, Python 3.8+ avec `bleak` installé.

## 🚀 Scripts Disponibles

### 🎮 **scanpad_interactive.py** - Terminal Interactif Complet
**Application complète pour tester toutes les fonctionnalités**

```bash
python scanpad_interactive.py
```

**Fonctionnalités** :
- Snapshot complet de l'appareil au démarrage
- Menu interactif pour tous les contrôles
- Configuration avancée des touches (batch mode)
- Tests de tous les périphériques (LEDs, buzzer, etc.)
- Paramètres de l'appareil (orientation, langue, auto-shutdown)

**Idéal pour** : Tests complets, validation, développement

---

### 🔗 **connection_demo.py** - Démonstration de Connexion
**Apprendre les bases de la connexion BLE**

```bash
python connection_demo.py
```

**Fonctionnalités** :
- Connexion automatique au premier appareil
- Gestion des erreurs de connexion
- Informations de base de l'appareil
- Pattern de connexion/déconnexion propre

**Idéal pour** : Premiers pas, comprendre la connexion

---

### 🔍 **device_discovery_demo.py** - Découverte d'Appareils
**Scanner et lister les appareils aRdent disponibles**

```bash
python device_discovery_demo.py
```

**Fonctionnalités** :
- Scan des appareils BLE disponibles
- Filtrage par nom et services
- Informations détaillées (RSSI, adresse MAC)
- Sélection d'appareil spécifique

**Idéal pour** : Environnements multi-appareils

---

### 📝 **basic_usage.py** - Exemple de Base
**Configuration simple et rapide des touches**

```bash
python basic_usage.py
```

**Fonctionnalités** :
- Configuration texte simple ("Hello", "World!")
- Raccourcis clavier (Ctrl+C, Ctrl+V)
- Contrôles média (Volume, Play/Pause)
- Touches de fonction et Enter
- Sauvegarde/restauration de configuration

**Idéal pour** : Premiers développements, prototypage rapide

---

### 💡 **basic_led_demo.py** - Contrôle des LEDs
**Démonstration complète des fonctionnalités LED**

```bash
python basic_led_demo.py
```

**Fonctionnalités** :
- Contrôle individuel des LEDs (1-9)
- Couleurs et effets RGB
- Modes de clignotement avec fréquences
- Contrôle global (all on/off)
- États et statuts en temps réel

**Idéal pour** : Feedback visuel, notifications, debugging

---

### 🔊 **buzzer_demo.py** - Contrôle Audio
**Démonstration des capacités audio et feedback sonore**

```bash
python buzzer_demo.py
```

**Fonctionnalités** :
- Beeps simples et multiples
- Contrôle du volume (0-100)
- Mélodies prédéfinies (SUCCESS, ERROR, WARNING, etc.)
- Patterns rythmiques personnalisés
- Feedback interactif simulé

**Idéal pour** : Feedback audio, notifications, UX

---

### ⌨️ **simple_key_config.py** - Configuration de Touches
**Configuration basique mais complète des touches et boutons**

```bash
python simple_key_config.py
```

**Fonctionnalités** :
- Actions UTF-8 simples avec support international
- Raccourcis clavier avec modificateurs
- Contrôles média et consumer controls
- Séquences d'actions avec délais
- Configuration des boutons externes
- Sauvegarde persistante

**Idéal pour** : Applications métier, raccourcis personnalisés

---

### 🧪 **test_clear_functionality.py** - Tests de Fonctionnalités
**Tests et validation des fonctionnalités de base**

```bash
python test_clear_functionality.py
```

**Fonctionnalités** :
- Tests automatisés des LEDs
- Validation du buzzer
- Tests de configuration des touches
- Clear/reset des configurations
- Rapport de tests détaillé

**Idéal pour** : Validation, tests automatisés, CI/CD

## 🔧 Structure Commune

Tous les exemples suivent le même pattern :

```python
import asyncio
from ardent_scanpad import ScanPad

async def main():
    # 1. Connexion
    async with ScanPad() as scanpad:
        print(f"✅ Connected to: {scanpad.device_info['name']}")
        
        # 2. Opérations
        await scanpad.device.led.turn_on(1)
        await scanpad.device.buzzer.beep()
        
        # 3. Déconnexion automatique (context manager)

if __name__ == "__main__":
    asyncio.run(main())
```

## 📚 API Quick Reference

### Connexion & Device Info
```python
scanpad = ScanPad()
await scanpad.connect()  # ou utiliser async with
info = await scanpad.device.get_device_info()
battery = await scanpad.device.get_battery_level()
```

### Contrôle LEDs
```python
await scanpad.device.led.turn_on(led_id)
await scanpad.device.led.turn_off(led_id) 
await scanpad.device.led.blink(led_id, frequency=2.0)
await scanpad.device.led.all_off()
```

### Contrôle Audio
```python
await scanpad.device.buzzer.beep()
await scanpad.device.buzzer.set_volume(75)
await scanpad.device.buzzer.play_melody("SUCCESS")
```

### Configuration Touches
```python
# Actions de base
text_action = scanpad.keys.create_text_action("Hello")
hid_action = scanpad.keys.create_hid_action(HIDKeyCodes.ENTER)
consumer_action = scanpad.keys.create_consumer_action(ConsumerCodes.VOLUME_UP)

# Configuration
await scanpad.keys.set_key_config(key_id, [action1, action2])
await scanpad.keys.save_config()
```

## 💡 Conseils de Développement

- **Utilisez `async with ScanPad()`** pour gestion automatique connexion/déconnexion
- **Gérez les exceptions** pour une expérience utilisateur robuste
- **Ajoutez des délais** (`await asyncio.sleep()`) entre opérations intensives
- **Sauvegardez les configurations** avec `save_config()` pour les persister
- **Testez la déconnexion** et reconnexion automatique dans vos apps

## 🔗 Liens Utiles

- [Constants et codes HID](../ardent_scanpad/utils/constants.py)
- [Documentation complète API](../../README.md)
- [Exemples QR codes](../qr-commands/)
- [Scripts Lua](../lua-scripting/)