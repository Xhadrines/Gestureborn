"""Componenta de viziune artificiala pentru Gestureborn.

Detectare si analiza landmark-urilor folosind MediaPipe:
- Maini: 21 landmark-uri per mana, folosit pentru detectie geste
- Fata: landmark-uri faciale, nasul folosit pentru control mouse
"""

from .head_direction_detector import HeadDirectionDetector
from .hand_gesture_detector import HandGestureDetector
