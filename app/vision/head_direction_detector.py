"""Detector de directie cap relativ la zonele de control.

Identifica directia capului in functie de pozitia acestuia
fata de cercurile de detectie si deadzone.
"""

import math


class HeadDirectionDetector:
    """Analizor de pozitie cap.

    Mapare pozitie cap -> directie unica (sus, jos, stanga, dreapta, neutru, exterior).
    """

    def get_direction(self, point, circle, deadzone):
        """Determina directia unica a capului.

        Returns: "up", "down", "left", "right", "neutral", "outside"
        """
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

    def get_axes(self, point, circle, deadzone):
        """Determina care directii sunt active pe axa.

        Permite combinatia sus-stanga, sus-dreapta etc. pentru miscare diagonala.
        Returns: set cu directiile active
        """
        cx, cy = circle["center"]
        x, y = point
        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < deadzone["radius"]:
            return set()

        if dist > circle["radius"]:
            return set()

        directions = set()

        if abs(dx) > deadzone["radius"]:
            directions.add("right" if dx > 0 else "left")

        if abs(dy) > deadzone["radius"]:
            directions.add("down" if dy > 0 else "up")

        return directions
