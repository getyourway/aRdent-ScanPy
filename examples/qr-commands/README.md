# 📱 QR Code Commands Generation

Génération de QR codes pour configurer l'aRdent ScanPad **sans connexion Bluetooth**.

> **Avantage** : Pas de BLE requis ! Parfait pour applications web, documentation, ou déploiement à distance.

## 🚀 Scripts Disponibles

### 🎮 **scanpad_qrcode_interactive.py** - Terminal QR Interactif
**Application complète de génération de QR codes avec menu interactif**

```bash
python scanpad_qrcode_interactive.py
```

**Fonctionnalités complètes** :
- 💡 **LED Control** : QR codes pour contrôle individuel des LEDs (ON/OFF/Blink)
- 🔊 **Buzzer Control** : QR codes pour mélodies et beeps personnalisés
- ⌨️ **Key Configuration** : QR codes pour configuration complète des touches
- 🛠️ **Complete Keyboard Builder** : Configuration complète 4×4 avec multi-actions
- 🔧 **Lua Script Deployment** : QR codes multi-fragments pour scripts Lua
- ⚙️ **Device Settings** : Orientation, langue, paramètres système
- 📦 **Batch Operations** : Génération et sauvegarde en lot

**Nouveau dans cette version** :
- 🛠️ **Deploy Lua script from file** (option 17)
- 📝 **Deploy custom Lua script** (option 18) 
- 🗑️ **Clear Lua script** (option 19)
- ℹ️ **Lua script info** (option 21)

**Idéal pour** : Développement d'interfaces utilisateur, documentation, déploiement

---

### 🔧 **generate_backslash_filter_qr.py** - Filtre Backslash
**QR code pour script Lua de filtrage des backslash**

```bash
python generate_backslash_filter_qr.py
```

**Fonctionnalités** :
- Génère QR code pour script Lua de filtrage `\`
- Gestion automatique des échappements  
- Sauvegarde PNG avec compression optimisée

**Cas d'usage** : Systèmes Windows avec chemins de fichiers

---

### 📊 **generate_barcode_filter_qr.py** - Filtre Barcode
**QR code pour script Lua de filtrage de codes-barres**

```bash
python generate_barcode_filter_qr.py
```

**Fonctionnalités** :
- Script de validation et filtrage de codes-barres
- Patterns de validation configurables
- Feedback LED et audio intégré

**Cas d'usage** : Validation de codes-barres métier, contrôle qualité

---

### 🔄 **generate_duplicate_detector_qr.py** - Détecteur de Doublons
**QR code pour script Lua de détection de doublons**

```bash
python generate_duplicate_detector_qr.py
```

**Fonctionnalités** :
- Détection automatique des scans en double
- Historique configurable des derniers scans
- Alertes visuelles et sonores

**Cas d'usage** : Inventaire, contrôle de stock, prévention erreurs

## 🎯 Formats QR Supportés

### Commandes Device (Format `$CMD:DEV:`)
```
$CMD:DEV:10<hex_data>CMD$    # LED Control
$CMD:DEV:20<hex_data>CMD$    # Buzzer Control  
$CMD:DEV:42<hex_data>CMD$    # Device Settings
```

### Commandes Configuration (Format `$CMD:KEY:`)
```
$CMD:KEY:80<hex_data>CMD$    # Key Configuration
$CMD:KEY:90<hex_data>CMD$    # Save Configuration
```

### Scripts Lua (Format Multi-QR)
```
$LUA1:<base64_data>$         # Fragment 1
$LUA2:<base64_data>$         # Fragment 2
$LUAX:<base64_data>$         # Fragment final (Execute)
```

### Configuration Complète (Format `$FULL:`)
```
$FULL:<compressed_base64>$   # Configuration complète clavier
```

## 🔧 Architecture QR

### QRCommand Class
Chaque QR généré est encapsulé dans un objet `QRCommand` :

```python
from ardent_scanpad.controllers.qr_generator import QRGeneratorController

