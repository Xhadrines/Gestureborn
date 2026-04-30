"""Engine central de procesare gesturi.

Orchestreaza toti engine-urile de control (mouse, tastatura, hold)
si coordoneaza comunicarea intre detectare si executie actiuni.
"""

from .hand_keyboard_engine import HandKeyboardEngine
from .head_mouse_engine import HeadMouseEngine
from .mouse_hold_engine import MouseHoldEngine


class GestureEngine:
    """Orchestrator principal pentru gesturi detectate.

    Coordoneaza engine-urile pentru:
    - Miscare mouse controlata de cap (HeadMouseEngine)
    - Apasari mouse cu degete (MouseHoldEngine)
    - Comenzi tastatura cu maini (HandKeyboardEngine)
    """

    def __init__(self, mouse, keyboard, webcam):
        """Initializeaza engine-ul cu controllere si camera.

        Args:
            mouse: MouseController pentru comenzi mouse
            keyboard: KeyboardController pentru comenzi tastatura
            webcam: Webcam instance cu informatii detectie
        """
        self.mouse_engine = HeadMouseEngine(mouse)
        self.mouse_hold_engine = MouseHoldEngine(mouse)
        self.hand_engine = HandKeyboardEngine(keyboard)
        self.webcam = webcam

    def update(self, hand_result, face_result):
        if face_result.face_landmarks:
            nose = face_result.face_landmarks[0][1]
            point = (int(nose.x * 1280), int(nose.y * 720))
            self.mouse_engine.process(
                point,
                self.webcam.head_circle,
                self.webcam.head_deadzone,
            )

        left_hand, left_center, right_hand, right_center = self.webcam.split_hands(
            hand_result.hand_landmarks
        )

        if left_hand and left_center:
            if self.mouse_hold_engine.detector.is_peace_sign(left_hand):
                self.webcam.should_close = True
                self.mouse_hold_engine.process_left([])
                self.mouse_hold_engine.process_right([])
                return

            self.hand_engine.process_left(
                left_hand,
                left_center,
                self.webcam.left_hand_circle,
                self.webcam.left_hand_deadzone,
            )
            self.mouse_hold_engine.process_left(left_hand)
        else:
            self.mouse_hold_engine.process_left([])

        if right_hand and right_center:
            self.hand_engine.process_right(
                right_hand,
                right_center,
                self.webcam.right_hand_circle,
                self.webcam.right_hand_deadzone,
            )
            self.mouse_hold_engine.process_right(right_hand)
        else:
            self.mouse_hold_engine.process_right([])
