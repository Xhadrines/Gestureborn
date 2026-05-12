"""Detector de directie cap relativ la zonele de control.

Identifica directia capului in functie de pozitia acestuia
fata de cercurile de detectie si deadzone-uri. Foloseste coordonate
face landmarks (nasul) pentru a determina directie.
"""

import math


class HeadDirectionDetector:
    """Analizor de pozitie cap.

    Mapare pozitie cap -> directii (sus, jos, stanga, dreapta, neutru, exterior).
    Calculeaza atat directie unica cat si seturi de directii pentru diagonal.
    """

    def get_direction(self, point, circle, deadzone):
        """Determina directia unica a capului.

        Returneaza directia preponderenta pe o singura axa.

        Args:
            point: tupla (x, y) pozitia capului in pixeli
            circle: dict cu centrul si raza cercului de detectie
            deadzone: dict cu centrul si raza zonei neutre

        Returns:
            str: "up", "down", "left", "right", "neutral", "outside"
        """

        cx, cy = circle["center"]
        x, y = point
        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx * dx + dy * dy)

        # In deadzone = neutral
        if dist < deadzone["radius"]:
            return "neutral"

        # Afara cercului = outside
        if dist > circle["radius"]:
            return "outside"

        # Determina directie principala
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        return "down" if dy > 0 else "up"

    def get_axes(self, point, circle, deadzone):
        """Determina care directii sunt active pe axe.

        Permite combinatia sus-stanga, sus-dreapta etc. pentru miscare diagonala.
        Fiecare axa (X, Y) se evalueaza independent.

        Args:
            point: tupla (x, y) pozitia capului in pixeli
            circle: dict cu centrul si raza cercului de detectie
            deadzone: dict cu centrul si raza zonei neutre

        Returns:
            set: directiile active (ex: {'up', 'left'} pentru diagonal)
        """

        cx, cy = circle["center"]
        x, y = point
        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx * dx + dy * dy)

        # In deadzone = nu exista directii active
        if dist < deadzone["radius"]:
            return set()

        # Afara cercului = nu exista directii active
        if dist > circle["radius"]:
            return set()

        directions = set()

        # Verifica axa X: stanga sau dreapta daca deplasarea orizontala e semnificativa
        if abs(dx) > deadzone["radius"]:
            directions.add("right" if dx > 0 else "left")

        # Verifica axa Y: sus sau jos daca deplasarea verticala e semnificativa
        if abs(dy) > deadzone["radius"]:
            directions.add("down" if dy > 0 else "up")

        return directions
