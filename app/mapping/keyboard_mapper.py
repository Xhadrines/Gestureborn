"""Mapare geste manuale la taste tastatura.

Defineaza cum directiile mainilor si combinatiile de degete sunt
mapate la comenzile de tastatura pentru control game/aplicatie.

Structura mapari:
- Mana stanga: directii -> taste miscare (WASD)
- Mana dreapta: directii -> taste modificator (SPACE, CTRL, ALT, SHIFT)
- Geste speciale: open palm, thumb, peace sign, pinky -> taste actiuni
"""


class KeyboardMapper:
    """Configuratie mapari geste -> taste tastatura.

    Centralizeaza definitii mapari pentru:
    - Miscari directionale (WASD)
    - Taste modificator (SPACE, CTRL, ALT, SHIFT)
    - Geste speciale (palm, thumb, peace, pinky)
    """

    # ==============================================
    # MISCARI DIRECTIONALE
    # ==============================================
    # Mana stanga: directii mapate la taste WASD pentru miscare
    LEFT_MAP = {"up": "W", "down": "S", "left": "A", "right": "D"}

    # Mana dreapta: directii mapate la taste modificator pentru actiuni
    RIGHT_MAP = {"up": "SPACE", "down": "CTRL", "left": "ALT", "right": "SHIFT"}

    # ==============================================
    # GESTUL PALM DESCHIS (OPEN PALM)
    # ==============================================
    # Palma deschisa pe mana stanga -> apasa R o singura data
    LEFT_OPEN_PRESS = "R"

    # Palma deschisa pe mana dreapta -> tine E apasata
    RIGHT_OPEN_HOLD = "E"

    # Palma deschisa simultan pe ambele maini -> apasa F o singura data
    BOTH_OPEN_PRESS = "F"

    # ==============================================
    # GESTUL THUMB (DEGET MARE)
    # ==============================================
    # Thumb pe mana stanga -> apasa TAB o singura data
    LEFT_THUMB_PRESS = "TAB"

    # Thumb pe mana dreapta -> apasa Q o singura data
    RIGHT_THUMB_PRESS = "Q"

    # Thumb simultan pe ambele maini -> apasa ESC o singura data
    BOTH_THUMB_PRESS = "ESC"

    # ==============================================
    # GESTUL PEACE SIGN (INDEX + MIDDLE)
    # ==============================================
    # Peace sign pe mana dreapta -> apasa T o singura data
    RIGHT_PEACE_PRESS = "T"

    # ==============================================
    # GESTUL PINKY (DEGET MIC)
    # ==============================================
    # Pinky pe mana stanga -> apasa ENTER o singura data
    LEFT_PINKY_PRESS = "ENTER"

    # Pinky pe mana dreapta -> tine Z apasata
    RIGHT_PINKY_HOLD = "Z"
