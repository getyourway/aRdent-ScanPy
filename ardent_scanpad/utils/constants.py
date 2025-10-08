"""
Constants and enumerations for aRdent ScanPad library

Contains all key IDs, action types, HID key codes, and other constants
used throughout the library.
"""

class KeyTypes:
    """Action types for key configuration"""
    UTF8 = 0              # UTF-8 character (language-aware conversion)
    HID = 1               # Direct HID keycode
    CONSUMER = 2          # Consumer control (media keys)
    HARDWARE = 3          # Hardware actions (LED, BUZZER, SCAN_TRIGGER) - processed locally
    MODIFIER_TOGGLE = 4   # ⭐ NEW - Sticky modifier toggle (Shift, Ctrl, Alt, GUI) - Mecalux feature
    API = 5               # ⚠️ SHIFTED from 4 to 5 - API call (reserved for future use)


class HardwareActions:
    """Hardware action IDs for KeyTypes.HARDWARE actions"""
    # Scanner actions
    SCAN_TRIGGER = 20       # Send scan trigger pulse [duration_ms]

    # Future expansion
    # NFC_TRIGGER = 30      # Future: NFC trigger


class KeyIDs:
    """Unified key identifiers (0-19, 100-115) with long press support"""

    # Matrix keys SHORT PRESS (0-15) - 4×4 grid in row-major order
    MATRIX_0_0 = 0   # Row 0, Col 0 (typically '1')
    MATRIX_0_1 = 1   # Row 0, Col 1 (typically '2')
    MATRIX_0_2 = 2   # Row 0, Col 2 (typically '3')
    MATRIX_0_3 = 3   # Row 0, Col 3 (typically 'A')
    MATRIX_1_0 = 4   # Row 1, Col 0 (typically '4')
    MATRIX_1_1 = 5   # Row 1, Col 1 (typically '5')
    MATRIX_1_2 = 6   # Row 1, Col 2 (typically '6')
    MATRIX_1_3 = 7   # Row 1, Col 3 (typically 'B')
    MATRIX_2_0 = 8   # Row 2, Col 0 (typically '7')
    MATRIX_2_1 = 9   # Row 2, Col 1 (typically '8')
    MATRIX_2_2 = 10  # Row 2, Col 2 (typically '9')
    MATRIX_2_3 = 11  # Row 2, Col 3 (typically 'C')
    MATRIX_3_0 = 12  # Row 3, Col 0 (typically '←')
    MATRIX_3_1 = 13  # Row 3, Col 1 (typically '0')
    MATRIX_3_2 = 14  # Row 3, Col 2 (typically '→')
    MATRIX_3_3 = 15  # Row 3, Col 3 (typically 'D')

    # Button actions (16-19) - external buttons
    SCAN_TRIGGER_DOUBLE = 16  # Scan trigger double-press
    SCAN_TRIGGER_LONG = 17    # Scan trigger long-press
    POWER_SINGLE = 18         # Power button single-press
    POWER_DOUBLE = 19         # Power button double-press

    # Matrix keys LONG PRESS (100-115) - same 4×4 layout, offset +100
    MATRIX_0_0_LONG = 100  # Row 0, Col 0 long press
    MATRIX_0_1_LONG = 101  # Row 0, Col 1 long press
    MATRIX_0_2_LONG = 102  # Row 0, Col 2 long press
    MATRIX_0_3_LONG = 103  # Row 0, Col 3 long press
    MATRIX_1_0_LONG = 104  # Row 1, Col 0 long press
    MATRIX_1_1_LONG = 105  # Row 1, Col 1 long press
    MATRIX_1_2_LONG = 106  # Row 1, Col 2 long press
    MATRIX_1_3_LONG = 107  # Row 1, Col 3 long press
    MATRIX_2_0_LONG = 108  # Row 2, Col 0 long press
    MATRIX_2_1_LONG = 109  # Row 2, Col 1 long press
    MATRIX_2_2_LONG = 110  # Row 2, Col 2 long press
    MATRIX_2_3_LONG = 111  # Row 2, Col 3 long press
    MATRIX_3_0_LONG = 112  # Row 3, Col 0 long press
    MATRIX_3_1_LONG = 113  # Row 3, Col 1 long press
    MATRIX_3_2_LONG = 114  # Row 3, Col 2 long press
    MATRIX_3_3_LONG = 115  # Row 3, Col 3 long press

    # Long press offset constant (KISS - simple addition/subtraction)
    LONG_PRESS_OFFSET = 100

    # Collections
    ALL_MATRIX_SHORT = list(range(0, 16))
    ALL_MATRIX_LONG = list(range(100, 116))
    ALL_MATRIX = ALL_MATRIX_SHORT + ALL_MATRIX_LONG
    ALL_BUTTONS = list(range(16, 20))
    ALL_KEYS = ALL_MATRIX_SHORT + ALL_BUTTONS + ALL_MATRIX_LONG

    # Helper methods (matching firmware macros)
    @staticmethod
    def is_long_press(key_id):
        """Check if key_id is a long press (100-115)"""
        return 100 <= key_id <= 115

    @staticmethod
    def is_short_press(key_id):
        """Check if key_id is a matrix short press (0-15)"""
        return 0 <= key_id <= 15

    @staticmethod
    def is_button(key_id):
        """Check if key_id is a button action (16-19)"""
        return 16 <= key_id <= 19

    @staticmethod
    def get_base_key(long_press_id):
        """Convert long press ID to base key ID (100-115 → 0-15)"""
        if KeyIDs.is_long_press(long_press_id):
            return long_press_id - KeyIDs.LONG_PRESS_OFFSET
        return long_press_id

    @staticmethod
    def get_long_press(base_key_id):
        """Convert base key ID to long press ID (0-15 → 100-115)"""
        if 0 <= base_key_id <= 15:
            return base_key_id + KeyIDs.LONG_PRESS_OFFSET
        return None

    @staticmethod
    def is_valid(key_id):
        """Validate key ID (0-19, 100-115)"""
        return KeyIDs.is_short_press(key_id) or KeyIDs.is_button(key_id) or KeyIDs.is_long_press(key_id)

    # Names for display
    NAMES = {
        # Matrix keys SHORT PRESS (4×4 layout)
        0: "Key [0,0] (1)", 1: "Key [0,1] (2)", 2: "Key [0,2] (3)", 3: "Key [0,3] (A)",
        4: "Key [1,0] (4)", 5: "Key [1,1] (5)", 6: "Key [1,2] (6)", 7: "Key [1,3] (B)",
        8: "Key [2,0] (7)", 9: "Key [2,1] (8)", 10: "Key [2,2] (9)", 11: "Key [2,3] (C)",
        12: "Key [3,0] (←)", 13: "Key [3,1] (0)", 14: "Key [3,2] (→)", 15: "Key [3,3] (D)",

        # Button actions
        16: "Scan Trigger Double-Press",
        17: "Scan Trigger Long-Press",
        18: "Power Button Single-Press",
        19: "Power Button Double-Press",

        # Matrix keys LONG PRESS (same 4×4 layout, offset +100)
        100: "Key [0,0] Long Press", 101: "Key [0,1] Long Press", 102: "Key [0,2] Long Press", 103: "Key [0,3] Long Press",
        104: "Key [1,0] Long Press", 105: "Key [1,1] Long Press", 106: "Key [1,2] Long Press", 107: "Key [1,3] Long Press",
        108: "Key [2,0] Long Press", 109: "Key [2,1] Long Press", 110: "Key [2,2] Long Press", 111: "Key [2,3] Long Press",
        112: "Key [3,0] Long Press", 113: "Key [3,1] Long Press", 114: "Key [3,2] Long Press", 115: "Key [3,3] Long Press"
    }


