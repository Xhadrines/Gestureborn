"""Mapare geste manuale la taste tastatura.

Defineaza cum directiile mainilor sunt mapate la comenzi tastatura.
"""


class KeyboardMapper:
    """Configuratie mapari geste -> taste tastatura.

    Separa comenzile de miscare (mana stanga) de comenzile de actiune (mana dreapta).
    """

    # Mana stanga: directii mapate la taste WASD pentru miscare
    LEFT_MAP = {"up": "W", "down": "S", "left": "A", "right": "D"}

    # Mana dreapta: directii mapate la taste modificator pentru actiuni
    RIGHT_MAP = {"up": "SPACE", "down": "CTRL", "left": "ALT", "right": "SHIFT"}

    # Palma deschisa pe mana stanga
    LEFT_OPEN_PRESS = "R"

    # Palma deschisa pe mana dreapta
    RIGHT_OPEN_HOLD = "E"

    # Palma deschisa simultan pe ambele maini
    BOTH_OPEN_PRESS = "F"

    # Pinch pe mana stanga
    LEFT_PINCH_PRESS = "TAB"

    # Pinch pe mana dreapta
    RIGHT_PINCH_PRESS = "Q"

    # Pinch simultan pe ambele maini
    BOTH_PINCH_PRESS = "ESC"
