"""Mapare configuri pentru control mouse.

Defineaza parametri de viteza si alte constante pentru engine-ul mouse.
"""


class MouseMapper:
    """Configuratie constante mouse mapper.

    Contine parametri de control pentru miscarea si viteza mouse-ului.
    """

    # Viteza fixa (fallback cand viteza dinamica este dezactivata)
    SPEED = 25

    # Activeaza viteza dinamica in functie de distanta fata de deadzone
    DYNAMIC_SPEED = True

    # Limite viteza dinamica
    MIN_SPEED = 5
    MAX_SPEED = 500

    # Curba de raspuns: >1 = mai fina aproape de centru, mai rapida spre margine
    SPEED_CURVE = 1.5
