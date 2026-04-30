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
        if not landmarks or len(landmarks) < 21:
            return False

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

    def is_open_palm(self, landmarks):
        """Verifica daca mana este deschisa complet.

        Toate cele patru degete principale trebuie sa fie ridicate.
        Returns: True daca palma este deschisa
        """
        if not landmarks or len(landmarks) < 21:
            return False

        index_up = landmarks[8].y < landmarks[6].y
        middle_up = landmarks[12].y < landmarks[10].y
        ring_up = landmarks[16].y < landmarks[14].y
        pinky_up = landmarks[20].y < landmarks[18].y

        return index_up and middle_up and ring_up and pinky_up

    def is_pinch(self, landmarks, hand_side=None):
        """Verifica gestul cu aratator + deget mare intinse.

        Conditii: aratatorul este ridicat, degetul mare este intins pe axa X,
        iar mijlociul, inelarul si degetul mic sunt pliate.
        Pentru mana stanga, degetul mare trebuie sa avanseze spre +X.
        Pentru mana dreapta, degetul mare trebuie sa avanseze spre -X.
        """
        if not landmarks or len(landmarks) < 21:
            return False

        thumb_tip = landmarks[4]
        thumb_mcp = landmarks[2]

        index_up = landmarks[8].y < landmarks[6].y

        middle_folded = landmarks[12].y > landmarks[10].y
        ring_folded = landmarks[16].y > landmarks[14].y
        pinky_folded = landmarks[20].y > landmarks[18].y

        hand_scale = math.sqrt(
            (landmarks[9].x - landmarks[0].x) ** 2
            + (landmarks[9].y - landmarks[0].y) ** 2
        )

        if hand_scale <= 0:
            return False

        thumb_dx = thumb_tip.x - thumb_mcp.x
        thumb_dy = abs(thumb_tip.y - thumb_mcp.y)
        thumb_extended = (
            abs(thumb_dx) > hand_scale * 0.18 and abs(thumb_dx) > thumb_dy
        )

        if hand_side == "left":
            thumb_direction_ok = thumb_dx > hand_scale * 0.08
        elif hand_side == "right":
            thumb_direction_ok = thumb_dx < -(hand_scale * 0.08)
        else:
            thumb_direction_ok = True

        return (
            index_up
            and middle_folded
            and ring_folded
            and pinky_folded
            and thumb_extended
            and thumb_direction_ok
        )

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
