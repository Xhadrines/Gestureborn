"""Componenta camera: captura video si detectie gesture pe baza frame-urilor.

Gestioneaza conectarea la camera, rularea modelelor de detectie MediaPipe
(maini si fata) si actualizarea starilor zonelor de control.
"""

import math

import cv2 as cv

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class Webcam:
    """Gestionar camera si detectie gesture video.

    Capturea frame-urile de la camera, ruleaza modele MediaPipe pentru
    detectia mainilor si fetei, si contine zona de control cu cercuri
    de detectie si deadzone-uri. Coordoneaza cu GestureEngine pentru
    a genera comenzi in timp real.
    """

    def __init__(self, camera_id=0, engine=None):
        """Initializeaza camera, modele si zone de control.

        Args:
            camera_id: indexul device camera (implicit: 0 = prima camera)
            engine: instanta GestureEngine pentru procesarea gesturilor
        """
        self.engine = engine
        self.should_close = False

        self.cap = cv.VideoCapture(camera_id)

        # Setari camera: rezolutie fixa si format MJPG pentru stabilitate
        self.cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv.CAP_PROP_FPS, 30)

        # Initializare model: detectie maini pentru coordonarea gesturilor
        hand_base_options = python.BaseOptions(
            model_asset_path="app/models/hand_landmarker.task"
        )

        hand_options = vision.HandLandmarkerOptions(
            base_options=hand_base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
        )

        self.hand_detector = vision.HandLandmarker.create_from_options(hand_options)

        # Initializare model: detectie fata pentru pozitia capului
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

        # Zone de detectie: centre fixe si raze pentru fiecare regiune
        self.head_circle = {"center": (640, 300), "radius": 200}
        self.left_hand_circle = {"center": (200, 500), "radius": 280}
        self.right_hand_circle = {"center": (1080, 500), "radius": 280}

        # Deadzone: zona neutra in care nu se declanseaza actiuni
        self.head_deadzone = {"center": (640, 300), "radius": 25}
        self.left_hand_deadzone = {"center": (200, 500), "radius": 50}
        self.right_hand_deadzone = {"center": (1080, 500), "radius": 50}

        # Stare cercuri: indica daca landmark-urile sunt in zonele active
        self.head_in_circle = False
        self.left_hand_in_circle = False
        self.right_hand_in_circle = False

        # Stare deadzone: marcheaza pozitionarea in zona neutra
        self.head_in_deadzone = False
        self.left_hand_in_deadzone = False
        self.right_hand_in_deadzone = False

    def point_in_circle(self, point, circle):
        """Verifica daca un punct se afla in interiorul unui cerc.

        Args:
            point: tupla (x, y) in coordonate pixel
            circle: dict continand 'center' (x, y) si 'radius'

        Returneaza:
            bool: True daca punctul este in interiorul cercului
        """
        x, y = point
        center_x, center_y = circle["center"]
        radius = circle["radius"]

        distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
        return distance <= radius

    def point_in_deadzone(self, point, deadzone):
        """Verifica daca un punct este in deadzone (zona neutrala).

        Returneaza True daca punctul este in zona neutrala.
        """

        return self.point_in_circle(point, deadzone)

    def get_position_offset(self, point, circle):
        """Calculeaza offsetul fata de centrul cercului (pentru vizualizare axe).

        Returneaza (offset_x, offset_y) in pixeli.
        """
        x, y = point
        center_x, center_y = circle["center"]
        offset_x = x - center_x
        offset_y = y - center_y
        return (offset_x, offset_y)

    def get_landmark_center(self, landmarks):
        """Calculeaza punctul central pentru un set de landmarks.

        Primeste lista de landmarks (coordonate normalizate) si
        returneaza coordonate in pixeli raportate la rezolutia frame-ului.
        """
        if not landmarks:
            return None

        total_x = 0
        total_y = 0

        for lm in landmarks:
            total_x += lm.x
            total_y += lm.y

        avg_x = total_x / len(landmarks)
        avg_y = total_y / len(landmarks)

        # Converteste coordonatele normalizate in pixeli folosind dimensiunea frame-ului
        pixel_x = int(avg_x * 1280)
        pixel_y = int(avg_y * 720)

        return (pixel_x, pixel_y)

    def split_hands(self, hand_landmarks):
        """Atribuie mainile pe baza pozitiei pe ecran, nu a ordinii de detectie.

        MediaPipe nu garanteaza ordinea listei de maini, asa ca folosim centrul
        fiecarei maini pentru a decide care este in zona stanga si care in zona
        dreapta a cadrului.
        """

        left_hand = None
        left_center = None
        right_hand = None
        right_center = None

        if not hand_landmarks:
            return left_hand, left_center, right_hand, right_center

        hands_by_x = []

        for hand in hand_landmarks:
            center = self.get_landmark_center(hand)
            if center:
                hands_by_x.append((center[0], center, hand))

        if not hands_by_x:
            return left_hand, left_center, right_hand, right_center

        hands_by_x.sort(key=lambda item: item[0])

        if len(hands_by_x) == 1:
            _, center, hand = hands_by_x[0]
            if center[0] < 640:
                left_hand, left_center = hand, center
            else:
                right_hand, right_center = hand, center
            return left_hand, left_center, right_hand, right_center

        _, left_center, left_hand = hands_by_x[0]
        _, right_center, right_hand = hands_by_x[-1]

        return left_hand, left_center, right_hand, right_center

    def draw_circles(self, frame):
        """Deseneaza cercurile de detectie, axele si deadzone pe frame.

        Args:
            frame: frame video BGR
        """

        # Culoare cerc cap: galben=deadzone, rosu=detectie, altfel=normal
        if self.head_in_deadzone:
            color_head = (0, 255, 255)
        elif self.head_in_circle:
            color_head = (0, 0, 255)
        else:
            color_head = (255, 140, 80)

        # Deseneaza cercul principal pentru cap
        cv.circle(
            frame, self.head_circle["center"], self.head_circle["radius"], color_head, 2
        )

        # Deseneaza axele de referinta pentru cap
        axis_length = self.head_circle["radius"] + 30
        cv.line(
            frame,
            (
                self.head_circle["center"][0] - axis_length,
                self.head_circle["center"][1],
            ),
            (
                self.head_circle["center"][0] + axis_length,
                self.head_circle["center"][1],
            ),
            (200, 200, 200),
            1,
        )
        cv.line(
            frame,
            (
                self.head_circle["center"][0],
                self.head_circle["center"][1] - axis_length,
            ),
            (
                self.head_circle["center"][0],
                self.head_circle["center"][1] + axis_length,
            ),
            (200, 200, 200),
            1,
        )

        # Deseneaza cerc deadzone pentru cap
        cv.circle(
            frame,
            self.head_deadzone["center"],
            self.head_deadzone["radius"],
            (150, 150, 150),
            2,
        )

        # Culoare cerc mana stanga: galben=deadzone, rosu=detectie, altfel=normal
        if self.left_hand_in_deadzone:
            color_left = (0, 255, 255)
        elif self.left_hand_in_circle:
            color_left = (0, 0, 255)
        else:
            color_left = (100, 255, 100)

        cv.circle(
            frame,
            self.left_hand_circle["center"],
            self.left_hand_circle["radius"],
            color_left,
            2,
        )

        # Deseneaza axele de referinta pentru mana stanga
        axis_length = self.left_hand_circle["radius"] + 30
        cv.line(
            frame,
            (
                self.left_hand_circle["center"][0] - axis_length,
                self.left_hand_circle["center"][1],
            ),
            (
                self.left_hand_circle["center"][0] + axis_length,
                self.left_hand_circle["center"][1],
            ),
            (200, 200, 200),
            1,
        )
        cv.line(
            frame,
            (
                self.left_hand_circle["center"][0],
                self.left_hand_circle["center"][1] - axis_length,
            ),
            (
                self.left_hand_circle["center"][0],
                self.left_hand_circle["center"][1] + axis_length,
            ),
            (200, 200, 200),
            1,
        )

        # Deseneaza deadzone pentru mana stanga
        cv.circle(
            frame,
            self.left_hand_deadzone["center"],
            self.left_hand_deadzone["radius"],
            (150, 150, 150),
            2,
        )

        # Culoare cerc mana dreapta: galben=deadzone, rosu=detectie, altfel=normal
        if self.right_hand_in_deadzone:
            color_right = (0, 255, 255)
        elif self.right_hand_in_circle:
            color_right = (0, 0, 255)
        else:
            color_right = (100, 255, 100)

        cv.circle(
            frame,
            self.right_hand_circle["center"],
            self.right_hand_circle["radius"],
            color_right,
            2,
        )

        # Deseneaza axele de referinta pentru mana dreapta
        axis_length = self.right_hand_circle["radius"] + 30
        cv.line(
            frame,
            (
                self.right_hand_circle["center"][0] - axis_length,
                self.right_hand_circle["center"][1],
            ),
            (
                self.right_hand_circle["center"][0] + axis_length,
                self.right_hand_circle["center"][1],
            ),
            (200, 200, 200),
            1,
        )
        cv.line(
            frame,
            (
                self.right_hand_circle["center"][0],
                self.right_hand_circle["center"][1] - axis_length,
            ),
            (
                self.right_hand_circle["center"][0],
                self.right_hand_circle["center"][1] + axis_length,
            ),
            (200, 200, 200),
            1,
        )

        # Deseneaza deadzone pentru mana dreapta
        cv.circle(
            frame,
            self.right_hand_deadzone["center"],
            self.right_hand_deadzone["radius"],
            (150, 150, 150),
            2,
        )

        # Informatii debug afisate pe ecran pentru stare si distante
        cv.putText(
            frame,
            f"Left Hand Circle: {self.left_hand_in_circle} | Left Hand DeadZone: {self.left_hand_in_deadzone}",
            (10, 30),
            cv.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv.putText(
            frame,
            f"Right Hand Circle: {self.right_hand_in_circle} | Right Hand DeadZone: {self.right_hand_in_deadzone}",
            (10, 60),
            cv.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        # Afiaseaza separat starea pentru cap
        cv.putText(
            frame,
            f"Head Circle: {self.head_in_circle} | Head DeadZone: {self.head_in_deadzone}",
            (10, 90),
            cv.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

    def are_all_detected_in_circles(self):
        """Verifica daca elementele detectate sunt in zonele cerute.

        Head trebuie detectat si sa se afle in cercul dedicat; mainile raman optionale.
        Returneaza True daca conditiile minime sunt indeplinite.
        """

        if not self.head_in_circle:
            return False

        return True

    def run(self):
        """Ruleaza bucla principala: captura, detectie si procesare gesture.

        Deschide fereastra window, incepe captura video, ruleaza modele
        MediaPipe pe fiecare frame, actualizeaza stari zone si coordoneaza
        cu GestureEngine. Se opreste cand fereastra se inchide sau
        cand se detecteaza Peace sign (exit gesture).
        """
        cv.namedWindow(self.window_name, cv.WINDOW_NORMAL)
        cv.resizeWindow(self.window_name, 1280, 720)

        frame_id = 0

        while True:
            if self.should_close:
                break

            ret, frame = self.cap.read()

            if not ret:
                break

            frame = cv.flip(frame, 1)

            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb,
            )

            # Detectie: ruleaza modele pentru fiecare frame
            hand_result = self.hand_detector.detect_for_video(mp_image, frame_id)

            face_result = self.face_detector.detect_for_video(mp_image, frame_id)

            frame_id += 1

            # Actualizare stari cercuri
            # Se reseteaza starea inainte de evaluare
            self.head_in_circle = False
            self.head_in_deadzone = False
            self.left_hand_in_circle = False
            self.left_hand_in_deadzone = False
            self.right_hand_in_circle = False
            self.right_hand_in_deadzone = False

            if self.engine:
                self.engine.update(hand_result, face_result)

            # Verifica pozitia capului in raport cu cercul si deadzone-ul
            if face_result.face_landmarks and len(face_result.face_landmarks) > 0:
                # Foloseste landmark-ul nasului pentru a evita drift-ul de la media tuturor punctelor faciale
                nose = face_result.face_landmarks[0][1]
                head_center = (int(nose.x * 1280), int(nose.y * 720))
                # Valideaza ca pozitia capului ramane in limitele cadrului
                if (
                    head_center
                    and 0 <= head_center[0] <= 1280
                    and 0 <= head_center[1] <= 720
                ):
                    in_circle = self.point_in_circle(head_center, self.head_circle)
                    in_deadzone = self.point_in_deadzone(
                        head_center, self.head_deadzone
                    )
                    self.head_in_deadzone = in_deadzone
                    # Capul este in cerc doar daca este in zona si nu in deadzone
                    self.head_in_circle = in_circle and not in_deadzone

            # Verifica mainile in raport cu cercul si deadzone-ul
            left_hand, left_center, right_hand, right_center = self.split_hands(
                hand_result.hand_landmarks
            )

            if (
                left_center
                and 0 <= left_center[0] <= 1280
                and 0 <= left_center[1] <= 720
            ):
                in_circle = self.point_in_circle(left_center, self.left_hand_circle)
                in_deadzone = self.point_in_deadzone(
                    left_center, self.left_hand_deadzone
                )
                self.left_hand_in_deadzone = in_deadzone
                # Mana este in cerc doar daca se afla in zona si nu in deadzone
                self.left_hand_in_circle = in_circle and not in_deadzone

            if (
                right_center
                and 0 <= right_center[0] <= 1280
                and 0 <= right_center[1] <= 720
            ):
                in_circle = self.point_in_circle(right_center, self.right_hand_circle)
                in_deadzone = self.point_in_deadzone(
                    right_center, self.right_hand_deadzone
                )
                self.right_hand_in_deadzone = in_deadzone
                # Mana este in cerc doar daca se afla in zona si nu in deadzone
                self.right_hand_in_circle = in_circle and not in_deadzone

            # Deseneaza informatiile pentru maini pe frame
            if hand_result.hand_landmarks:
                for hand, label, circle, deadzone, in_circle, in_deadzone in (
                    (
                        left_hand,
                        "LH",
                        self.left_hand_circle,
                        self.left_hand_deadzone,
                        self.left_hand_in_circle,
                        self.left_hand_in_deadzone,
                    ),
                    (
                        right_hand,
                        "RH",
                        self.right_hand_circle,
                        self.right_hand_deadzone,
                        self.right_hand_in_circle,
                        self.right_hand_in_deadzone,
                    ),
                ):
                    if not hand:
                        continue

                    hand_center = self.get_landmark_center(hand)
                    if not hand_center:
                        continue

                    if in_deadzone:
                        hand_point_color = (0, 255, 255)  # Galben
                    elif in_circle:
                        hand_point_color = (0, 0, 255)  # Rosu
                    else:
                        hand_point_color = (0, 255, 0)  # Verde

                    dist_relevant = math.sqrt(
                        (hand_center[0] - circle["center"][0]) ** 2
                        + (hand_center[1] - circle["center"][1]) ** 2
                    )
                    dist_deadzone = math.sqrt(
                        (hand_center[0] - deadzone["center"][0]) ** 2
                        + (hand_center[1] - deadzone["center"][1]) ** 2
                    )

                    # Deseneaza centrul mainii cu culoarea zonei curente
                    cv.circle(frame, hand_center, 8, hand_point_color, -1)

                    # Afiseaza pozitia mainii si distantele utile
                    cv.putText(
                        frame,
                        f"{label}: ({hand_center[0]}, {hand_center[1]})",
                        (hand_center[0] - 80, hand_center[1] - 30),
                        cv.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        hand_point_color,
                        1,
                    )
                    cv.putText(
                        frame,
                        f"Dist: {int(dist_relevant)}, DZ: {int(dist_deadzone)}",
                        (hand_center[0] - 80, hand_center[1] - 10),
                        cv.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        hand_point_color,
                        1,
                    )

                    # Deseneaza fiecare landmark al mainii
                    for lm in hand:
                        x = int(lm.x * frame.shape[1])
                        y = int(lm.y * frame.shape[0])

                        cv.circle(frame, (x, y), 5, (0, 255, 0), -1)

            # Deseneaza landmark-urile fetei
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

            # Deseneaza zonele de detectie peste imagine

            # Adauga informatii debug pentru cap
            if face_result.face_landmarks:
                nose = face_result.face_landmarks[0][1]

                head_center = (int(nose.x * 1280), int(nose.y * 720))
                if head_center:
                    if self.head_in_deadzone:
                        head_debug_color = (0, 255, 255)
                    elif self.head_in_circle:
                        head_debug_color = (0, 0, 255)
                    else:
                        head_debug_color = (255, 140, 80)

                    cv.circle(frame, head_center, 10, head_debug_color, -1)

                    # Calculeaza distanta fata de cercul capului
                    dist_relevant = math.sqrt(
                        (head_center[0] - self.head_circle["center"][0]) ** 2
                        + (head_center[1] - self.head_circle["center"][1]) ** 2
                    )
                    # Calculeaza distanta fata de deadzone-ul capului
                    dist_deadzone = math.sqrt(
                        (head_center[0] - self.head_deadzone["center"][0]) ** 2
                        + (head_center[1] - self.head_deadzone["center"][1]) ** 2
                    )

                    # Afiseaza pozitia capului si distantele relevante
                    cv.putText(
                        frame,
                        f"Head: ({head_center[0]}, {head_center[1]})",
                        (head_center[0] - 80, head_center[1] - 30),
                        cv.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        head_debug_color,
                        1,
                    )
                    cv.putText(
                        frame,
                        f"Dist: {int(dist_relevant)}, DZ: {int(dist_deadzone)}",
                        (head_center[0] - 40, head_center[1] - 10),
                        cv.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        head_debug_color,
                        1,
                    )

            self.draw_circles(frame)

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

        if self.engine and hasattr(self.engine, "mouse_hold_engine"):
            self.engine.mouse_hold_engine.process_left([])
            self.engine.mouse_hold_engine.process_right([])

        self.cap.release()
        cv.destroyAllWindows()


if __name__ == "__main__":
    Webcam().run()
