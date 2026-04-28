# Gestureborn

Gestureborn este o aplicație dezvoltată în Python care permite controlarea jocului **The Elder Scrolls V: Skyrim** folosind gesturi realizate în fața camerei.

## Cerințe

Pentru a rula aplicația, trebuie să ai instalat:

- Python (v3.14.4 sau o versiune mai mare)
- pip (v26.0.1 sau o versiune mai mare)

## Instalare

### 1. Clonează repository-ul

```bash
git clone https://github.com/Xhadrines/Gestureborn.git
```

### 2. Creează mediul virtual

```bash
python -m venv .venv
```

### 3. Activează mediul virtual

```bash
source ./.venv/bin/activate
```

### 4. Instalează dependențele

```bash
pip install -r requirements.txt
```

### 5. Configurare uinput

Încarcă modulul uinput

```bash
sudo modprobe uinput
lsmod | grep uinput
```

Creează regula udev

```bash
sudo vim /etc/udev/rules.d/99-uinput.rules
```

Adaugă următoarea linie:

```
KERNEL=="uinput", GROUP="khajiit", MODE="0660"
```

_NOTE: Înlocuiește "khajiit" cu grupul utilizatorului tău Linux._

Verificare:

```
sudo cat /etc/udev/rules.d/99-uinput.rules
```

Reîncarcă regulile

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Verifică device-ul

```bash
ls -l /dev/uinput
```

### 6. Descarcă hand model

Intră aici: [Hand landmarks detection guide](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/index#models)  
Descarcă fișierul: `hand_landmarker.task`  
După descărcare, mută fișierul în: `app/models/hand_landmarker.task`

### 7. Descarcă face model

Intră aici: [Face landmark detection guide
](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker)  
Descarcă fișierul: `face_landmarker.task`  
După descărcare, mută fișierul în: `app/models/face_landmarker.task`

### 8. Rulează proiectul

```bash
python main.py
```

**_NOTE: Pentru detalii despre controale și gesturi, vezi [aici](gestureborn-controls.md)_**
