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
