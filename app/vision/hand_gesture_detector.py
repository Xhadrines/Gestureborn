import math


class HandGestureDetector:
    def is_fist(self, landmarks):
        tips = [8, 12, 16, 20]
        pip = [6, 10, 14, 18]
        folded = 0
        for t, p in zip(tips, pip):
            if landmarks[t].y > landmarks[p].y:
                folded += 1
        return folded >= 3

    def is_index_finger_up(self, landmarks):
        if not landmarks or len(landmarks) < 21:
            return False

        index_up = landmarks[8].y < landmarks[6].y
        middle_folded = landmarks[12].y > landmarks[10].y
        ring_folded = landmarks[16].y > landmarks[14].y
        pinky_folded = landmarks[20].y > landmarks[18].y

        return index_up and middle_folded and ring_folded and pinky_folded

    def is_peace_sign(self, landmarks):
        if not landmarks or len(landmarks) < 21:
            return False

        index_up = landmarks[8].y < landmarks[6].y
        middle_up = landmarks[12].y < landmarks[10].y
        ring_folded = landmarks[16].y > landmarks[14].y
        pinky_folded = landmarks[20].y > landmarks[18].y

        return index_up and middle_up and ring_folded and pinky_folded

    def get_direction(self, center, circle, deadzone):
        cx, cy = circle["center"]
        x, y = center
        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < deadzone["radius"]:
            return "neutral"
        if dist > circle["radius"]:
            return "outside"
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        return "down" if dy > 0 else "up"
