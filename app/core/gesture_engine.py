from .hand_keyboard_engine import HandKeyboardEngine
from .head_mouse_engine import HeadMouseEngine
from .mouse_hold_engine import MouseHoldEngine


class GestureEngine:
    def __init__(self, mouse, keyboard, webcam):
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

        left_hand = None
        right_hand = None

        if hand_result.hand_landmarks:
            if len(hand_result.hand_landmarks) >= 1:
                left_hand = hand_result.hand_landmarks[0]
                left_center = self.webcam.get_landmark_center(left_hand)
                if left_center:
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

            if len(hand_result.hand_landmarks) >= 2:
                right_hand = hand_result.hand_landmarks[1]
                right_center = self.webcam.get_landmark_center(right_hand)
                if right_center:
                    self.hand_engine.process_right(
                        right_hand,
                        right_center,
                        self.webcam.right_hand_circle,
                        self.webcam.right_hand_deadzone,
                    )
                    self.mouse_hold_engine.process_right(right_hand)

        if not left_hand:
            self.mouse_hold_engine.process_left([])

        if not right_hand:
            self.mouse_hold_engine.process_right([])
