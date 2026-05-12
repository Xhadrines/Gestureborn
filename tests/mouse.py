"""Module de teste pentru MouseController.

Verifica functionalitatea:
- Miscari pe axele X/Y
- Click-uri scurte si lungi (left/right)
- Hold/release pentru drag and drop

NOTA: Necesita focus pe aplicatia tinta (ex: Skyrim) inainte de test.
"""

from app.controller.mouse import MouseController
import time


class MouseTest:
    """Suite de teste pentru MouseController.

    Testeaza:
    - Miscari pe directii (up/down/left/right)
    - Click-uri rapide (short)
    - Click-uri lungi (long)
    - Hold/release pentru operatii drag and drop
    """

    def __init__(self):
        """Initializeaza dispozitivul mouse virtual."""

        self.mouse = MouseController()

    def run(self):
        """Executa suita completa de teste in ordine.

        Se asteapta 5 secunde pentru a permite focus pe aplicatia tinta
        inainte de a incepe testele.
        """

        # Acorda timp pentru a muta focusul in aplicatia tinta inainte de test
        print("Ai 5 secunde sa dai focus pe aplicatia tinta...")
        time.sleep(5)

        # Ruleaza pe rand testele de miscare si click
        print("MOUSE TEST STARTED...")

        self.move_test()
        self.click_short_test()
        self.click_long_test()
        self.click_hold_test()

        print("MOUSE TEST COMPLETED!")

    def move_test(self):
        """Testeaza directiile de baza pentru deplasarea mouse-ului.

        Fiecare directie e testata timp de 3 secunde cu miscari repetate.
        """

        print("MOVE RIGHT...")
        self._hold_move(self.mouse.move_right)

        print("MOVE LEFT...")
        self._hold_move(self.mouse.move_left)

        print("MOVE UP...")
        self._hold_move(self.mouse.move_up)

        print("MOVE DOWN...")
        self._hold_move(self.mouse.move_down)

    def _hold_move(self, func):
        """Helper: trimite repetat evenimentul pentru a simula miscare continua.

        Args:
            func: functie de miscare (move_up/down/left/right)
        """

        start = time.time()
        while time.time() - start < 3:
            func(6)
            time.sleep(0.01)

    def click_short_test(self):
        """Verifica apasarile scurte (click rapid).

        Testeaza:
        - Right click short (0.25s)
        - Left click short (0.25s)
        """

        print("RIGHT CLICK SHORT...")
        self.mouse.right_click_short()
        time.sleep(1)

        print("LEFT CLICK SHORT...")
        self.mouse.left_click_short()
        time.sleep(1)

    def click_long_test(self):
        """Verifica apasarile mai lungi (click prelungit).

        Util pentru interactiuni speciale in jocuri.
        Testeaza:
        - Right click long (0.5s)
        - Left click long (0.5s)
        """

        print("RIGHT CLICK LONG...")
        self.mouse.right_click_long()
        time.sleep(1.5)

        print("LEFT CLICK LONG...")
        self.mouse.left_click_long()
        time.sleep(1.5)

    def click_hold_test(self):
        """Testeaza mentinerea apasata si eliberarea butoanelor.

        Simuleza hold pentru drag and drop:
        1. Apasa buton (hold)
        2. Asteapta 5 secunde
        3. Elibereaza buton (release)
        """

        print("RIGHT CLICK HOLD...")
        self.mouse.right_click_hold()
        time.sleep(5)
        self.mouse.right_click_release()

        print("LEFT CLICK HOLD...")
        self.mouse.left_click_hold()
        time.sleep(5)
        self.mouse.left_click_release()


if __name__ == "__main__":
    MouseTest().run()
