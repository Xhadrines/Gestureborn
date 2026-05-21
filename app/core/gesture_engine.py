"""Engine central de procesare de gesturi.

Componenta principal care coordoneaza:
- Detectie geste pe baza landmark-urilor mainilor si capului
- Procesare comenzi tastatura pe baza gesturilor mainilor
- Control mouse pe baza pozitiei capului si gesturilor pinch/hold
- Gestionare geste speciale (Peace sign pentru exit)
"""

import time

from .hand_keyboard_engine import HandKeyboardEngine
from .head_mouse_engine import HeadMouseEngine
from .mouse_hold_engine import MouseHoldEngine
from ..mapping import KeyboardMapper


class GestureEngine:
    """Componenta principal pentru gesturi detectate.

    Coordoneaza engine-urile pentru:
    - Miscare mouse controlata de cap (HeadMouseEngine)
    - Click-uri mouse cu degete (MouseHoldEngine)
    - Comenzi tastatura cu maini (HandKeyboardEngine)
    """

    def __init__(self, mouse, keyboard, webcam):
        """Initializeaza engine-ul cu controllere si camera.

        Args:
            mouse: MouseController pentru comenzi mouse
            keyboard: KeyboardController pentru comenzi tastatura
            webcam: Webcam instance cu informatii detectie
        """

        # Creaza engine-uri specializate pentru fiecare tip de control
        self.mouse_engine = HeadMouseEngine(mouse)
        self.mouse_hold_engine = MouseHoldEngine(mouse)
        self.hand_engine = HandKeyboardEngine(keyboard)
        self.webcam = webcam

        # Gestionare Peace sign (iesire aplicatie)
        # Peace sign cere mentinere 2 secunde pentru a se activa
        self.left_peace_start = None
        self.peace_hold_seconds = 2.0

    def _format_keys(self, keys):
        """Formateaza tastele activate intr-un sir stabil si usor de citit."""

        order = ["W", "A", "S", "D", "SPACE", "CTRL", "ALT", "SHIFT"]
        ordered_keys = [key for key in order if key in keys]
        return "+".join(ordered_keys) if ordered_keys else "neutral"

    def _describe_key(self, key):
        """Descrie o tasta de miscare in limbaj natural."""

        descriptions = {
            "W": "W = Forward",
            "A": "A = Strafe Left",
            "S": "S = Back",
            "D": "D = Strafe Right",
            "SPACE": "SPACE = Jump",
            "CTRL": "CTRL = Sneak",
            "ALT": "ALT = Sprint",
            "SHIFT": "SHIFT = Run",
        }
        return descriptions.get(key, key)

    def _format_key_descriptions(self, keys):
        """Formateaza tastele activate impreuna cu explicatia lor."""

        order = ["W", "A", "S", "D", "SPACE", "CTRL", "ALT", "SHIFT"]
        ordered_keys = [key for key in order if key in keys]
        if not ordered_keys:
            return "neutral"
        return " + ".join(self._describe_key(key) for key in ordered_keys)

    def _format_head_directions(self, directions):
        """Formateaza directiile capului in limbaj natural."""

        order = ["up", "left", "down", "right"]
        labels = {
            "up": "Look Up",
            "down": "Look Down",
            "left": "Look Left",
            "right": "Look Right",
        }
        ordered = [labels[direction] for direction in order if direction in directions]
        return "+".join(ordered) if ordered else "neutral"

    def _describe_tap_mode(self, key, center, circle, deadzone):
        """Descrie modul tap pentru mana stanga."""

        cx, cy = circle["center"]
        x, y = center
        dx = x - cx
        dy = y - cy

        if key in ("A", "D"):
            dominant_strength = abs(dx)
        else:
            dominant_strength = abs(dy)

        far_threshold = deadzone["radius"] * self.hand_engine.left_tap_far_multiplier
        is_far = dominant_strength >= far_threshold

        if is_far:
            return f"{self._describe_key(key)} -> tap repetat automat"

        return f"{self._describe_key(key)} -> tap o singura data"

    def _describe_head_status(self, face_result):
        """Returneaza starea curenta a capului si efectul asupra mouse-ului."""

        if not face_result.face_landmarks:
            return "Head: no face detected"

        nose = face_result.face_landmarks[0][1]
        point = (int(nose.x * 1280), int(nose.y * 720))
        directions = self.mouse_engine.detector.get_axes(
            point,
            self.webcam.head_circle,
            self.webcam.head_deadzone,
        )

        if not directions:
            if self.webcam.point_in_deadzone(point, self.webcam.head_deadzone):
                return "Head: neutral -> mouse stopped"
            if self.webcam.point_in_circle(point, self.webcam.head_circle):
                return "Head: inside zone -> no movement"
            return "Head: outside zone -> no movement"

        speed = self.mouse_engine.get_speed(
            point,
            self.webcam.head_circle,
            self.webcam.head_deadzone,
        )
        direction_text = self._format_head_directions(directions)
        return f"Head: {direction_text} -> mouse move | speed {speed}"

    def _describe_left_status(self, left_hand, left_center):
        """Returneaza gestul curent al mainii stangi si efectul lui."""

        if not left_hand or not left_center:
            return ["Left: no hand detected"]

        detector = self.hand_engine.detector

        if self.hand_engine.both_open:
            return ["Both hands: open palm -> F"]

        if self.hand_engine.both_thumb:
            return ["Both hands: thumb -> ESC"]

        if self.mouse_hold_engine.detector.is_peace_sign(left_hand):
            return ["Left: peace sign -> exit after 2s"]

        if detector.is_open_palm(left_hand):
            return ["Left: open palm -> R / Ready-Sheathe"]

        if detector.is_thumb(left_hand, "left"):
            mode = "tap" if self.hand_engine.left_wasd_tap_mode else "hold"
            return [f"Left: thumb -> TAB / Character Menu | WASD {mode} mode"]

        if detector.is_pinky_up(left_hand):
            return ["Left: pinky -> ENTER / Confirm-Accept"]

        if detector.is_index_finger_up(left_hand) or detector.is_fist(left_hand):
            if self.hand_engine.left_wasd_tap_mode:
                target_key = self.hand_engine.get_single_axis_target(
                    left_center,
                    self.webcam.left_hand_circle,
                    self.webcam.left_hand_deadzone,
                )
                movement = (
                    self._describe_tap_mode(
                        target_key,
                        left_center,
                        self.webcam.left_hand_circle,
                        self.webcam.left_hand_deadzone,
                    )
                    if target_key
                    else "neutral"
                )
            else:
                target_keys = self.hand_engine.get_axis_targets(
                    left_center,
                    self.webcam.left_hand_circle,
                    self.webcam.left_hand_deadzone,
                )
                movement = self._format_key_descriptions(target_keys)

            click_state = (
                "M2 / right click hold"
                if self.mouse_hold_engine.left_held
                else "M2 / right click release"
            )
            return [f"Left: move {movement}", click_state]

        return ["Left: hand detected"]

    def _describe_right_status(self, right_hand, right_center):
        """Returneaza gestul curent al mainii drepte si efectul lui."""

        if not right_hand or not right_center:
            return ["Right: no hand detected"]

        detector = self.hand_engine.detector

        if self.hand_engine.both_open:
            return ["Both hands: open palm -> F"]

        if self.hand_engine.both_thumb:
            return ["Both hands: thumb -> ESC"]

        if detector.is_open_palm(right_hand):
            return ["Right: open palm -> E / Activate"]

        if detector.is_thumb(right_hand, "right"):
            mode = "tap" if self.hand_engine.left_wasd_tap_mode else "hold"
            return [f"Right: thumb -> Q / Favorites | WASD {mode} mode"]

        if detector.is_pinky_up(right_hand):
            return ["Right: pinky -> Z / Shout-Power"]

        if detector.is_peace_sign(right_hand):
            return ["Right: peace sign -> T / Wait"]

        if detector.is_index_finger_up(right_hand) or detector.is_fist(right_hand):
            target = self.hand_engine.get_locked_target(
                self.hand_engine.right_held,
                right_center,
                self.webcam.right_hand_circle,
                self.webcam.right_hand_deadzone,
                KeyboardMapper.RIGHT_MAP,
            )
            movement = self._describe_key(target) if target else "neutral"
            click_state = (
                "M1 / left click hold"
                if self.mouse_hold_engine.right_held
                else "M1 / left click release"
            )
            return [f"Right: move {movement}", click_state]

        return ["Right: hand detected"]

    def build_status_lines(
        self, face_result, left_hand, left_center, right_hand, right_center
    ):
        """Construieste liniile care apar in panoul de stare."""

        lines = [self._describe_head_status(face_result)]

        if face_result.face_landmarks:
            lines.append(
                f"Head Circle: {self.webcam.head_in_circle} | Head DeadZone: {self.webcam.head_in_deadzone}"
            )

        lines.append(
            f"Left Hand Circle: {self.webcam.left_hand_in_circle} | Left Hand DeadZone: {self.webcam.left_hand_in_deadzone}"
        )
        lines.extend(self._describe_left_status(left_hand, left_center))
        lines.append(
            f"Right Hand Circle: {self.webcam.right_hand_in_circle} | Right Hand DeadZone: {self.webcam.right_hand_in_deadzone}"
        )
        lines.extend(self._describe_right_status(right_hand, right_center))

        return lines

    def _describe_hand_gesture(self, landmarks, hand_side):
        """Returneaza o eticheta scurta pentru gestul curent al unei maini."""

        if not landmarks:
            return None

        detector = self.hand_engine.detector

        if detector.is_open_palm(landmarks):
            return f"{hand_side}: open palm"

        if detector.is_thumb(landmarks, hand_side):
            return f"{hand_side}: thumb"

        if detector.is_pinky_up(landmarks):
            return f"{hand_side}: pinky"

        if detector.is_peace_sign(landmarks):
            return f"{hand_side}: peace"

        if detector.is_index_finger_up(landmarks):
            return f"{hand_side}: index up"

        if detector.is_fist(landmarks):
            return f"{hand_side}: fist"

        return None

    def _update_active_gesture_text(self, left_hand, right_hand):
        """Actualizeaza textul afisat in overlay-ul camerei."""

        labels = []

        left_label = self._describe_hand_gesture(left_hand, "Left")
        if left_label:
            labels.append(left_label)

        right_label = self._describe_hand_gesture(right_hand, "Right")
        if right_label:
            labels.append(right_label)

        self.webcam.active_gesture_text = " | ".join(labels) if labels else None

    def update(self, hand_result, face_result):
        """Actualizeaza starea aplicatiei pentru frame-ul curent.

        Proceseaza:
        1. Capul pentru mouse movement (HeadMouseEngine)
        2. Mainile pentru tastatura si click-uri (HandKeyboardEngine + MouseHoldEngine)
        3. Gesturile speciale (Peace sign pentru exit)

        Args:
            hand_result: MediaPipe resultado detectie maini
            face_result: MediaPipe resultado detectie fata
        """

        # ================================================
        # PROCESARE CAP: CONTROL MOUSE
        # ================================================
        if face_result.face_landmarks:
            # Foloseste nasul pentru pozitie cap (landmark 1 din fata)
            nose = face_result.face_landmarks[0][1]
            point = (int(nose.x * 1280), int(nose.y * 720))
            # Comanda miscari mouse pe baza pozitiei capului
            self.mouse_engine.process(
                point,
                self.webcam.head_circle,
                self.webcam.head_deadzone,
            )

        # ================================================
        # PROCESARE MAINI: TASTATURA SI CLICK-URI
        # ================================================
        # Atribuie mainile pe baza pozitiei (stanga vs dreapta)
        left_hand, left_center, right_hand, right_center = self.webcam.split_hands(
            hand_result.hand_landmarks
        )

        # Procesare geste speciale (palm, thumb, pinky)
        self.hand_engine.process_open_palms(left_hand, right_hand)
        self.hand_engine.process_thumb(left_hand, right_hand)
        self.hand_engine.process_pinky(left_hand, right_hand)

        # ================================================
        # PROCESARE MANA STANGA
        # ================================================
        if left_hand and left_center:
            # Verifica Peace sign pe mana stanga (iesire)
            if self.mouse_hold_engine.detector.is_peace_sign(left_hand):
                now = time.time()
                if self.left_peace_start is None:
                    self.left_peace_start = now
                elif now - self.left_peace_start >= self.peace_hold_seconds:
                    # Iesire: setam flag si resetam hold-uri
                    self.webcam.should_close = True
                    self.mouse_hold_engine.process_left([])
                    self.mouse_hold_engine.process_right([])
                    return
            else:
                # Reinitializeaza timer cand Peace sign nu e detectat
                self.left_peace_start = None

            # Procesare miscare si click-uri mana stanga
            self.hand_engine.process_left(
                left_hand,
                left_center,
                self.webcam.left_hand_circle,
                self.webcam.left_hand_deadzone,
            )
            self.mouse_hold_engine.process_left(left_hand)
        else:
            # Reinitializeaza cand mana nu e detectata
            self.left_peace_start = None
            self.mouse_hold_engine.process_left([])

        # ================================================
        # PROCESARE MANA DREAPTA
        # ================================================
        if right_hand and right_center:
            # Verifica Peace sign pe mana dreapta
            self.hand_engine.process_peace_sign(right_hand)

            # Procesare miscare si click-uri mana dreapta
            self.hand_engine.process_right(
                right_hand,
                right_center,
                self.webcam.right_hand_circle,
                self.webcam.right_hand_deadzone,
            )
            self.mouse_hold_engine.process_right(right_hand)
        else:
            # Reinitializeaza cand mana nu e detectata
            self.mouse_hold_engine.process_right([])
