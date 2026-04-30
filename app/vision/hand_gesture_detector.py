"""Detector de geste manuale bazat pe landmark-urile degetelor.

Identifica pozitiile degetelor pentru a detecta geste specifice.
"""

import math


class HandGestureDetector:
    """Analizor de geste detectate pe maini.

    Verifica pozitia varfurilor degetelor fata de articulatii
    pentru a determina configura mainii.
    """

    def is_fist(self, landmarks):
        """Verifica daca mana este in pumn.

        Returns: True daca cel putin 3 din 4 degete sunt pliate
        """
        tips = [8, 12, 16, 20]
        pip = [6, 10, 14, 18]
        folded = 0
        for t, p in zip(tips, pip):
            if landmarks[t].y > landmarks[p].y:
                folded += 1
        return folded >= 3

    def is_index_finger_up(self, landmarks):
        """Verifica daca degetul aratator este ridicat.

        Restul degetelor trebuie sa fie pliate.
        Returns: True daca doar aratator este sus
        """
        if not landmarks or len(landmarks) < 21:
            return False

        index_up = landmarks[8].y < landmarks[6].y
        middle_folded = landmarks[12].y > landmarks[10].y
        ring_folded = landmarks[16].y > landmarks[14].y
        pinky_folded = landmarks[20].y > landmarks[18].y

        return index_up and middle_folded and ring_folded and pinky_folded

    def is_peace_sign(self, landmarks):
        """Verifica daca mana face Peace sign (V).

        Aratator si mijloc ridicati, restul pliate.
        Returns: True daca gestura Peace sign este detectata
        """
        if not landmarks or len(landmarks) < 21:
            return False

        index_up = landmarks[8].y < landmarks[6].y
        middle_up = landmarks[12].y < landmarks[10].y
        ring_folded = landmarks[16].y > landmarks[14].y
        pinky_folded = landmarks[20].y > landmarks[18].y

        return index_up and middle_up and ring_folded and pinky_folded

    def get_direction(self, center, circle, deadzone):
        """Determina directia unica a mainii.

        Mapare pozitie mana -> directia preponderenta (o singura directie).
        Returns: "up", "down", "left", "right", "neutral", "outside"
        """
        cx, cy = circle["center"]
        x, y = center
        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < deadzone["radius"]:
            return "neutral"
        if dist > circle["radius"]:
            return "outside"
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        return "down" if dy > 0 else "up"
