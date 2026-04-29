from app.controller import MouseController, KeyboardController
from app.camera import Webcam
from app.core import GestureEngine

from tests import MouseTest, KeyboardTest


class GesturebornApp:
    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()

        self.camera = Webcam()

        self.engine = GestureEngine(self.mouse, self.keyboard, self.camera)

        self.camera.engine = self.engine

    # Modul principal: porneste aplicatia cu camera si controlul gesturilor
    def run_app(self):
        print("Starting Gestureborn camera...")
        self.camera.run()

    # Modul de testare: ruleaza verificarile locale pentru mouse si tastatura
    def run_tests(self):
        mouse_test = MouseTest()
        mouse_test.run()

        keyboard_test = KeyboardTest()
        keyboard_test.run()


# Punct de intrare al aplicatiei
if __name__ == "__main__":
    app = GesturebornApp()

    MODE = "app"  # "app" sau "test"

    if MODE == "app":
        app.run_app()

    elif MODE == "test":
        app.run_tests()
