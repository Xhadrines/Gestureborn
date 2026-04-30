"""Engine de control mouse: mapare miscare cap -> miscare mouse.

Utilizeaza detectarea directiei capului pentru a controla miscarea
de mouse cu viteza constanta pe axa selectata.
"""

from ..vision import HeadDirectionDetector
from ..mapping import MouseMapper


class HeadMouseEngine:
    """Procesor de gesturi cap pentru control mouse.

    Detecteaza directiile capului relativ la zona de detectie si
    trimite comenzi de miscare mouse catre controller-ul virtual.
    """

    def __init__(self, mouse):
        """Initializeaza engine-ul cu controller mouse si detector cap."""
        self.mouse = mouse
        self.detector = HeadDirectionDetector()

    def process(self, point, circle, deadzone):
        """Proceseaza pozitia capului si comanda miscari mouse.

        Args:
            point: tupla (x, y) pozitia capului in pixeli
            circle: dict cu centrul si raza cercului de detectie
            deadzone: dict cu centrul si raza zonei neutre
        """
        directions = self.detector.get_axes(point, circle, deadzone)
        speed = MouseMapper.SPEED
        if "up" in directions:
            self.mouse.move_up(speed)
        if "down" in directions:
            self.mouse.move_down(speed)
        if "left" in directions:
            self.mouse.move_left(speed)
        if "right" in directions:
            self.mouse.move_right(speed)
