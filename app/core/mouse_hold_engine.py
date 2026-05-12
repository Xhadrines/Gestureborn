"""Engine pentru control click mouse cu deget ridicat.

Detecteaza gestul degetului aratator ridicat pe ambele maini
si genereaza eveniemente de click hold/release pentru mouse.

Mapare:
- Mana stanga cu deget sus -> right click hold/release
- Mana dreapta cu deget sus -> left click hold/release
"""

from ..vision import HandGestureDetector


class MouseHoldEngine:
    """Procesor pentru apasari prelungite de mouse.

    Monitorizeaza starea degetului aratator pe fiecare mana
    si declanseaza/elibereaza apasarile corespunzatoare.
    """

    def __init__(self, mouse):
        """Initializeaza engine-ul cu controller mouse si detectorul de geste.

        Args:
            mouse: MouseController pentru comenzi mouse
        """

        self.mouse = mouse
        self.detector = HandGestureDetector()

        # Stare hold pentru fiecare mana
        self.left_held = False
        self.right_held = False

    def _update_hold_state(self, current, target, hold_fn, release_fn):
        """Actualizeaza starea apasarii in functie de gestul detectat.

        Emite hold cand trece din 0->1, emite release cand trece din 1->0.

        Args:
            current: stare anterioara (True/False)
            target: starea tinta detectata acum (True/False)
            hold_fn: functie apel pentru a apasa butonul (hold)
            release_fn: functie apel pentru a elibera butonul (release)

        Returns:
            bool: noua stare a apasarii
        """

        # Tranzitie 0->1: emite hold
        if target and not current:
            hold_fn()
            return True

        # Tranzitie 1->0: emite release
        if not target and current:
            release_fn()
            return False

        # Stare stabila: nu se schimba nimic
        return current

    def process_left(self, landmarks):
        """Proceseaza landmark-urile mainii stangi.

        Detecteaza deget aratator ridicat si controleaza right click.
        Mapare inversa: mana stanga -> right click (pentru cross-hand control).

        Args:
            landmarks: lista de 21 landmark-uri din MediaPipe
        """

        # Detecteaza deget aratator ridicat
        target = self.detector.is_index_finger_up(landmarks)

        # Actualizeaza stare hold cu mapare inversa
        self.left_held = self._update_hold_state(
            self.left_held,
            target,
            self.mouse.right_click_hold,  # hold action
            self.mouse.right_click_release,  # release action
        )

    def process_right(self, landmarks):
        """Proceseaza landmark-urile mainii drepte.

        Detecteaza deget aratator ridicat si controleaza left click.
        Mapare inversa: mana dreapta -> left click (pentru cross-hand control).

        Args:
            landmarks: lista de 21 landmark-uri din MediaPipe
        """

        # Detecteaza deget aratator ridicat
        target = self.detector.is_index_finger_up(landmarks)

        # Actualizeaza stare hold cu mapare inversa
        self.right_held = self._update_hold_state(
            self.right_held,
            target,
            self.mouse.left_click_hold,  # hold action
            self.mouse.left_click_release,  # release action
        )