qr = QRGeneratorController()

# LED Command
led_cmd = qr.create_led_on_command(1)
print(led_cmd.command_data)  # $CMD:DEV:100101CMD$
led_cmd.save("led_on.png")

# Key Configuration  
actions = [qr.create_text_action("Hello")]
key_cmd = qr.create_key_config_command(0, actions)
key_cmd.save("key_config.png")

# Lua Script
lua_cmds = qr.create_lua_script_from_file("script.lua")
for i, cmd in enumerate(lua_cmds):
    cmd.save(f"lua_part_{i+1}.png")
```

### Métadonnées et Compression
Les QR codes incluent des métadonnées complètes :

```python
qr_command = qr.create_lua_script_from_file("script.lua")
metadata = qr_command.metadata

print(f"Original: {metadata['original_size_bytes']} bytes")
print(f"Compressed: {metadata['compressed_size_bytes']} bytes") 
print(f"Compression: {metadata['compression_ratio_percent']}%")
print(f"Fragments: {metadata['total_fragments']}")
```

## 📋 Guide d'Utilisation

### 1. Génération Simple
```python
from ardent_scanpad.controllers.qr_generator import QRGeneratorController

qr = QRGeneratorController()

# LED Control
cmd = qr.create_led_on_command(1)
cmd.save("output/led1_on.png")
```

### 2. Configuration Clavier Complète
```python
# Configuration complète 4x4
config = {
    0: [qr.create_text_action("1")],
    1: [qr.create_text_action("2")], 
    15: [qr.create_hid_action(HIDKeyCodes.ENTER)]
}

full_cmd = qr.create_full_keyboard_config(config)
full_cmd.save("full_keyboard.png")
```

### 3. Scripts Lua Multi-QR
```python
# Script volumineux avec fragmentation automatique
lua_cmds = qr.create_lua_script_from_file("large_script.lua", max_qr_size=1000)

print(f"Generated {len(lua_cmds)} QR codes")
for i, cmd in enumerate(lua_cmds):
    filename = f"lua_part_{i+1:02d}.png"
    cmd.save(f"output/{filename}")
```

## 🔨 Développement d'Applications

### Applications Web
```javascript
// Génération côté serveur Python + affichage web
fetch('/generate_qr', {
    method: 'POST',
    body: JSON.stringify({type: 'led_on', led_id: 1})
})
.then(response => response.blob())
.then(blob => {
    const img = document.createElement('img');
    img.src = URL.createObjectURL(blob);
    document.body.appendChild(img);
});
```

### Applications Desktop
```python
# Interface graphique avec QR codes
import tkinter as tk
from PIL import Image, ImageTk

qr_cmd = qr.create_led_on_command(1)
qr_image = qr_cmd.generate_qr_image(size=300)

# Affichage dans interface
photo = ImageTk.PhotoImage(qr_image)
label = tk.Label(root, image=photo)
label.pack()
```

### Documentation Technique
```markdown
# Configuration LED 1 ON
Scannez ce QR code pour allumer la LED 1 :

![LED 1 ON](qr_led1_on.png)

Commande générée : `$CMD:DEV:100101CMD$`
```

## 💡 Conseils d'Utilisation

- **Organisez vos QR codes** : Utilisez des noms de fichiers descriptifs
- **Testez sur device réel** : Vérifiez la lisibilité des QR codes générés
- **Utilisez la compression** : Pour les scripts Lua volumineux
- **Fragmentez intelligemment** : max_qr_size=1000 pour bonne lisibilité
- **Gardez les métadonnées** : Utiles pour debugging et documentation

## 🔗 Liens Utiles

- [Documentation QRGeneratorController](../../ardent_scanpad/controllers/qr_generator.py)
- [Constantes et codes](../../ardent_scanpad/utils/constants.py)
- [Exemples Bluetooth](../bluetooth/)  
- [Scripts Lua](../lua-scripting/)