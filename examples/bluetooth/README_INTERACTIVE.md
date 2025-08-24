# ScanPad Interactive Terminal

Un outil interactif complet pour tester et configurer votre aRdent ScanPad depuis le terminal.

## 🚀 Lancement Rapide

```bash
cd tools/python-library/examples
python3 scanpad_interactive.py
```

## 📊 Fonctionnalités

### 1. **Device Snapshot** (Au démarrage)
Affiche un résumé complet de l'état de votre ScanPad :
- **Device Information Service (DIS)** : Modèle, firmware, numéro de série
- **État de la batterie** : Niveau, voltage, statut de charge
- **Configuration** : Orientation, langue du clavier, auto-shutdown
- **État des LEDs** : Statut ON/OFF de chaque LED
- **Configuration des touches** : Résumé des touches configurées

### 2. **Menu Principal**
```
🎮 MAIN MENU
1. 🔧 Peripheral Control (LEDs, Buzzer, etc.)
2. ⌨️  Key Configuration
3. ⚙️  Device Settings
4. 📊 Refresh Device Snapshot
5. 🔄 Factory Reset
6. 🎯 OTA Update
0. 🚪 Exit
```

### 3. **Contrôle des Périphériques**

#### 💡 **LED Control**
- Allumer/éteindre des LEDs individuelles
- Faire clignoter des LEDs
- Configurer les couleurs RGB (LED 3-5)
- Voir l'état de toutes les LEDs
- Contrôle global (toutes ON/OFF)

#### 🔊 **Buzzer Control**
- Beep simple
- Beeps multiples
- Mélodies prédéfinies (success, error, warning, notification)
- Réglage du volume

#### 🔋 **Battery Info**
- Niveau de batterie
- Voltage, courant, température
- Temps restant / temps de charge

### 4. **Configuration des Touches**

#### 📋 **Visualisation**
Vue matricielle des touches configurées :
```
🔢 Matrix Keys (4x4):
[0,0] ✓ 2 action(s)  [0,1] - Empty      [0,2] ✓ 1 action(s)  [0,3] - Empty
[1,0] ✓ 3 action(s)  [1,1] ✓ 1 action(s)  [1,2] - Empty      [1,3] - Empty
...

🔘 Button Actions:
Scan Trigger Double: ✓ 1 action(s)
Power Single: - Empty
```

#### 🔧 **Configuration Simple**
Configuration interactive d'une touche :
1. Sélection de la touche (notation matricielle ou ID)
2. Ajout d'actions (jusqu'à 10) :
   - **UTF-8 Text** : Texte simple (max 8 bytes)
   - **HID Key** : Touches spéciales avec modificateurs
   - **Consumer Control** : Contrôles média/système
3. Aperçu et confirmation

#### 🎯 **Configuration Batch**
Configurez plusieurs touches puis envoyez tout :
- Mode **Burst** : Envoi rapide de toutes les configurations
- Mode **Séquentiel** : Envoi une par une avec feedback

### 5. **Paramètres de l'Appareil**

- **🔄 Orientation** : 0°, 90°, 180°, 270°
- **🌐 Langue du clavier** : US, FR, ES, IT, DE, UK
- **⏰ Auto-shutdown** : Timeouts BLE et activité
- **📱 Informations** : Détails complets du device

## 💡 Exemples d'Utilisation

### Configuration Rapide d'une Touche
1. Menu principal → `2` (Key Configuration)
2. → `2` (Configure Single Key)
3. Entrer `0,0` pour la première touche
4. → `1` (UTF-8 Text)
5. Taper `Hello` + Enter
6. → `4` (Finish)
7. → `y` pour confirmer

### Test des LEDs avec Couleurs
1. Menu principal → `1` (Peripheral Control)
2. → `1` (LED Control)
3. → `4` (Set RGB Color)
4. → `3` (Blue)

### Configuration Batch de Touches
1. Menu principal → `2` (Key Configuration)
2. → `3` (Configure Multiple Keys)
3. → `1` (Add key)
4. Format rapide : `text:Bonjour`
5. Répéter pour d'autres touches
6. → `3` (Send all burst mode)

## 🎨 Format d'Actions Rapide

Pour la configuration batch, utilisez le format rapide :
- **Texte** : `text:Hello World`
- **HID** : `hid:40` (Enter)
- **Consumer** : `consumer:233` (Volume Up)

## 🔑 Codes Utiles

### HID Key Codes
- Lettres : A=4, B=5, C=6... Z=29
- Chiffres : 1=30, 2=31... 0=39
- Enter=40, Esc=41, Backspace=42, Tab=43, Space=44
- F1=58, F2=59... F12=69
- Flèches : Right=79, Left=80, Down=81, Up=82

### Modificateurs
- 1 = Ctrl
- 2 = Shift
- 4 = Alt
- 8 = Win/Cmd
- Combiner : 3 = Ctrl+Shift

### Consumer Controls
- Volume : Up=233, Down=234, Mute=226
- Media : Play/Pause=205, Stop=183, Next=181, Previous=182

## 🛠️ Développement

Ce script est un excellent exemple d'utilisation complète de la librairie `ardent_scanpad`. Il démontre :
- Connexion et gestion asynchrone
- Utilisation de tous les contrôleurs (keys, leds, buzzer, device, ota)
- Gestion des erreurs et feedback utilisateur
- Interface utilisateur interactive dans le terminal

## 📝 Notes

- Le script se connecte automatiquement au premier ScanPad trouvé
- Toutes les modifications sont appliquées immédiatement
- Utilisez "Save Configuration" pour persister les touches en mémoire
- Le Factory Reset nécessite une confirmation explicite
- L'OTA Update redirige vers les scripts de test dédiés