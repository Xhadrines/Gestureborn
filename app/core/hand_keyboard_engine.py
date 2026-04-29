from ..vision import HandGestureDetector
from ..mapping import KeyboardMapper


class HandKeyboardEngine:
    def __init__(self, keyboard):
        self.keyboard = keyboard
        self.detector = HandGestureDetector()
        self.left_held = None
        self.right_held = None

    def _update_key(self, current, target):
        if current and current != target:
            self.keyboard.release(current)
            current = None
        if target and current != target:
            self.keyboard.hold(target)
            current = target
        if not target and current:
            self.keyboard.release(current)
            current = None
        return current

    def process_left(self, landmarks, center, circle, deadzone):
        if not (
            self.detector.is_fist(landmarks)
            or self.detector.is_index_finger_up(landmarks)
        ):
            self.left_held = self._update_key(self.left_held, None)
            return
        direction = self.detector.get_direction(center, circle, deadzone)
        target = KeyboardMapper.LEFT_MAP.get(direction)
        self.left_held = self._update_key(self.left_held, target)

    def process_right(self, landmarks, center, circle, deadzone):
        if not (
            self.detector.is_fist(landmarks)
            or self.detector.is_index_finger_up(landmarks)
        ):
            self.right_held = self._update_key(self.right_held, None)
            return
        direction = self.detector.get_direction(center, circle, deadzone)
        target = KeyboardMapper.RIGHT_MAP.get(direction)
        self.right_held = self._update_key(self.right_held, target)
