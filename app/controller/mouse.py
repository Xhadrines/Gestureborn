"""Controller pentru dispozitiv virtual de mouse.

Implementeaza emitere de evenimente de mouse (miscari, click-uri)
catre sistemul de operare prin intermediul uinput. Suporta:
- Miscari relative pe axele X/Y cu viteza configurable
- Click-uri scurte si lungi (left/right)
- Hold/release pentru apasari prelungite (drag operations)
"""

import time

import uinput


class MouseController:
    """Controleaza un dispozitiv virtual de mouse.

    Emite evenimente mouse la nivel sistem:
    - Miscari: up, down, left, right cu viteza relativa
    - Click-uri: left_click, right_click
    - Hold/release: pentru drag si drop
    """

    def __init__(self):
        """Initializeaza dispozitivul virtual de mouse.

        Configureaza butoane si axele relative pentru mouse virtual.
        """

        # Dispozitiv virtual mouse cu butoane si axe relative
        self.device = uinput.Device(
            [
                uinput.BTN_LEFT,  # Buton stang
                uinput.BTN_RIGHT,  # Buton dreapt
                uinput.REL_X,  # Deplasare relativa pe axa X
                uinput.REL_Y,  # Deplasare relativa pe axa Y
            ],
            name="Gestureborn Virtual Mouse",
        )

    def _emit(self, event, value):
        """Emit eveniment mouse catre dispozitivul virtual.

        Args:
            event: cod eveniment uinput (BTN_* sau REL_*)
            value: valoare eveniment (1/-1 pentru butoane, pixeli pentru miscare)
        """

        self.device.emit(event, value, syn=False)
        self.device.syn()  # Sincronizeaza evenimentul

    # =======================
    # MISCARI MOUSE
    # =======================

    def move_right(self, speed=1):
        """Misca mouse-ul catre dreapta.

        Args:
            speed: viteza miscare in pixeli (implicit 1)
        """

        self._emit(uinput.REL_X, speed)

    def move_left(self, speed=1):
        """Misca mouse-ul catre stanga.

        Args:
            speed: viteza miscare in pixeli (implicit 1)
        """

        self._emit(uinput.REL_X, -speed)

    def move_up(self, speed=1):
        """Misca mouse-ul in sus.

        Args:
            speed: viteza miscare in pixeli (implicit 1)
        """

        self._emit(uinput.REL_Y, -speed)

    def move_down(self, speed=1):
        """Misca mouse-ul in jos.

        Args:
            speed: viteza miscare in pixeli (implicit 1)
        """

        self._emit(uinput.REL_Y, speed)

    # =======================
    # CLICK-URI SCURTE
    # =======================

    def left_click_short(self, duration=0.25):
        """Click scurt buton stang (left click).

        Args:
            duration: timp mentinere in secunde (implicit 0.25s)
        """

        self._emit(uinput.BTN_LEFT, 1)
        time.sleep(duration)
        self._emit(uinput.BTN_LEFT, 0)

    def right_click_short(self, duration=0.25):
        """Click scurt buton dreapt (right click).

        Args:
            duration: timp mentinere in secunde (implicit 0.25s)
        """

        self._emit(uinput.BTN_RIGHT, 1)
        time.sleep(duration)
        self._emit(uinput.BTN_RIGHT, 0)

    # =======================
    # CLICK-URI LUNGI
    # =======================

    def left_click_long(self, duration=0.5):
        """Click lung buton stang (left click cu durata mai mare).

        Args:
            duration: timp mentinere in secunde (implicit 0.5s)
        """

        self._emit(uinput.BTN_LEFT, 1)
        time.sleep(duration)
        self._emit(uinput.BTN_LEFT, 0)

    def right_click_long(self, duration=0.5):
        """Click lung buton dreapt (right click cu durata mai mare).

        Args:
            duration: timp mentinere in secunde (implicit 0.5s)
        """

        self._emit(uinput.BTN_RIGHT, 1)
        time.sleep(duration)
        self._emit(uinput.BTN_RIGHT, 0)

    # =======================
    # HOLD / RELEASE
    # =======================

    def left_click_hold(self):
        """Mentine apasata butonul stang (fara release automat).

        Util pentru drag and drop sau actiuni care necesita apasare continua.
        """

        self._emit(uinput.BTN_LEFT, 1)

    def left_click_release(self):
        """Elibereaza butonul stang anterior mentionut."""

        self._emit(uinput.BTN_LEFT, 0)

    def right_click_hold(self):
        """Mentine apasata butonul dreapt (fara release automat).

        Util pentru drag and drop sau actiuni care necesita apasare continua.
        """

        self._emit(uinput.BTN_RIGHT, 1)

    def right_click_release(self):
        """Elibereaza butonul dreapt anterior mentionut."""

        self._emit(uinput.BTN_RIGHT, 0)