class HIDKeyCodes:
    """Common HID key codes"""
    # Letters
    A = 0x04; B = 0x05; C = 0x06; D = 0x07; E = 0x08; F = 0x09
    G = 0x0A; H = 0x0B; I = 0x0C; J = 0x0D; K = 0x0E; L = 0x0F
    M = 0x10; N = 0x11; O = 0x12; P = 0x13; Q = 0x14; R = 0x15
    S = 0x16; T = 0x17; U = 0x18; V = 0x19; W = 0x1A; X = 0x1B
    Y = 0x1C; Z = 0x1D
    
    # Numbers  
    NUM_1 = 0x1E; NUM_2 = 0x1F; NUM_3 = 0x20; NUM_4 = 0x21; NUM_5 = 0x22
    NUM_6 = 0x23; NUM_7 = 0x24; NUM_8 = 0x25; NUM_9 = 0x26; NUM_0 = 0x27
    
    # Special keys
    ENTER = 0x28; ESCAPE = 0x29; BACKSPACE = 0x2A; TAB = 0x2B
    SPACE = 0x2C; DELETE = 0x4C
    
    # Arrow keys
    RIGHT_ARROW = 0x4F; LEFT_ARROW = 0x50; DOWN_ARROW = 0x51; UP_ARROW = 0x52
    
    # Function keys
    F1 = 0x3A; F2 = 0x3B; F3 = 0x3C; F4 = 0x3D; F5 = 0x3E; F6 = 0x3F
    F7 = 0x40; F8 = 0x41; F9 = 0x42; F10 = 0x43; F11 = 0x44; F12 = 0x45
    
    # Modifiers (for mask parameter)
    CTRL = 0x01; SHIFT = 0x02; ALT = 0x04; GUI = 0x08


