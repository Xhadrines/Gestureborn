from ..vision import HandGestureDetector


class MouseHoldEngine:
    def __init__(self, mouse):
        self.mouse = mouse
        self.detector = HandGestureDetector()
        self.left_held = False
        self.right_held = False

    def _update_hold_state(self, current, target, hold_fn, release_fn):
        if target and not current:
            hold_fn()
            return True

        if not target and current:
            release_fn()
            return False

        return current

    def process_left(self, landmarks):
        target = self.detector.is_index_finger_up(landmarks)
        self.left_held = self._update_hold_state(
            self.left_held,
            target,
            self.mouse.right_click_hold,
            self.mouse.right_click_release,
        )

    def process_right(self, landmarks):
        target = self.detector.is_index_finger_up(landmarks)
        self.right_held = self._update_hold_state(
            self.right_held,
            target,
            self.mouse.left_click_hold,
            self.mouse.left_click_release,
        )
