"""Modul principal al aplicatiei Gestureborn.

Actoneaza ca punct de intrare pentru:
- Camera/webcam: captarea video si detectia de gesturi
- GestureEngine: procesarea de geste detectate si generare de comenzi
- MouseController si KeyboardController: executie de actiuni pe sistem

Permite lansare in doua moduri:
- 'app': ruleaza aplicatia cu control de gesturi in timp real
- 'test': ruleaza teste de verificare pentru mouse si tastatura
"""

from app.controller import MouseController, KeyboardController
from app.camera import Webcam
from app.core import GestureEngine

from tests import MouseTest, KeyboardTest


class GesturebornApp:
    """Aplicatia principala Gestureborn.

    Coordoneaza initializare controllers, camera si gesture engine.
    Ofera interfata simpla pentru a pornire aplicatia sau teste.
    """

    def __init__(self):
        """Initializeaza toate componentele: controllers, camera si engine."""

        # Initializeaza dispozitivele virtuale pentru mouse si tastatura
        self.mouse = MouseController()
        self.keyboard = KeyboardController()

        # Initializeaza camera pentru captare video si detectia de gesturi
        self.camera = Webcam()

        # Initializeaza engine-ul central care coordoneaza procesarea gesturilor
        self.engine = GestureEngine(self.mouse, self.keyboard, self.camera)

        # Conecteaza engine-ul la camera pentru comunicare bidirectionala
        self.camera.engine = self.engine

    def run_app(self):
        """Porneste aplicatia cu control de gesturi in timp real.

        Lanseaza loop-ul principal de camera care detecteaza geste
        si genereaza comenzi continue pentru mouse si tastatura.
        """

        self.camera.run()

    def run_tests(self):
        """Executa teste de verificare pentru mouse si tastatura.

        Ruleaza suita completa de teste:
        - MouseTest: verifica miscari si click-uri
        - KeyboardTest: verifica apasari de taste si combinatii
        """

        mouse_test = MouseTest()
        mouse_test.run()

        keyboard_test = KeyboardTest()
        keyboard_test.run()


# ==============================================================================
# PUNCT DE INTRARE AL APLICATIEI
# ==============================================================================
if __name__ == "__main__":
    app = GesturebornApp()

    # Selectare mod executie: 'app' pentru aplicatie, 'test' pentru teste
    MODE = "app"  # Optiuni: "app" sau "test"

    if MODE == "app":
        # Lansare aplicatie cu control de gesturi live
        app.run_app()

    elif MODE == "test":
        # Lansare module de teste
        app.run_tests()