class HIDModifiers:
    """HID modifier keys"""
    LEFT_CTRL = 0x01; LEFT_SHIFT = 0x02; LEFT_ALT = 0x04; LEFT_GUI = 0x08
    RIGHT_CTRL = 0x10; RIGHT_SHIFT = 0x20; RIGHT_ALT = 0x40; RIGHT_GUI = 0x80


class ConsumerCodes:
    """Consumer control codes for media keys"""
    VOLUME_UP = 0x00E9; VOLUME_DOWN = 0x00EA; MUTE = 0x00E2
    PLAY_PAUSE = 0x00CD; NEXT_TRACK = 0x00B5; PREV_TRACK = 0x00B6; STOP = 0x00B7
    HOME = 0x0223; BACK = 0x0224


class BLECharacteristics:
    """BLE service and characteristic UUIDs"""
    # Device command service (for LED, buzzer, settings, OTA)
    DEVICE_COMMAND_SERVICE = "12345678-1234-1234-1234-123456789abc"
    DEVICE_COMMAND_CHAR = "87654321-4321-4321-4321-cba987654321"
    DEVICE_RESPONSE_CHAR = "11111111-2222-3333-4444-555555555555"
    
    # Config command service (for key configuration)
    CONFIG_COMMAND_SERVICE = "a0b1c2d3-e4f5-6789-abcd-ef0123456789"
    CONFIG_COMMAND_CHAR = "fedcba98-7654-3210-fedc-ba9876543210"
    CONFIG_RESPONSE_CHAR = "aaaabbbb-cccc-dddd-eeee-ffff00001111"


# Removed Languages class - replaced by KeyboardLayouts with OS-specific codes


class DeviceOrientations:
    """Device orientation constants matching ESP32 firmware"""
    NORMAL = 0    # Normal orientation (0°)
    RIGHT = 1     # Rotated 90° right
    INVERTED = 2  # Rotated 180°
    LEFT = 3      # Rotated 90° left (270°)
    
    # Legacy aliases for backward compatibility
    PORTRAIT = NORMAL
    LANDSCAPE = RIGHT
    REVERSE_PORTRAIT = INVERTED
    REVERSE_LANDSCAPE = LEFT


