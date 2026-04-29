from ..vision import HeadDirectionDetector
from ..mapping import MouseMapper


class HeadMouseEngine:
    def __init__(self, mouse):
        self.mouse = mouse
        self.detector = HeadDirectionDetector()

    def process(self, point, circle, deadzone):
        direction = self.detector.get_direction(point, circle, deadzone)
        speed = MouseMapper.SPEED
        if direction == "up":
            self.mouse.move_up(speed)
        elif direction == "down":
            self.mouse.move_down(speed)
        elif direction == "left":
            self.mouse.move_left(speed)
        elif direction == "right":
            self.mouse.move_right(speed)
