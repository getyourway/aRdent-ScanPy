# Guide de Migration - API de Testing

Ce guide explique comment migrer tes test-scripts de l'ancienne API avec `_force` vers la nouvelle API de testing.

## Changements dans l'API Publique

### ❌ AVANT (avec _force dans l'API publique)
```python
from ardent_scanpad import ScanPad

async with ScanPad() as device:
    # Tests normaux
    await device.device.led.turn_on(1)
    
    # Tests avec validation bypassée (EXPOSAIT _force publiquement)
    result = await device.device.led.turn_on(-1, _force=True)
    assert result == False  # ESP32 devrait rejeter
```

### ✅ APRÈS (API publique propre + API de test séparée)
```python
from ardent_scanpad.testing import ScanPadTesting

async with ScanPadTesting() as device:
    # Tests normaux (API identique)
    await device.device.led.turn_on(1)
    
    # Tests avec validation bypassée (API de testing explicite)
    result = await device.testing.led_turn_on_force(-1, bypass_validation=True)
    assert result == False  # ESP32 devrait rejeter
```

## Migration Complète par Méthode

### LED Testing
```python
# AVANT
await device.device.led.turn_on(led_id, _force=True)
await device.device.led.turn_off(led_id, _force=True)
await device.device.led.blink(led_id, frequency, _force=True)
await device.device.led.stop_blink(led_id, _force=True)
await device.device.led.get_state(led_id, _force=True)

# APRÈS
await device.testing.led_turn_on_force(led_id, bypass_validation=True)
await device.testing.led_turn_off_force(led_id, bypass_validation=True)
await device.testing.led_blink_force(led_id, frequency, bypass_validation=True)
await device.testing.led_stop_blink_force(led_id, bypass_validation=True)
await device.testing.led_get_state_force(led_id, bypass_validation=True)
```

### Buzzer Testing
```python
# AVANT
await device.device.buzzer.beep(duration, volume, _force=True)
await device.device.buzzer.set_volume(volume, enabled, _force=True)

# APRÈS
await device.testing.buzzer_beep_force(duration, volume, bypass_validation=True)
await device.testing.buzzer_set_volume_force(volume, enabled, bypass_validation=True)
```

### Language Testing
```python
# AVANT
await device.device.set_language(layout_id, _force=True)

# APRÈS
await device.testing.set_language_force(layout_id, bypass_validation=True)
```

### Key Configuration Testing
```python
# AVANT
await device.keys.set_key_config(key_id, actions, _force=True)

# APRÈS
await device.testing.set_key_config_force(key_id, actions, bypass_validation=True)
```

## Script de Migration Automatique

```python
#!/usr/bin/env python3
"""
Script pour migrer automatiquement les test-scripts
"""
import os
import re

def migrate_test_file(filepath):
    """Migre un fichier de test vers la nouvelle API"""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # 1. Changer l'import
    content = re.sub(
        r'from ardent_scanpad import ScanPad',
        'from ardent_scanpad.testing import ScanPadTesting as ScanPad',
        content
    )
    
    # 2. Migrer les appels LED
    led_methods = ['turn_on', 'turn_off', 'blink', 'stop_blink', 'get_state']
    for method in led_methods:
        pattern = rf'device\.device\.led\.{method}\(([^,]+),\s*_force=True\)'
        replacement = rf'device.testing.led_{method}_force(\1, bypass_validation=True)'
        content = re.sub(pattern, replacement, content)
    
    # 3. Migrer les appels Buzzer
    buzzer_methods = ['beep', 'set_volume']
    for method in buzzer_methods:
        pattern = rf'device\.device\.buzzer\.{method}\(([^,]+),\s*([^,]+),\s*_force=True\)'
        replacement = rf'device.testing.buzzer_{method}_force(\1, \2, bypass_validation=True)'
        content = re.sub(pattern, replacement, content)
    
    # 4. Migrer set_language
    content = re.sub(
        r'device\.device\.set_language\(([^,]+),\s*_force=True\)',
        r'device.testing.set_language_force(\1, bypass_validation=True)',
        content
    )
    
    # 5. Migrer set_key_config
    content = re.sub(
        r'device\.keys\.set_key_config\(([^,]+),\s*([^,]+),\s*_force=True\)',
        r'device.testing.set_key_config_force(\1, \2, bypass_validation=True)',
        content
    )
    
    # Sauvegarder
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Migré: {filepath}")

def migrate_all_tests():
    """Migre tous les fichiers de test dans tools/test-scripts/"""
    test_dir = "../test-scripts"
    
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                migrate_test_file(filepath)
    
    print("🎉 Migration terminée!")

if __name__ == '__main__':
    migrate_all_tests()
```

## Avantages de la Nouvelle API

### ✅ Pour l'API Publique
- **Propre et stable** : Aucun paramètre interne exposé
- **Documentation claire** : Pas de confusion sur les paramètres "internes"
- **Backward compatibility** : L'API normale fonctionne toujours

### ✅ Pour les Tests
- **API explicite** : `ScanPadTesting` indique clairement l'usage test
- **Bypass contrôlé** : `bypass_validation=True` est explicite
- **Méthodes dédiées** : `led_turn_on_force()` au lieu de paramètre caché
- **Documentation séparée** : Tests documentés séparément

### ✅ Pour la Maintenance
- **Séparation claire** : Code de production vs code de test
- **Évolution indépendante** : L'API de test peut évoluer sans affecter l'API publique
- **Tests intensifs** : Toutes tes fonctionnalités de test preserved

## Migration Recommandée

### Phase 1 : Mise à jour immédiate
```bash
# Dans tools/test-scripts/
find . -name "*.py" -exec sed -i '' 's/from ardent_scanpad import ScanPad/from ardent_scanpad.testing import ScanPadTesting as ScanPad/g' {} \;
```

### Phase 2 : Migration progressive des méthodes
Migrer fichier par fichier en utilisant le script ci-dessus ou manuellement.

### Phase 3 : Validation
Tester que tous les test-scripts fonctionnent avec la nouvelle API.

---

**Questions ?** La nouvelle API est 100% compatible fonctionnellement. Seule la façon d'accéder aux méthodes de test a changé pour protéger l'API publique.