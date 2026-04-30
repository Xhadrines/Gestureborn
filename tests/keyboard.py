from app.controller.keyboard import KeyboardController
import time


class KeyboardTest:
    def __init__(self):
        self.kb = KeyboardController()

    def run(self):
        # Acorda timp pentru a muta focusul in aplicatia tinta inainte de test
        print("Ai 5 secunde sa dai focus pe Skyrim...")
        time.sleep(5)

        # Ruleaza seturile de teste in ordine: miscare, sprint si actiuni
        print("KEYBOARD TEST STARTED...")

        self.test_movement()
        self.test_sprint()
        self.test_actions()

        print("KEYBOARD TEST COMPLETED!")

    def test_movement(self):
        # Verifica apasarea prelungita pe WASD
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
        # Apasa tasta, mentine-o activata si apoi o elibereaza
        self.kb.hold(key)
        time.sleep(duration)
        self.kb.release(key)

    def test_sprint(self):
        # Simuleaza combinatia de sprint: W tinut si ALT activat
        print("TEST SPRINT...")

        print("HOLD W...")
        self.kb.hold("W")
        time.sleep(0.5)

        print("PRESS ALT...")
        self.kb.press("ALT")

        time.sleep(3)

        self.kb.release("W")

    def test_actions(self):
        # Verifica tastele de actiune folosite frecvent in joc
        print("TEST ACTION KEYS...")

        print("PRESS TAB...")
        self.kb.press("TAB")
        time.sleep(0.5)

        print("PRESS ESC...")
        self.kb.press("ESC")
        time.sleep(0.5)

        print("PRESS SPACE...")
        self.kb.press("SPACE")
        time.sleep(1)

        print("PRESS CTRL...")
        self.kb.press("CTRL")
        time.sleep(1)

        print("PRESS CTRL...")
        self.kb.press("CTRL")
        time.sleep(1)


if __name__ == "__main__":
    KeyboardTest().run()