class LEDs:
    """LED identifiers and configurations - EXACT match with ESP32 hardware cases 1-9"""
    # Individual LEDs - exact ESP32 case mapping
    GREEN_1 = 1    # case 1: LED1 Green (GPIO 7)
    RED = 2        # case 2: LED2 RED (GPIO 17)
    GREEN_2 = 3    # case 3: LED2 GREEN (GPIO 15)  
    BLUE = 4       # case 4: LED2 BLUE (GPIO 16)
    YELLOW = 5     # case 5: LED2 YELLOW (R+G)
    CYAN = 6       # case 6: LED2 CYAN (G+B)
    MAGENTA = 7    # case 7: LED2 MAGENTA (R+B)
    WHITE = 8      # case 8: LED2 WHITE (R+G+B)
    GREEN_3 = 9    # case 9: LED3 Green (GPIO 18)
    
    # Collections
    INDIVIDUAL_LEDS = [GREEN_1, GREEN_3]  # Physical individual LEDs (1, 9)
    RGB_COLORS = [RED, GREEN_2, BLUE, YELLOW, CYAN, MAGENTA, WHITE]  # RGB LED2 colors (2-8)  
    ALL = [GREEN_1, RED, GREEN_2, BLUE, YELLOW, CYAN, MAGENTA, WHITE, GREEN_3]  # All valid IDs 1-9
    
    # Names for display - EXACT ESP32 case mapping
    NAMES = {
        1: "Green LED 1 (GPIO7)",         # case 1: LED1 Green
        2: "Red LED2 (GPIO17)",           # case 2: LED2 RED
        3: "Green LED2 (GPIO15)",         # case 3: LED2 GREEN  
        4: "Blue LED2 (GPIO16)",          # case 4: LED2 BLUE
        5: "Yellow LED2 (R+G)",           # case 5: LED2 YELLOW
        6: "Cyan LED2 (G+B)",             # case 6: LED2 CYAN
        7: "Magenta LED2 (R+B)",          # case 7: LED2 MAGENTA
        8: "White LED2 (R+G+B)",          # case 8: LED2 WHITE
        9: "Green LED 3 (GPIO18)"         # case 9: LED3 Green
    }


# LED Colors work with LED IDs only, not RGB tuples


# Configuration limits
MAX_ACTIONS_PER_KEY = 10
MAX_BATCH_KEYS = 16
BLE_TIMEOUT_DEFAULT = 30.0
RECONNECT_ATTEMPTS = 3


class BuzzerMelodies:
    """Buzzer melody identifiers - Simple command IDs"""
    KEY = 1
    START = 2
    STOP = 3
    NOTIF_UP = 4
    NOTIF_DOWN = 5
    CONFIRM = 6
    WARNING = 7
    ERROR = 8
    SUCCESS = 9
    
    NAMES = {
        KEY: "Key Press",
        START: "Start Up",
        STOP: "Shut Down",
        NOTIF_UP: "Notification Up",
        NOTIF_DOWN: "Notification Down", 
        CONFIRM: "Confirm",
        WARNING: "Warning",
        ERROR: "Error",
        SUCCESS: "Success"
    }


class KeyboardLayouts:
    """
    Compositional Keyboard Layout System for aRdent ScanPad
    
    Format: 0x[OS][PHYSICAL][LANGUAGE][RESERVED]
    - OS: Windows(0x1), macOS(0x2), Android(0x3), iOS(0x4), Linux(0x5)
    - Physical: QWERTY(0x1), AZERTY(0x2), QWERTZ(0x3), Dvorak(0x4), Colemak(0x5)  
    - Language: US(0x1), French(0x2), Belgian(0x3), German(0x4), Spanish(0x5), etc.
    - Reserved: Always 0x0
    
    Keyboard layout identifiers for different language configurations
    """
    
    # === Windows/Linux Layouts (Implemented) ===
    WIN_US_QWERTY = 0x1110      # Windows + QWERTY + US English
    WIN_FR_AZERTY = 0x1220      # Windows + AZERTY + French
    WIN_BE_AZERTY = 0x1230      # Windows + AZERTY + Belgian French
    WIN_DE_QWERTZ = 0x1340      # Windows + QWERTZ + German
    WIN_ES_QWERTY = 0x1150      # Windows + QWERTY + Spanish
    WIN_IT_QWERTY = 0x1160      # Windows + QWERTY + Italian
    WIN_PT_QWERTY = 0x1170      # Windows + QWERTY + Portuguese
    WIN_NL_QWERTY = 0x1180      # Windows + QWERTY + Dutch
    
    # === macOS Layouts (Implemented) ===
    MAC_US_QWERTY = 0x2110      # macOS + QWERTY + US English
    MAC_FR_AZERTY = 0x2220      # macOS + AZERTY + French
    MAC_BE_AZERTY = 0x2230      # macOS + AZERTY + Belgian French


