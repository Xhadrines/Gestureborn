from app.controller.mouse import MouseController
import time


class MouseTest:
    def __init__(self):
        self.mouse = MouseController()

    def run(self):
        print("Ai 5 secunde sa dai focus pe Skyrim...")
        time.sleep(5)

        print("MOUSE TEST STARTED...")

        self.move_test()
        self.click_short_test()
        self.click_long_test()
        self.click_hold_test()

        print("MOUSE TEST COMPLETED!")

    def move_test(self):
        print("MOVE RIGHT...")
        self._hold_move(self.mouse.move_right)

        print("MOVE LEFT...")
        self._hold_move(self.mouse.move_left)

        print("MOVE UP...")
        self._hold_move(self.mouse.move_up)

        print("MOVE DOWN...")
        self._hold_move(self.mouse.move_down)

    def _hold_move(self, func):
        start = time.time()
        while time.time() - start < 3:
            func(6)
            time.sleep(0.01)

    def click_short_test(self):
        print("RIGHT CLICK SHORT...")
        self.mouse.right_click_short()
        time.sleep(1)

        print("LEFT CLICK SHORT...")
        self.mouse.left_click_short()
        time.sleep(1)

    def click_long_test(self):
        print("RIGHT CLICK LONG...")
        self.mouse.right_click_long()
        time.sleep(1.5)

        print("LEFT CLICK LONG...")
        self.mouse.left_click_long()
        time.sleep(1.5)

    def click_hold_test(self):
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
