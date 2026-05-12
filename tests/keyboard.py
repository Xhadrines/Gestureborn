"""Module de teste pentru KeyboardController.

Verifica functionalitatea:
- Apasari WASD pentru miscare
- Combinatii tasta pentru sprint (W + ALT)
- Taste de actiune (TAB, ESC, SPACE, CTRL)

NOTA: Necesita focus pe aplicatia tinta (ex: Skyrim) inainte de test.
"""

from app.controller.keyboard import KeyboardController
import time


class KeyboardTest:
    """Suite de teste pentru KeyboardController.

    Testeaza:
    - Apasari WASD cu hold/release
    - Combinatii tasta (W + ALT pentru sprint)
    - Taste actiuni (TAB, ESC, SPACE, CTRL)
    """

    def __init__(self):
        """Initializeaza dispozitivul tastatura virtual."""

        self.kb = KeyboardController()

    def run(self):
        """Executa suita completa de teste in ordine.

        Se asteapta 5 secunde pentru a permite focus pe aplicatia tinta
        inainte de a incepe testele.
        """

        # Acorda timp pentru a muta focusul in aplicatia tinta inainte de test
        print("Ai 5 secunde sa dai focus pe aplicatia tinta...")
        time.sleep(5)

        # Ruleaza seturile de teste in ordine: miscare, sprint si actiuni
        print("KEYBOARD TEST STARTED...")

        self.test_movement()
        self.test_sprint()
        self.test_actions()

        print("KEYBOARD TEST COMPLETED!")

    def test_movement(self):
        """Verifica apasarea prelungita pe WASD.

        Testeaza fiecare directie timp de 3 secunde.
        """

        print("TEST WASD HOLD MOVEMENT...")

        print("MOVE FORWARD (W)...")
        self._hold_key("W", duration=3)

        print("MOVE LEFT (A)...")
        self._hold_key("A", duration=3)

        print("MOVE BACKWARD (S)...")
        self._hold_key("S", duration=3)

        print("MOVE RIGHT (D)...")
        self._hold_key("D", duration=3)

    def _hold_key(self, key, duration=3):
        """Helper: apasa tasta, mentine-o activata si apoi o elibereaza.

        Args:
            key: nume tasta (ex: 'W', 'A')
            duration: timp mentinere in secunde
        """

        self.kb.hold(key)
        time.sleep(duration)
        self.kb.release(key)

    def test_sprint(self):
        """Simuleaza combinatia de taste pentru sprint: W tinut + ALT activat.

        Testul:
        1. Apasa si tine W (forward)
        2. Apasa ALT (modifier pentru sprint)
        3. Asteapta 3 secunde
        4. Elibereaza W
        """

        print("TEST SPRINT (W + ALT)...")

        print("HOLD W...")
        self.kb.hold("W")
        time.sleep(0.5)

        print("PRESS ALT...")
        self.kb.press("ALT")

        time.sleep(3)

        self.kb.release("W")

    def test_actions(self):
        """Verifica tastele de actiune folosite frecvent in jocuri.

        Testeaza:
        - TAB (inventar)
        - ESC (meniu/cancel)
        - SPACE (jump/interact)
        - CTRL (crouch/sneak)
        """

        print("TEST ACTION KEYS...")

        print("PRESS TAB (inventar)...")
        self.kb.press("TAB")
        time.sleep(0.5)

        print("PRESS ESC (meniu)...")
        self.kb.press("ESC")
        time.sleep(0.5)

        print("PRESS SPACE (jump)...")
        self.kb.press("SPACE")
        time.sleep(1)

        print("PRESS CTRL (crouch)...")
        self.kb.press("CTRL")
        time.sleep(1)

        print("PRESS CTRL (uncrouch)...")
        self.kb.press("CTRL")
        time.sleep(1)


if __name__ == "__main__":
    KeyboardTest().run()
