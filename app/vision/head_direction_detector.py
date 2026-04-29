import math


class HeadDirectionDetector:
    def get_direction(self, point, circle, deadzone):
        cx, cy = circle["center"]
        x, y = point
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
