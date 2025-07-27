# aRdent ScanPad Python Examples

Collection complète d'exemples d'utilisation de la librairie Python `ardent_scanpad`.

## 🚀 Démarrage Rapide

```bash
# Installer la librairie
pip install bleak

# Lancer un exemple
cd tools/python-library/examples
python3 basic_led_demo.py
```

## 📁 Exemples Disponibles

### 1. 🎮 **scanpad_interactive.py** - Terminal Interactif Complet
**Application complète pour tester toutes les fonctionnalités**

```bash
python3 scanpad_interactive.py
```

- Snapshot complet de l'appareil au démarrage
- Menu interactif pour tous les contrôles
- Configuration avancée des touches (batch mode)
- Tests de tous les périphériques (LEDs, buzzer, etc.)
- Paramètres de l'appareil (orientation, langue, auto-shutdown)

→ [Documentation détaillée](README_INTERACTIVE.md)

### 2. 💡 **basic_led_demo.py** - Contrôle des LEDs
**Démonstration des fonctionnalités LED**

```bash
python3 basic_led_demo.py
```

- Contrôle individuel des LEDs
- Couleurs RGB (LEDs 3-5)
- Effets de clignotement
- Contrôle global (all on/off)

### 3. ⌨️ **simple_key_config.py** - Configuration des Touches
**Configuration basique des touches**

```bash
python3 simple_key_config.py
```

- Actions UTF-8 simples
- Raccourcis clavier (Ctrl+C)
- Contrôles média (Volume)
- Séquences d'actions avec délais
- Configuration des boutons externes

### 4. 📱 **device_info_demo.py** - Informations de l'Appareil
**Récupération des informations système**

```bash
python3 device_info_demo.py
```

- Device Information Service (DIS)
- État de la batterie
- Configuration (orientation, langue)
- État des LEDs
- Résumé des touches configurées

### 5. 🔊 **buzzer_demo.py** - Contrôle Audio
**Démonstration des capacités audio**

```bash
python3 buzzer_demo.py
```

- Beeps simples et multiples
- Contrôle du volume
- Mélodies prédéfinies
- Patterns rythmiques personnalisés
- Feedback interactif simulé

### 6. 📝 **basic_usage.py** - Exemple Basique (Hérité)
Configuration simple de touches :
- Configuration texte
- Raccourcis clavier (Ctrl+C, Ctrl+V)  
- Contrôles média (Volume, Play/Pause)
- Touches de fonction et Enter
- Sauvegarde/restauration de configuration

```bash
python3 basic_usage.py
```

## 🎯 Cas d'Usage par Exemple

### Débutant
- **device_info_demo.py** → Comprendre votre appareil
- **basic_led_demo.py** → Premiers contrôles

### Développement d'Applications
- **simple_key_config.py** → Configurer des touches pour votre app
- **buzzer_demo.py** → Ajouter du feedback audio

### Test et Validation
- **scanpad_interactive.py** → Test complet de tous les composants

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