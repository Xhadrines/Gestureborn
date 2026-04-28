import cv2 as cv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class Webcam:
    def __init__(self, camera_id=0):
        self.cap = cv.VideoCapture(camera_id)

        # Camera settings
        self.cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv.CAP_PROP_FPS, 30)

        # -------------------------
        # HAND MODEL
        # -------------------------
        hand_base_options = python.BaseOptions(
            model_asset_path="app/models/hand_landmarker.task"
        )

        hand_options = vision.HandLandmarkerOptions(
            base_options=hand_base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
        )

        self.hand_detector = vision.HandLandmarker.create_from_options(hand_options)

        # -------------------------
        # FACE MODEL
        # -------------------------
        face_base_options = python.BaseOptions(
            model_asset_path="app/models/face_landmarker.task"
        )

        face_options = vision.FaceLandmarkerOptions(
            base_options=face_base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1,
        )

        self.face_detector = vision.FaceLandmarker.create_from_options(face_options)

        self.window_name = "Gestureborn"

    def run(self):
        cv.namedWindow(self.window_name, cv.WINDOW_NORMAL)
        cv.resizeWindow(self.window_name, 1280, 720)

        frame_id = 0

        while True:
            ret, frame = self.cap.read()

            if not ret:
                break

            frame = cv.flip(frame, 1)

            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb,
            )

            # -------------------------
            # DETECTION
            # -------------------------
            hand_result = self.hand_detector.detect_for_video(mp_image, frame_id)

            face_result = self.face_detector.detect_for_video(mp_image, frame_id)

            frame_id += 1

            # -------------------------
            # DRAW HANDS
            # -------------------------
            if hand_result.hand_landmarks:
                for hand in hand_result.hand_landmarks:
                    for lm in hand:
                        x = int(lm.x * frame.shape[1])
                        y = int(lm.y * frame.shape[0])

                        cv.circle(
                            frame,
                            (x, y),
                            5,
                            (0, 255, 0),
                            -1,
                        )

            # -------------------------
            # DRAW FACE
            # -------------------------
            if face_result.face_landmarks:
                for face in face_result.face_landmarks:
                    for lm in face:
                        x = int(lm.x * frame.shape[1])
                        y = int(lm.y * frame.shape[0])

                        cv.circle(
                            frame,
                            (x, y),
                            1,
                            (255, 0, 0),
                            -1,
                        )

            cv.imshow(self.window_name, frame)

            cv.waitKey(1)

            try:
                visible = cv.getWindowProperty(
                    self.window_name,
                    cv.WND_PROP_VISIBLE,
                )

                if visible < 1:
                    break

            except cv.error:
                break

        self.cap.release()
        cv.destroyAllWindows()


if __name__ == "__main__":
    Webcam().run()
