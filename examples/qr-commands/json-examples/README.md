# JSON Examples for aRdent ScanPad QR Generation

Ce dossier contient des exemples JSON prêts à utiliser pour générer des QR codes avec la nouvelle API hybride d'aRdent ScanPad.

## Structure

```
json-examples/
├── keyboard-configs/     # Configurations clavier complètes
│   ├── warehouse_keypad.json
│   ├── pos_terminal.json
│   ├── function_keys.json
│   ├── multilingual_text.json
│   └── gaming_controller.json
├── device-commands/      # Commandes device (multi-commandes = 1 QR)
│   ├── initial_setup.json
│   ├── warehouse_lighting.json
│   ├── demo_sequence.json
│   ├── emergency_reset.json
│   ├── single_led_on.json
│   └── individual_commands.json
└── README.md            # Cette documentation
```

## Usage

### Configuration Clavier (Keyboard Configs)

**1 JSON = 1 QR Code** avec configuration complète des 16 touches + boutons externes

```python
from ardent_scanpad.qr_generators import KeyboardConfigGenerator

gen = KeyboardConfigGenerator()

# Charger une configuration depuis JSON
qr_codes = gen.from_json_file("json-examples/keyboard-configs/warehouse_keypad.json")
print(f"Generated {len(qr_codes)} QR code(s)")

# Sauvegarder les QR codes
gen.save_qr_codes(qr_codes, "output/", filename_prefix="warehouse_")
```

### Commandes Device

**Multi-commandes = 1 QR Code** par défaut (format batch)

```python
from ardent_scanpad.qr_generators import DeviceCommandGenerator

dev_gen = DeviceCommandGenerator()

# Charger plusieurs commandes qui seront encodées dans UN SEUL QR
qr_codes = dev_gen.from_json_file("json-examples/device-commands/initial_setup.json")
print(f"Generated {len(qr_codes)} QR code(s)")  # = 1 QR avec toutes les commandes

# Sauvegarder
dev_gen.save_qr_codes(qr_codes, "output/", filename_prefix="setup_")
```

## Exemples de Configurations Clavier

### 🏭 warehouse_keypad.json
- **Usage** : Entrepôt et logistique
- **Touches** : Chiffres 0-9 + préfixes "QTY:", "LOC:", "SKU:" 
- **Spécialités** : Tab, Entrée, saut de ligne
- **Format** : Configuration complète 16 touches

### 🛒 pos_terminal.json  
- **Usage** : Terminal point de vente
- **Touches** : Chiffres + ".", "€", " x", "+"
- **Spécialités** : Symboles monétaires et opérations
- **Boutons** : TOTAL (power), SCAN: (trigger)

### ⚙️ function_keys.json
- **Usage** : Développement et contrôle système
- **Touches** : F1-F12 + Entrée/Échap/Tab/Backspace
- **Format** : Codes HID pour touches de fonction

### 🌍 multilingual_text.json
- **Usage** : Support international
- **Touches** : Texte UTF-8 (café, naïve, résumé, müde, niño)
- **Spécialités** : Caractères accentués, symboles €£
- **Encodage** : UTF-8 jusqu'à 8 bytes par action

### 🎮 gaming_controller.json
- **Usage** : Gaming et raccourcis
- **Touches** : 1-4, WASD, flèches, "gg wp" + Entrée
- **Spécialités** : Macros texte + actions HID combinées

## Exemples de Commandes Device

### 🔧 initial_setup.json
- **Multi-commandes** : Orientation + LED + Buzzer + Clear Lua
- **Usage** : Configuration initiale complète
- **Format** : 1 QR = 5 commandes séquentielles

### 💡 warehouse_lighting.json
- **Multi-commandes** : All LEDs OFF + 3 LEDs ON + Buzzer
- **Usage** : Éclairage d'entrepôt
- **Format** : 1 QR = 5 commandes

### 🎭 demo_sequence.json
- **Multi-commandes** : Séquence complète de démonstration
- **Usage** : Présentation des capacités
- **Format** : 1 QR = 7 commandes (START → LEDs → Orientation → SUCCESS)

### 🚨 emergency_reset.json
- **Multi-commandes** : Reset complet du device
- **Usage** : Remise à zéro d'urgence
- **Format** : 1 QR = 5 commandes (Clear → OFF → Orientation → WARNING → LED rouge)

### 💡 single_led_on.json
- **Commande unique** : Une seule LED
- **Usage** : Test de commande individuelle
- **Format** : 1 QR = 1 commande

### 🔀 individual_commands.json
- **Mode individuel** : `"batch_format": "individual"`
- **Usage** : Génère plusieurs QR (1 par commande)
- **Format** : 3 commandes = 3 QR codes séparés

## Options de Configuration

### Keyboard Configs
```json
{
  "options": {
    "qr_format": "full",           // "full" ou "individual" 
    "compression_level": 6         // 1-9 (compression zlib)
  }
}
```

### Device Commands  
```json
{
  "options": {
    "batch_format": "sequential"   // "sequential" (défaut) ou "individual"
  }
}
```

## Formats QR Générés

| Type | Format | Exemple |
|------|--------|---------|
| Keyboard Full | `$FULL:base64_data$` | Configuration complète compressée |
| Keyboard Individual | `$CMD:KEY:xxxx$` | Une commande par QR |
| Device Batch | `$BATCH:base64_data$` | Plusieurs commandes dans 1 QR |
| Device Individual | `$CMD:DEV:xxxx$` | Une commande par QR |

## Validation JSON

Tous les JSON sont automatiquement validés :
- **Structure** : Champs requis, types corrects
- **Limites** : UTF-8 ≤ 8 bytes, HID codes 0-255, etc.
- **Actions** : Types valides (text, hid, consumer)
- **Domaines** : led_control, buzzer_control, device_settings, etc.

## Cas d'Erreur

```python
try:
    qr_codes = gen.from_json_file("invalid.json")
except ValueError as e:
    print(f"Erreur JSON: {e}")
```

Messages d'erreur détaillés pour :
- JSON malformé
- Champs manquants
- Valeurs hors limites
- Types d'actions non supportés

## Extension

Pour créer vos propres JSON :

1. **Copiez** un exemple similaire
2. **Modifiez** les métadonnées et commandes
3. **Testez** avec les générateurs
4. **Validez** les QR codes générés

Les JSON sont **auto-documentés** avec métadonnées complètes pour faciliter la maintenance et le partage.