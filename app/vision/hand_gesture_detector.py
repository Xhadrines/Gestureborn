"""Detector de geste manuale bazat pe landmark-urile degetelor.

Identifica pozitiile degetelor si verifica relatiile intre
articulatii pentru a detecta geste specifice: fist, peace sign,
open palm, thumb, pinky, index-only.

Landmarking MediaPipe: 21 puncte per mana
- 0: wrist
- 1-4: thumb
- 5-8: index
- 9-12: middle
- 13-16: ring
- 17-20: pinky
"""

import math


class HandGestureDetector:
    """Analizor de geste detectate pe maini.

    Verifica pozitia varfurilor degetelor fata de articulatii
    pentru a determina configuratia mainii si gesturile specifice.
    """

    def is_fist(self, landmarks):
        """Verifica daca mana este in pumn.

        Pumn = cel putin 3 din 4 degete pliate (varf sub articulatia PIP).

        Args:
            landmarks: lista de 21 NormalizedLandmark-uri

        Returns:
            bool: True daca mana este in pozitie pumn
        """

        if not landmarks or len(landmarks) < 21:
            return False

        # Varfuri degete: index, middle, ring, pinky
        tips = [8, 12, 16, 20]
        # Articulatii PIP (Proximal InterPhalangeal)
        pip = [6, 10, 14, 18]

        folded = 0
        for t, p in zip(tips, pip):
            # Deget pliat cand varful este sub articulatia PIP (y > y_pip)
            if landmarks[t].y > landmarks[p].y:
                folded += 1

        return folded >= 3

    def is_index_finger_up(self, landmarks):
        """Verifica daca degetul aratator este ridicat singur.

        Conditii: aratator ridicat (y_tip < y_pip), restul pliate.

        Args:
            landmarks: lista de 21 NormalizedLandmark-uri

        Returns:
            bool: True daca doar aratator este sus
        """

        if not landmarks or len(landmarks) < 21:
            return False

        # Verificare: aratator ridicat
        index_up = landmarks[8].y < landmarks[6].y
        # Verificare: restul degetelor pliate
        middle_folded = landmarks[12].y > landmarks[10].y
        ring_folded = landmarks[16].y > landmarks[14].y
        pinky_folded = landmarks[20].y > landmarks[18].y

        return index_up and middle_folded and ring_folded and pinky_folded

    def is_peace_sign(self, landmarks):
        """Verifica daca mana face Peace sign (V).

        Peace sign = aratator si mijlociu ridicati, restul pliate.

        Args:
            landmarks: lista de 21 NormalizedLandmark-uri

        Returns:
            bool: True daca gestura Peace sign este detectata
        """

        if not landmarks or len(landmarks) < 21:
            return False

        # Verificare: aratator si mijlociu ridicati
        index_up = landmarks[8].y < landmarks[6].y
        middle_up = landmarks[12].y < landmarks[10].y
        # Verificare: restul degetelor pliate
        ring_folded = landmarks[16].y > landmarks[14].y
        pinky_folded = landmarks[20].y > landmarks[18].y

        return index_up and middle_up and ring_folded and pinky_folded

    def is_open_palm(self, landmarks):
        """Verifica daca mana este complet deschisa.

        Open palm = toate patru degete principale ridicate (nu degetul mare).

        Args:
            landmarks: lista de 21 NormalizedLandmark-uri

        Returns:
            bool: True daca palma este deschisa
        """
        if not landmarks or len(landmarks) < 21:
            return False

        # Verificare: toate patru degete ridicate
        index_up = landmarks[8].y < landmarks[6].y
        middle_up = landmarks[12].y < landmarks[10].y
        ring_up = landmarks[16].y < landmarks[14].y
        pinky_up = landmarks[20].y < landmarks[18].y

        return index_up and middle_up and ring_up and pinky_up

    def is_thumb(self, landmarks, hand_side=None):
        """Verifica gestul cu degetul mare intins (thumb only).

        Thumb = degetul mare ridicat si intins pe axa X, restul pliate.
        Directie: stanga -> +X, dreapta -> -X (bazat pe hand_side).

        Args:
            landmarks: lista de 21 NormalizedLandmark-uri
            hand_side: 'left' sau 'right' pentru verificare directie, sau None

        Returns:
            bool: True daca thumb este intins in directia corecta
        """

        if not landmarks or len(landmarks) < 21:
            return False

        thumb_tip = landmarks[4]
        thumb_mcp = landmarks[2]

        # Scala mainii pentru normalizare (distanta wrist-middle PIP)
        hand_scale = math.sqrt(
            (landmarks[9].x - landmarks[0].x) ** 2
            + (landmarks[9].y - landmarks[0].y) ** 2
        )

        if hand_scale <= 0:
            return False

        # Calculeaza deplasare thumb relativ la scale
        thumb_dx = thumb_tip.x - thumb_mcp.x
        thumb_dy = abs(thumb_tip.y - thumb_mcp.y)

        # Thumb intins = deplasare orizontala semnificativa vs verticala
        thumb_extended = abs(thumb_dx) > hand_scale * 0.18 and abs(thumb_dx) > thumb_dy

        # Verifica directie in functie de mana
        if hand_side == "left":
            # Mana stanga: thumb trebuie intins spre +X (dreapta)
            thumb_direction_ok = thumb_dx > hand_scale * 0.08
        elif hand_side == "right":
            # Mana dreapta: thumb trebuie intins spre -X (stanga)
            thumb_direction_ok = thumb_dx < -(hand_scale * 0.08)
        else:
            thumb_direction_ok = True

        return thumb_extended and thumb_direction_ok

    def is_pinky_up(self, landmarks):
        """Verifica daca degetul mic este ridicat singur.

        Pinky up = degetul mic ridicat, restul pliate.

        Args:
            landmarks: lista de 21 NormalizedLandmark-uri

        Returns:
            bool: True daca doar degetul mic este sus
        """

        if not landmarks or len(landmarks) < 21:
            return False

        # Verificare: pinky ridicat
        pinky_up = landmarks[20].y < landmarks[18].y
        # Verificare: restul degetelor pliate
        index_folded = landmarks[8].y > landmarks[6].y
        middle_folded = landmarks[12].y > landmarks[10].y
        ring_folded = landmarks[16].y > landmarks[14].y

        return pinky_up and index_folded and middle_folded and ring_folded

    def get_direction(self, center, circle, deadzone):
        """Determina directia unica a mainii relativ la zona de control.

        Mapare pozitie mana -> directia preponderenta (o singura directie).

        Args:
            center: tupla (x, y) pozitia centrului mainii
            circle: dict cu centrul si raza cercului de detectie
            deadzone: dict cu centrul si raza zonei neutre

        Returns:
            str: directia: "up", "down", "left", "right", "neutral", "outside"
        """

        cx, cy = circle["center"]
        x, y = center
        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx * dx + dy * dy)

        # In deadzone = neutral
        if dist < deadzone["radius"]:
            return "neutral"

        # Afara cercului = outside
        if dist > circle["radius"]:
            return "outside"

        # Determina directie principala (pe care axa e mai mare deplasarea)
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        return "down" if dy > 0 else "up"
