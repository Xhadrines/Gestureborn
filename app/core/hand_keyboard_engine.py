"""Engine pentru control tastatura cu gesturi manuale.

Mapare gesturilor manuale la tastatura pentru comenzi in joc.
"""

import time

from ..vision import HandGestureDetector
from ..mapping import KeyboardMapper


class HandKeyboardEngine:
    """Procesor pentru gesturi manuale mapate la taste de tastatura.

    Coordoneaza detectie geste pe ambele maini si mapare la comenzi
    tastatura cu mecanisme de delay si inertie pentru stabilitate.
    """

    def __init__(self, keyboard):
        """Initializeaza engine-ul cu controller tastatura si detectorul de geste.

        Args:
            keyboard: KeyboardController pentru comenzi tastatura
        """

        self.keyboard = keyboard
        self.detector = HandGestureDetector()

        # ================================================================
        # COMENZI DE MISCARE (WASD, SPACE, CTRL, ALT, SHIFT)
        # ================================================================
        # Mana stanga: set de taste tinute apasate simultan (WASD)
        self.left_held = set()
        # Mana dreapta: o singura tasta bloc (inertie pentru stabilitate)
        self.right_held = None

        # Mod pentru WASD mana stanga:
        # False = hold continuu, True = tap pe directia dominanta
        self.left_wasd_tap_mode = False
        self.left_tap_last_key = None
        self.left_tap_last_press_time = 0
        self.left_tap_needs_reset = False
        self.left_tap_repeat_seconds = 0.5
        self.left_tap_far_multiplier = 2.0

        # ================================================================
        # GESTUL PALM DESCHIS (OPEN PALM)
        # ================================================================
        # Stari detectie palme deschise
        self.left_open = False
        self.right_open = False
        self.both_open = False

        # Timeri pentru delay-uri (previne declansare instantanee)
        self.left_open_start = None
        self.right_open_start = None
        self.both_open_start = None

        # Delay configurable in secunde
        self.open_hold_seconds = 1
        # Comportament pe mana stanga: apasa R dupa delay
        self.delay_left_open = True
        # Comportament pe mana dreapta: tine E apasata imediat (fara delay)
        self.delay_right_open = False
        # Comportament ambele maini: apasa F dupa delay
        self.delay_both_open = True

        # ================================================================
        # GESTUL THUMB (DEGET MARE INTINS)
        # ================================================================
        # Stari detectie thumb
        self.left_thumb = False
        self.right_thumb = False
        self.both_thumb = False

        # Timeri pentru delay-uri
        self.left_thumb_start = None
        self.right_thumb_start = None
        self.both_thumb_start = None

        # Delay configurable in secunde
        self.thumb_hold_seconds = 1
        # Comportament: apasa TAB o data dupa delay
        self.delay_left_thumb = True
        # Comportament: apasa Q o data dupa delay
        self.delay_right_thumb = True
        # Comportament: apasa ESC o data dupa delay
        self.delay_both_thumb = True

        # ================================================================
        # GESTUL PEACE SIGN (INDEX + MIDDLE RIDICATI)
        # ================================================================
        # Stare detectie peace sign
        self.right_peace = False

        # Timer pentru delay
        self.right_peace_start = None

        # Delay configurable in secunde
        self.peace_hold_seconds = 1
        # Comportament: apasa T o data dupa delay
        self.delay_right_peace = True

        # ================================================================
        # GESTUL PINKY (DEGET MIC RIDICAT)
        # ================================================================
        # Stari detectie pinky
        self.left_pinky = False
        self.right_pinky = False

        # Timeri pentru delay-uri
        self.left_pinky_start = None
        self.right_pinky_start = None

        # Delay configurable in secunde
        self.pinky_hold_seconds = 1
        # Comportament: apasa ENTER o data dupa delay
        self.delay_left_pinky = True
        # Comportament: tine Z apasata dupa delay
        self.delay_right_pinky = True

    def _sync_keys(self, current_keys, target_keys):
        """Sincronizeaza tastele: elibereaza cele nefiind necesare, apasa cele noi.

        Compara set de taste actuale cu set tinta si emite comenzi
        hold/release pentru taste care s-au schimbat.

        Args:
            current_keys: set de taste tinute apasate acum
            target_keys: set de taste care trebuie tinute acum

        Returns:
            set: noul set de taste tinute apasate (identic cu target_keys)
        """

        for key in current_keys - target_keys:
            self.keyboard.release(key)

        for key in target_keys - current_keys:
            self.keyboard.hold(key)

        return set(target_keys)

    def _get_axis_targets(self, center, circle, deadzone):
        """Determina care taste de miscare trebuie apasate.

        Verifica pozitia mainii relativ la zona de control si emite
        taste WASD corespunzatoare directiilor active pe axe.

        Args:
            center: tupla (x, y) pozitia centrului mainii
            circle: zona de detectie
            deadzone: zona neutra

        Returns:
            set: taste WASD care trebuie apasate (W=sus, S=jos, A=stanga, D=dreapta)
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
        """Determina tasta bloc (SPACE, CTRL, ALT, SHIFT) cu stabilitate.

        Implementeaza inertie: pastreaza tasta activa pana cand se depaseste
        pragul complet pentru a previne ciclarea rapida intre taste.

        Args:
            current_target: tasta bloc activa acum (sau None)
            center: tupla (x, y) pozitia centrului mainii
            circle: zona de detectie
            deadzone: zona neutra
            mapping: dictionar mapare directie -> tasta

        Returns:
            str: tasta bloc (SPACE/CTRL/ALT/SHIFT) sau None
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
        """Mentine sau elibereaza o singura tasta in functie de stare.

        Verifica daca tasta trebuie sa treaca din hold la release sau invers.

        Args:
            current_state: stare anterioara (True=held, False=released)
            target_state: starea tinta detectata
            key: nume tasta

        Returns:
            bool: noua stare
        """

        if target_state and not current_state:
            self.keyboard.hold(key)
        elif not target_state and current_state:
            self.keyboard.release(key)

        return target_state

    def _reset_left_tap_state(self):
        """Reseteaza starea interna pentru modul tap WASD al mainii stangi."""

        self.left_tap_last_key = None
        self.left_tap_last_press_time = 0
        self.left_tap_needs_reset = False

    def _set_left_wasd_tap_mode(self, enabled):
        """Seteaza modul WASD pentru mana stanga si sincronizeaza starea tap."""

        self.left_wasd_tap_mode = enabled
        self._reset_left_tap_state()
        if enabled:
            self.left_held = self._sync_keys(self.left_held, set())

    def _toggle_left_wasd_tap_mode(self):
        """Comuta modul WASD al mainii stangi intre hold si tap."""

        self._set_left_wasd_tap_mode(not self.left_wasd_tap_mode)

    def _get_single_axis_target(self, center, circle, deadzone):
        """Alege o singura tasta WASD pe axa dominanta (fara diagonale).

        In modul tap, directia trebuie sa fie strict una singura. Daca deplasarea
        depaseste deadzone pe ambele axe, se alege axa cu magnitudine mai mare.

        Returns:
            str: una dintre tastele WASD, sau None pentru neutral/outside.
        """

        direction = self.detector.get_direction(center, circle, deadzone)
        if direction in ("neutral", "outside"):
            return None

        cx, cy = circle["center"]
        x, y = center
        dx = x - cx
        dy = y - cy
        radius = deadzone["radius"]
        horizontal_strength = abs(dx)
        vertical_strength = abs(dy)

        if horizontal_strength <= radius and vertical_strength <= radius:
            return None

        if horizontal_strength >= vertical_strength:
            if horizontal_strength <= radius:
                return None
            return "D" if dx > 0 else "A"

        if vertical_strength <= radius:
            return None
        return "S" if dy > 0 else "W"

    def _process_left_tap_mode(self, center, circle, deadzone, now):
        """Proceseaza WASD in modul tap pentru mana stanga.

        Comportament:
        - directie unica pe axa dominanta;
        - langa deadzone: un singur tap pana la reset (revenire in neutral/outside);
        - departe de deadzone: repetare la interval fix.
        """

        self.left_held = self._sync_keys(self.left_held, set())

        target_key = self._get_single_axis_target(center, circle, deadzone)
        if not target_key:
            self._reset_left_tap_state()
            return

        cx, cy = circle["center"]
        x, y = center
        dx = x - cx
        dy = y - cy

        if target_key in ("A", "D"):
            dominant_strength = abs(dx)
        else:
            dominant_strength = abs(dy)

        far_threshold = deadzone["radius"] * self.left_tap_far_multiplier
        is_far = dominant_strength >= far_threshold

        if target_key != self.left_tap_last_key:
            self.keyboard.press(target_key)
            self.left_tap_last_key = target_key
            self.left_tap_last_press_time = now
            self.left_tap_needs_reset = not is_far
            return

        if self.left_tap_needs_reset and not is_far:
            return

        if not is_far:
            self.left_tap_needs_reset = True
            return

        if now - self.left_tap_last_press_time >= self.left_tap_repeat_seconds:
            self.keyboard.press(target_key)
            self.left_tap_last_press_time = now

    def process_open_palms(self, left_landmarks, right_landmarks):
        """Proceseaza palmele deschise pentru actiuni de interactiune.

        Palma stanga declanseaza R o singura data la deschidere.
        Palma dreapta mentine E cat timp ramane deschisa.
        Cand ambele palme sunt deschise simultan, se apasa F o singura data.
        """

        left_open = self.detector.is_open_palm(left_landmarks)
        right_open = self.detector.is_open_palm(right_landmarks)
        both_open = left_open and right_open

        now = time.time()

        if not left_open and not right_open:
            was_right_open = self.right_open
            self.left_open = False
            self.both_open = False
            self.left_open_start = None
            self.right_open_start = None
            self.both_open_start = None
            if was_right_open:
                self.keyboard.release(KeyboardMapper.RIGHT_OPEN_HOLD)
            self.right_open = False
            return

        if both_open:
            if self.delay_both_open:
                if self.both_open_start is None:
                    self.both_open_start = (
                        self.left_open_start or self.right_open_start or now
                    )
                if now - self.both_open_start < self.open_hold_seconds:
                    return

            if not self.both_open:
                if self.right_open:
                    self.keyboard.release(KeyboardMapper.RIGHT_OPEN_HOLD)
                    self.right_open = False
                self.keyboard.press(KeyboardMapper.BOTH_OPEN_PRESS)
            self.both_open = True
            self.left_open = False
            self.right_open = False
            self.left_open_start = None
            self.right_open_start = None
            self.both_open_start = None
            return

        if left_open:
            if self.delay_left_open:
                if self.left_open_start is None:
                    self.left_open_start = now
                if now - self.left_open_start < self.open_hold_seconds:
                    self.right_open = self._sync_hold_key(
                        self.right_open,
                        right_open,
                        KeyboardMapper.RIGHT_OPEN_HOLD,
                    )
                    return

            if not self.left_open:
                self.keyboard.press(KeyboardMapper.LEFT_OPEN_PRESS)
            self.left_open = True
            self.both_open = False
            self.left_open_start = None
        else:
            self.left_open = False
            self.left_open_start = None

        if right_open:
            if self.delay_right_open:
                if self.right_open_start is None:
                    self.right_open_start = now
                if now - self.right_open_start < self.open_hold_seconds:
                    self.both_open = False
                    return

            self.right_open = self._sync_hold_key(
                self.right_open,
                True,
                KeyboardMapper.RIGHT_OPEN_HOLD,
            )
        else:
            self.right_open = self._sync_hold_key(
                self.right_open,
                False,
                KeyboardMapper.RIGHT_OPEN_HOLD,
            )
            self.right_open_start = None

        self.both_open = False
        self.both_open_start = None

    def process_thumb(self, left_landmarks, right_landmarks):
        """Proceseaza gestul thumb pentru actiuni rapide.

        Mana stanga apasa TAB o singura data la detectie si comuta
        modul WASD pentru mana stanga (hold <-> tap).
        Mana dreapta apasa Q o singura data la detectie si comuta
        acelasi mod WASD pentru mana stanga.
        Cand ambele maini fac thumb simultan, se apasa ESC o singura data
        si modul WASD revine fortat la hold normal.
        """

        left_thumb = self.detector.is_thumb(left_landmarks, "left")
        right_thumb = self.detector.is_thumb(right_landmarks, "right")
        both_thumb = left_thumb and right_thumb

        now = time.time()

        if not left_thumb and not right_thumb:
            self.left_thumb = False
            self.right_thumb = False
            self.both_thumb = False
            self.left_thumb_start = None
            self.right_thumb_start = None
            self.both_thumb_start = None
            return

        if both_thumb:
            if self.delay_both_thumb:
                if self.both_thumb_start is None:
                    self.both_thumb_start = (
                        self.left_thumb_start or self.right_thumb_start or now
                    )
                if now - self.both_thumb_start < self.thumb_hold_seconds:
                    return

            if not self.both_thumb:
                self.keyboard.press(KeyboardMapper.BOTH_THUMB_PRESS)
                self._set_left_wasd_tap_mode(False)
            self.both_thumb = True
            self.left_thumb = False
            self.right_thumb = False
            self.left_thumb_start = None
            self.right_thumb_start = None
            self.both_thumb_start = None
            return

        if left_thumb:
            if self.delay_left_thumb:
                if self.left_thumb_start is None:
                    self.left_thumb_start = now
                if now - self.left_thumb_start < self.thumb_hold_seconds:
                    self.right_thumb = False
                    return

            if not self.left_thumb:
                self.keyboard.press(KeyboardMapper.LEFT_THUMB_PRESS)
                self._toggle_left_wasd_tap_mode()
            self.left_thumb = True
            self.right_thumb = False
            self.both_thumb = False
            self.left_thumb_start = None
        else:
            self.left_thumb = False
            self.left_thumb_start = None

        if right_thumb:
            if self.delay_right_thumb:
                if self.right_thumb_start is None:
                    self.right_thumb_start = now
                if now - self.right_thumb_start < self.thumb_hold_seconds:
                    self.both_thumb = False
                    return

            if not self.right_thumb:
                self.keyboard.press(KeyboardMapper.RIGHT_THUMB_PRESS)
                self._toggle_left_wasd_tap_mode()
            self.right_thumb = True
            self.left_thumb = False
            self.both_thumb = False
            self.right_thumb_start = None
        else:
            self.right_thumb = False
            self.right_thumb_start = None

        self.both_thumb_start = None

    def process_left(self, landmarks, center, circle, deadzone):
        """Proceseaza mana stanga: comenzi de miscare (WASD).

        Verifica daca mana este in configuratie valida (pumn sau index ridicat)
        si activeaza taste directionale dupa pozitia mainii in zonele de detectie.
        In modul normal tine tastele apasate, iar in modul tap apasa o singura
        tasta pe axa dominanta cu repetare controlata cand mana este departe.

        Args:
            landmarks: lista de 21 landmark-uri
            center: tupla (x, y) centrul mainii
            circle: zona de detectie
            deadzone: zona neutra
        """

        if not (
            self.detector.is_fist(landmarks)
            or self.detector.is_index_finger_up(landmarks)
        ):
            self.left_held = self._sync_keys(self.left_held, set())
            self._reset_left_tap_state()
            return

        now = time.time()

        if self.left_wasd_tap_mode:
            self._process_left_tap_mode(center, circle, deadzone, now)
            return

        target_keys = self._get_axis_targets(center, circle, deadzone)
        self.left_held = self._sync_keys(self.left_held, target_keys)
        self._reset_left_tap_state()

    def process_right(self, landmarks, center, circle, deadzone):
        """Proceseaza mana dreapta: comenzi bloc (SPACE, CTRL, ALT, SHIFT).

        Activeaza o singura tasta bloc la un moment, cu inertie pentru stabilitate
        si evitare ciclare rapida intre taste.

        Args:
            landmarks: lista de 21 landmark-uri
            center: tupla (x, y) centrul mainii
            circle: zona de detectie
            deadzone: zona neutra
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

    def process_peace_sign(self, right_landmarks):
        """Proceseaza gestul peace sign pe mana dreapta pentru actiuni rapide.

        Detecteaza peace sign (index + middle sus) si apasa T o singura data
        dupa delay-ul confirmat.

        Args:
            right_landmarks: lista de 21 landmark-uri din mana dreapta
        """

        right_peace = self.detector.is_peace_sign(right_landmarks)

        now = time.time()

        if not right_peace:
            self.right_peace = False
            self.right_peace_start = None
            return

        if self.delay_right_peace:
            if self.right_peace_start is None:
                self.right_peace_start = now
            if now - self.right_peace_start < self.peace_hold_seconds:
                return

        if not self.right_peace:
            self.keyboard.press(KeyboardMapper.RIGHT_PEACE_PRESS)
        self.right_peace = True
        self.right_peace_start = None

    def process_pinky(self, left_landmarks, right_landmarks):
        """Proceseaza gestul pinky pentru actiuni rapide.

        Mana stanga: apasa ENTER o singura data dupa delay-ul confirmat.
        Mana dreapta: tine apasata Z cat timp degetul mic este ridicat.

        Args:
            left_landmarks: lista de 21 landmark-uri din mana stanga
            right_landmarks: lista de 21 landmark-uri din mana dreapta
        """

        left_pinky = self.detector.is_pinky_up(left_landmarks)
        right_pinky = self.detector.is_pinky_up(right_landmarks)

        now = time.time()

        if left_pinky:
            if self.delay_left_pinky:
                if self.left_pinky_start is None:
                    self.left_pinky_start = now
                if now - self.left_pinky_start < self.pinky_hold_seconds:
                    right_pinky_state = right_pinky
                    self.right_pinky = self._sync_hold_key(
                        self.right_pinky,
                        right_pinky_state,
                        KeyboardMapper.RIGHT_PINKY_HOLD,
                    )
                    return

            if not self.left_pinky:
                self.keyboard.press(KeyboardMapper.LEFT_PINKY_PRESS)
            self.left_pinky = True
            self.left_pinky_start = None
        else:
            self.left_pinky = False
            self.left_pinky_start = None

        if right_pinky:
            if self.delay_right_pinky:
                if self.right_pinky_start is None:
                    self.right_pinky_start = now
                if now - self.right_pinky_start < self.pinky_hold_seconds:
                    return

            self.right_pinky = self._sync_hold_key(
                self.right_pinky,
                True,
                KeyboardMapper.RIGHT_PINKY_HOLD,
            )
        else:
            self.right_pinky = self._sync_hold_key(
                self.right_pinky,
                False,
                KeyboardMapper.RIGHT_PINKY_HOLD,
            )
            self.right_pinky_start = None
