"""Engine pentru control tastatura cu gesturi manuale.

Mapare gesturilor manuale la tastatura pentru comenzi in joc.
"""

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
