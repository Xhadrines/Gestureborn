"""Controller pentru dispozitiv virtual de tastatura.

Implementeaza emitere de evenimente de tastatura catre sistemul de operare
prin intermediul uinput. Suporta atât apasari scurte cat si apasari
prelungite (hold/release) pentru simulare input real.
"""

import time

import uinput


class KeyboardController:
    """Controleaza un dispozitiv virtual de tastatura.

    Mapare taste logice la coduri uinput si emit de evenimente
    pentru simulare input de tastatura la nivel sistem.
    """

    def __init__(self):
        """Initializeaza dispozitivul virtual de tastatura.

        Configureaza toate tastele suportate si construieste mapare
        intre numele taste si coduri uinput.
        """

        # Lista completa de taste suportate de dispozitiv
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
                uinput.KEY_CAPSLOCK,  # nu e folosit
                uinput.KEY_C,  # nu e folosit
                uinput.KEY_Q,
                uinput.KEY_F5,  # nu e folosit
                uinput.KEY_F9,  # nu e folosit
                uinput.KEY_T,
                uinput.KEY_J,  # nu e folosit
                uinput.KEY_ESC,
                uinput.KEY_I,  # nu e folosit
                uinput.KEY_P,  # nu e folosit
                uinput.KEY_SLASH,  # nu e folosit
                uinput.KEY_M,  # nu e folosit
                uinput.KEY_ENTER,
            ],
            name="Gestureborn Virtual Keyboard",
        )

        # Mapare nume taste (stringuri) la coduri uinput
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
            "CAPS": uinput.KEY_CAPSLOCK,  # nu e folosit
            "C": uinput.KEY_C,  # nu e folosit
            "Q": uinput.KEY_Q,
            "F5": uinput.KEY_F5,  # nu e folosit
            "F9": uinput.KEY_F9,  # nu e folosit
            "T": uinput.KEY_T,
            "J": uinput.KEY_J,  # nu e folosit
            "ESC": uinput.KEY_ESC,
            "I": uinput.KEY_I,  # nu e folosit
            "P": uinput.KEY_P,  # nu e folosit
            "/": uinput.KEY_SLASH,  # nu e folosit
            "M": uinput.KEY_M,  # nu e folosit
            "ENTER": uinput.KEY_ENTER,
        }

    def _emit(self, key, value):
        """Emit eveniment tasta catre dispozitivul virtual.

        Args:
            key: cod uinput KEY_*
            value: 1 pentru press, 0 pentru release
        """

        self.device.emit(key, value)
        self.device.syn()  # Sincronizeaza evenimentul

    def press(self, key, duration=0.1):
        """Apasa si elibereaza o tasta (press + release).

        Simuleaza apasarea rapida a unei taste.

        Args:
            key: nume tasta (ex: 'W', 'TAB', 'ESC')
            duration: timp mentinere in secunde (implicit 0.1s)
        """

        real_key = self.map[key.upper()]

        # Press
        self._emit(real_key, 1)
        time.sleep(duration)
        # Release
        self._emit(real_key, 0)

    def hold(self, key):
        """Mentine tasta apasata (fara release automat).

        Args:
            key: nume tasta
        """

        real_key = self.map[key.upper()]
        self._emit(real_key, 1)

    def release(self, key):
        """Elibereaza o tasta anterioe mentinuta.

        Args:
            key: nume tasta
        """

        real_key = self.map[key.upper()]
        self._emit(real_key, 0)
