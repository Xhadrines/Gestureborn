"""Engine pentru control tastatura cu gesturi manuale.

Mapare gesturilor manuale la tastatura pentru comenzi in joc.
"""
import time

from ..vision import HandGestureDetector
from ..mapping import KeyboardMapper


class HandKeyboardEngine:
    """Procesor pentru gesturi manuale mapate la taste tastatura.

    Detecteaza directiile mainilor si combina cu alte geste
    pentru a genera comenzi tastatura.
    """

    def __init__(self, keyboard):
        """Initializeaza engine-ul cu controller tastatura si detector geste.

        Args:
            keyboard: KeyboardController pentru comenzi tastatura
        """
        self.keyboard = keyboard
        self.detector = HandGestureDetector()
        self.left_held = set()
        self.right_held = None
        self.left_open = False
        self.right_open = False
        self.both_open = False
        self.left_pinch = False
        self.right_pinch = False
        self.both_pinch = False

        self.left_pinch_start = None
        self.right_pinch_start = None
        self.both_pinch_start = None
        # Praguri separate pentru actiuni rapide si actiuni combinate
        self.pinch_single_hold_seconds = 2.0
        self.pinch_both_hold_seconds = 1.0

    def _sync_keys(self, current_keys, target_keys):
        """Sincronizeaza tastele: elibereaza cele nefiind necesare.

        Args:
            current_keys: set de taste tinute apasate acum
            target_keys: set de taste care trebuie tinute acum

        Returns:
            Noul set de taste tinute apasate
        """
        for key in current_keys - target_keys:
            self.keyboard.release(key)

        for key in target_keys - current_keys:
            self.keyboard.hold(key)

        return set(target_keys)

    def _get_axis_targets(self, center, circle, deadzone):
        """Determina care taste de miscare trebuie apasate.

        Mapare: dreapta->D, stanga->A, jos->S, sus->W
        """
        direction = self.detector.get_direction(center, circle, deadzone)
        if direction in ("neutral", "outside"):
            return set()

        cx, cy = circle["center"]
        x, y = center
        dx = x - cx
        dy = y - cy
        targets = set()

        if abs(dx) > deadzone["radius"]:
            targets.add("D" if dx > 0 else "A")

        if abs(dy) > deadzone["radius"]:
            targets.add("S" if dy > 0 else "W")

        return targets

    def _get_locked_target(self, current_target, center, circle, deadzone, mapping):
        """Determina tastela bloc (SPACE, CTRL, ALT, SHIFT) cu stabilitate.

        Pastreaza tasta activa pana cand se depaseste prag-ul complet.
        """
        direction = self.detector.get_direction(center, circle, deadzone)
        if direction in ("neutral", "outside"):
            return None

        target = mapping.get(direction)
        if not target:
            return None

        if current_target and current_target == target:
            return current_target

        cx, cy = circle["center"]
        x, y = center
        dx = x - cx
        dy = y - cy
        horizontal_strength = abs(dx)
        vertical_strength = abs(dy)

        if (
            current_target
            and horizontal_strength > deadzone["radius"]
            and vertical_strength > deadzone["radius"]
        ):
            if current_target in ("SPACE", "CTRL", "ALT", "SHIFT"):
                return current_target

        if current_target and current_target != target:
            if (
                horizontal_strength > deadzone["radius"]
                and vertical_strength > deadzone["radius"]
            ):
                return current_target

        return target

    def _sync_hold_key(self, current_state, target_state, key):
        """Mentine sau elibereaza o singura tasta in functie de stare."""
        if target_state and not current_state:
            self.keyboard.hold(key)
        elif not target_state and current_state:
            self.keyboard.release(key)

        return target_state

    def process_open_palms(self, left_landmarks, right_landmarks):
        """Proceseaza palmele deschise pentru actiuni de interactiune.

        Palma stanga declanseaza R o singura data la deschidere.
        Palma dreapta mentine E cat timp ramane deschisa.
        Cand ambele palme sunt deschise simultan, se apasa F o singura data.
        """
        left_open = self.detector.is_open_palm(left_landmarks)
        right_open = self.detector.is_open_palm(right_landmarks)
        both_open = left_open and right_open

        # Cand ambele palme sunt deschise, prioritatea trece pe actiunea comuna
        if both_open:
            if self.right_open:
                self.keyboard.release(KeyboardMapper.RIGHT_OPEN_HOLD)
                self.right_open = False

            if not self.both_open:
                self.keyboard.press(KeyboardMapper.BOTH_OPEN_PRESS)

            self.both_open = True
            self.left_open = False
            return

        if self.both_open:
            self.both_open = False

        if left_open and not self.left_open:
            self.keyboard.press(KeyboardMapper.LEFT_OPEN_PRESS)

        self.left_open = left_open

        self.right_open = self._sync_hold_key(
            self.right_open,
            right_open,
            KeyboardMapper.RIGHT_OPEN_HOLD,
        )

    def process_pinch(self, left_landmarks, right_landmarks):
        """Proceseaza gestul pinch pentru actiuni rapide.

        Mana stanga apasa TAB o singura data la detectie.
        Mana dreapta apasa Q o singura data la detectie.
        Cand ambele maini fac pinch simultan, se apasa ESC o singura data.
        """
        left_pinch = self.detector.is_pinch(left_landmarks, "left")
        right_pinch = self.detector.is_pinch(right_landmarks, "right")
        both_pinch = left_pinch and right_pinch

        now = time.time()

        # Gestul simultan are prioritate fata de gesturile individuale
        if both_pinch:
            self.left_pinch_start = None
            self.right_pinch_start = None

            if self.both_pinch_start is None:
                self.both_pinch_start = now

            if now - self.both_pinch_start >= self.pinch_both_hold_seconds:
                if not self.both_pinch:
                    self.keyboard.press(KeyboardMapper.BOTH_PINCH_PRESS)
                self.both_pinch = True
                self.left_pinch = False
                self.right_pinch = False
            return

        if self.both_pinch:
            self.both_pinch = False
        self.both_pinch_start = None

        if left_pinch and not right_pinch:
            if self.left_pinch_start is None:
                self.left_pinch_start = now
            if now - self.left_pinch_start >= self.pinch_single_hold_seconds:
                if not self.left_pinch:
                    self.keyboard.press(KeyboardMapper.LEFT_PINCH_PRESS)
                self.left_pinch = True
        else:
            self.left_pinch_start = None
            self.left_pinch = False

        if right_pinch and not left_pinch:
            if self.right_pinch_start is None:
                self.right_pinch_start = now
            if now - self.right_pinch_start >= self.pinch_single_hold_seconds:
                if not self.right_pinch:
                    self.keyboard.press(KeyboardMapper.RIGHT_PINCH_PRESS)
                self.right_pinch = True
        else:
            self.right_pinch_start = None
            self.right_pinch = False

        if both_pinch:
            if not self.both_pinch:
                self.keyboard.press(KeyboardMapper.BOTH_PINCH_PRESS)

            self.both_pinch = True
            self.left_pinch = False
            self.right_pinch = False
            return

        if self.both_pinch:
            self.both_pinch = False

        if left_pinch and not self.left_pinch:
            self.keyboard.press(KeyboardMapper.LEFT_PINCH_PRESS)

        if right_pinch and not self.right_pinch:
            self.keyboard.press(KeyboardMapper.RIGHT_PINCH_PRESS)

        self.left_pinch = left_pinch
        self.right_pinch = right_pinch

    def process_left(self, landmarks, center, circle, deadzone):
        """Proceseaza mana stanga: comenzi de miscare (WASD).

        Activeaza taste directionale dupa pozitia mainii in zonele de detectie.
        """
        if not (
            self.detector.is_fist(landmarks)
            or self.detector.is_index_finger_up(landmarks)
        ):
            self.left_held = self._sync_keys(self.left_held, set())
            return

        target_keys = self._get_axis_targets(center, circle, deadzone)
        self.left_held = self._sync_keys(self.left_held, target_keys)

    def process_right(self, landmarks, center, circle, deadzone):
        """Proceseaza mana dreapta: comenzi bloc (SPACE, CTRL, ALT, SHIFT).

        Activeaza o singura tasta bloc la un moment, cu inertie pentru stabilitate.
        """
        if not (
            self.detector.is_fist(landmarks)
            or self.detector.is_index_finger_up(landmarks)
        ):
            if self.right_held:
                self.keyboard.release(self.right_held)
            self.right_held = None
            return

        target = self._get_locked_target(
            self.right_held,
            center,
            circle,
            deadzone,
            KeyboardMapper.RIGHT_MAP,
        )

        if target == self.right_held:
            return

        if self.right_held:
            self.keyboard.release(self.right_held)

        if target:
            self.keyboard.hold(target)

        self.right_held = target
