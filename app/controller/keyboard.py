import uinput
import time


class KeyboardController:
    def __init__(self):
        self.device = uinput.Device(
            [
                uinput.KEY_W,
                uinput.KEY_A,
                uinput.KEY_S,
                uinput.KEY_D,
                uinput.KEY_E,
                uinput.KEY_R,
                uinput.KEY_TAB,
                uinput.KEY_F,
                uinput.KEY_SPACE,
                uinput.KEY_LEFTALT,
                uinput.KEY_Z,
                uinput.KEY_LEFTCTRL,
                uinput.KEY_LEFTSHIFT,
                uinput.KEY_CAPSLOCK,
                uinput.KEY_C,
                uinput.KEY_Q,
                uinput.KEY_F5,
                uinput.KEY_F9,
                uinput.KEY_T,
                uinput.KEY_J,
                uinput.KEY_ESC,
                uinput.KEY_I,
                uinput.KEY_P,
                uinput.KEY_SLASH,
                uinput.KEY_M,
            ],
            name="Gestureborn Virtual Keyboard",
        )

        self.map = {
            "W": uinput.KEY_W,
            "A": uinput.KEY_A,
            "S": uinput.KEY_S,
            "D": uinput.KEY_D,
            "E": uinput.KEY_E,
            "R": uinput.KEY_R,
            "TAB": uinput.KEY_TAB,
            "F": uinput.KEY_F,
            "SPACE": uinput.KEY_SPACE,
            "ALT": uinput.KEY_LEFTALT,
            "Z": uinput.KEY_Z,
            "CTRL": uinput.KEY_LEFTCTRL,
            "SHIFT": uinput.KEY_LEFTSHIFT,
            "CAPS": uinput.KEY_CAPSLOCK,
            "C": uinput.KEY_C,
            "Q": uinput.KEY_Q,
            "F5": uinput.KEY_F5,
            "F9": uinput.KEY_F9,
            "T": uinput.KEY_T,
            "J": uinput.KEY_J,
            "ESC": uinput.KEY_ESC,
            "I": uinput.KEY_I,
            "P": uinput.KEY_P,
            "/": uinput.KEY_SLASH,
            "M": uinput.KEY_M,
        }

    # -------------------------
    # Core emit
    # -------------------------
    def _emit(self, key, value):
        self.device.emit(key, value)
        self.device.syn()

    # -------------------------
    # Generic press
    # -------------------------
    def press(self, key, duration=0.1):
        real_key = self.map[key.upper()]

        self._emit(real_key, 1)
        time.sleep(duration)
        self._emit(real_key, 0)

    # -------------------------
    # Hold si release presses
    # -------------------------
    def hold(self, key):
        real_key = self.map[key.upper()]
        self._emit(real_key, 1)

    def release(self, key):
        real_key = self.map[key.upper()]
        self._emit(real_key, 0)
