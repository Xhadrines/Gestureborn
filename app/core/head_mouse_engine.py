"""Engine de control mouse: mapare miscare cap -> miscare mouse.

Utilizeaza detectarea directiei capului pentru a controla miscarea
de mouse. Suporta:
- Viteza dinamica in functie de distanta de la deadzone
- Curba de raspuns pentru control non-linear
- Miscare diagonala simultana pe ambele axe
"""

import math

from ..vision import HeadDirectionDetector
from ..mapping import MouseMapper


class HeadMouseEngine:
    """Procesor de gesturi cap pentru control mouse.

    Detecteaza directiile capului relativ la zona de detectie si
    trimite comenzi de miscare mouse catre controller-ul virtual.
    """

    def __init__(self, mouse):
        """Initializeaza engine-ul cu controller mouse si detector cap.

        Args:
            mouse: MouseController pentru comenzi mouse
        """

        self.mouse = mouse
        self.detector = HeadDirectionDetector()

    def _get_speed(self, point, circle, deadzone):
        """Calculeaza viteza mouse in functie de distanta fata de deadzone.

        Implementeaza viteza dinamica cu curba de raspuns exponentiala.
        Permite control fin aproape de centru si mai rapid la margine.

        Args:
            point: tupla (x, y) pozitia capului
            circle: zona de detectie
            deadzone: zona neutra

        Returns:
            int: viteza
        """

        # Fallback la viteza fixa daca dinamica e dezactivata
        if not MouseMapper.DYNAMIC_SPEED:
            return MouseMapper.SPEED

        # Calculeaza distanta fata de centru
        cx, cy = circle["center"]
        x, y = point
        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx * dx + dy * dy)

        # Determina range-ul activ (intre deadzone si cerc)
        deadzone_radius = deadzone["radius"]
        outer_radius = circle["radius"]
        active_range = outer_radius - deadzone_radius

        if active_range <= 0:
            return MouseMapper.SPEED

        # Normalizeaza distanta in range 0-1
        ratio = (dist - deadzone_radius) / active_range
        ratio = max(0.0, min(1.0, ratio))

        # Aplica curba de raspuns pentru accelerare non-lineara
        ratio = ratio**MouseMapper.SPEED_CURVE

        # Interpoleaza intre min si max viteza
        min_speed = MouseMapper.MIN_SPEED
        max_speed = MouseMapper.MAX_SPEED
        speed = min_speed + ratio * (max_speed - min_speed)
        return max(1, int(round(speed)))

    def get_speed(self, point, circle, deadzone):
        """Wrapper public pentru viteza calculata a capului."""

        return self._get_speed(point, circle, deadzone)

    def process(self, point, circle, deadzone):
        """Proceseaza pozitia capului si comanda miscari mouse.

        Determina directiile active pe ambele axe si emite comenzi
        mouse cu viteza calculata dinamic.

        Args:
            point: tupla (x, y) pozitia capului in pixeli
            circle: dict cu centrul si raza cercului de detectie
            deadzone: dict cu centrul si raza zonei neutre
        """

        # Determina directii active pe axe (pentru miscare diagonala)
        directions = self.detector.get_axes(point, circle, deadzone)

        # Calculeaza viteza pe baza distantei de la deadzone
        speed = self._get_speed(point, circle, deadzone)

        # Emite comenzi mouse pentru directiile active
        if "up" in directions:
            self.mouse.move_up(speed)
        if "down" in directions:
            self.mouse.move_down(speed)
        if "left" in directions:
            self.mouse.move_left(speed)
        if "right" in directions:
            self.mouse.move_right(speed)
