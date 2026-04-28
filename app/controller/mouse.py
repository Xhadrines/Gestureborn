import uinput
import time


class MouseController:
    def __init__(self):
        self.device = uinput.Device(
            [
                uinput.BTN_LEFT,
                uinput.BTN_RIGHT,
                uinput.REL_X,
                uinput.REL_Y,
            ],
            name="Gestureborn Virtual Mouse",
        )

    # -------------------------
    # Core emit
    # -------------------------
    def _emit(self, event, value):
        self.device.emit(event, value, syn=False)
        self.device.syn()

    # -------------------------
    # Miscari mouse
    # -------------------------
    def move_right(self, speed=1):
        self._emit(uinput.REL_X, speed)

    def move_left(self, speed=1):
        self._emit(uinput.REL_X, -speed)

    def move_up(self, speed=1):
        self._emit(uinput.REL_Y, -speed)

    def move_down(self, speed=1):
        self._emit(uinput.REL_Y, speed)

    # -------------------------
    # Click-uri scurte
    # -------------------------
    def left_click_short(self, duration=0.25):
        self._emit(uinput.BTN_LEFT, 1)
        time.sleep(duration)
        self._emit(uinput.BTN_LEFT, 0)

    def right_click_short(self, duration=0.25):
        self._emit(uinput.BTN_RIGHT, 1)
        time.sleep(duration)
        self._emit(uinput.BTN_RIGHT, 0)

    # -------------------------
    # Click-uri lungi
    # -------------------------
    def left_click_long(self, duration=0.5):
        self._emit(uinput.BTN_LEFT, 1)
        time.sleep(duration)
        self._emit(uinput.BTN_LEFT, 0)

    def right_click_long(self, duration=0.5):
        self._emit(uinput.BTN_RIGHT, 1)
        time.sleep(duration)
        self._emit(uinput.BTN_RIGHT, 0)

    # -------------------------
    # Hold si release click-uri
    # -------------------------
    def left_click_hold(self):
        self._emit(uinput.BTN_LEFT, 1)

    def left_click_release(self):
        self._emit(uinput.BTN_LEFT, 0)

    def right_click_hold(self):
        self._emit(uinput.BTN_RIGHT, 1)

    def right_click_release(self):
        self._emit(uinput.BTN_RIGHT, 0)
