from app.controller import MouseController, KeyboardController
from app.camera import Webcam

from tests import MouseTest, KeyboardTest


class GesturebornApp:
    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.camera = Webcam()

    # -------------------------
    # MODE 1: APP
    # -------------------------
    def run_app(self):
        print("Starting Gestureborn camera...")
        self.camera.run()

    # -------------------------
    # MODE 2: TESTS
    # -------------------------
    def run_tests(self):
        test = MouseTest()
        # test.run()

        test = KeyboardTest()
        # test.run()


# -------------------------
# ENTRY POINT
# -------------------------
if __name__ == "__main__":
    app = GesturebornApp()

    MODE = "app"  # "app" or "test"

    if MODE == "app":
        app.run_app()

    elif MODE == "test":
        app.run_tests()
