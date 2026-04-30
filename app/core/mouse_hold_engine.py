"""Engine pentru control click mouse cu deget ridicat.

Detecteaza gestul degetului aratator ridicat si genereaza
eveniemente de click hold/release pentru mouse.
"""

from ..vision import HandGestureDetector


class MouseHoldEngine:
    """Procesor pentru apasari prelungite de mouse.

    Monitorizeaza starea degetului aratator pe fiecare mana
    si declanseaza/elibereaza apasarile corespunzatoare.
    """

    def __init__(self, mouse):
        """Initializeaza engine-ul cu controller mouse si detector geste."""
        self.mouse = mouse
        self.detector = HandGestureDetector()
        self.left_held = False
        self.right_held = False

    def _update_hold_state(self, current, target, hold_fn, release_fn):
        """Actualizeaza starea apasarii in functie de gestul detectat.

        Args:
            current: stare anterioara (True/False)
            target: starea tinta detectata acum (True/False)
            hold_fn: functie apel pentru a apasa butonul
            release_fn: functie apel pentru a elibera butonul

        Returns:
            Noua stare a apasarii
        """
        if target and not current:
            hold_fn()
            return True

        if not target and current:
            release_fn()
            return False

        return current

    def process_left(self, landmarks):
        """Proceseaza landmark-urile mainii stangi.

        Detecteaza deget ridicat si controleaza click dreapta (atribuire inversa).
        """
        target = self.detector.is_index_finger_up(landmarks)
        self.left_held = self._update_hold_state(
            self.left_held,
            target,
            self.mouse.right_click_hold,
            self.mouse.right_click_release,
        )

    def process_right(self, landmarks):
        """Proceseaza landmark-urile mainii drepte.

        Detecteaza deget ridicat si controleaza click stanga (atribuire inversa).
        """
        target = self.detector.is_index_finger_up(landmarks)
        self.right_held = self._update_hold_state(
            self.right_held,
            target,
            self.mouse.left_click_hold,
            self.mouse.left_click_release,
        )
