# Gesture-Controlled Box

Control a servo motor to open and close a box using hand gestures detected via webcam.

---

## How It Works

1. **`gesture_recognition.py`** — Captures webcam frames, runs MediaPipe's GestureRecognizer and HandLandmarker in live-stream mode, draws hand landmarks on screen, and fires a callback with the detected gesture name.
2. **`gesture_motor_control.py`** — Receives gesture callbacks, maps them to serial commands, and sends those commands to the ESP32 over UART. Includes a lock/unlock mechanism: `Thumb_Down` locks (blocks further commands), `Thumb_Up` unlocks.
3. **`main.cpp`** (ESP32 / ESP-IDF) — Reads UART commands, drives a servo via LEDC PWM, and updates an SSD1306 OLED over I2C with face or lock animations.

---

## Gesture → Command Mapping

| Gesture      | Serial Command | ESP32 Action                                      |
|--------------|----------------|---------------------------------------------------|
| Open Palm    | `OPEN`         | Servo → 120° (opens box), sad face on OLED       |
| Closed Fist  | `CLOSE`        | Servo → 0° (closes box), neutral face on OLED    |
| Thumb Up     | `UNLOCK`       | OLED shows unlocked icon — other gestures enabled |
| Thumb Down   | `LOCK`         | OLED shows locked icon — other gestures ignored   |

Commands are only sent when the gesture **changes**. While locked (Thumb Down), all gestures except Thumb Up are ignored.

---

## Hardware

- ESP32 (connected via USB serial)
- Servo motor on GPIO 25
- SSD1306 128×64 OLED on I2C: SDA → GPIO 33, SCL → GPIO 32
- Webcam connected to host machine

---

## Software Requirements

### Python (Host Machine)

Use **Python 3.10** for MediaPipe compatibility.

```bash
# Create and activate a conda environment
conda create -n gesture python=3.10
conda activate gesture

# Install dependencies
conda install opencv
pip install mediapipe==0.10.9
pip install pyserial
```

> **Note:** Specify `mediapipe==0.10.9` — other versions may be incompatible with Python 3.10.

### MediaPipe Models

Download both model files and place them in your local project directory:

- **Gesture Recognizer** — [`gesture_recognizer.task`](https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer/index#models)
- **Hand Landmarker** — [`hand_landmarker.task`](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/index#models)

Then update the paths in `gesture_recognition.py`:

```python
gesture_model = "/path/to/gesture_recognizer.task"
hand_model    = "/path/to/hand_landmarker.task"
```

### ESP32 Firmware

Built with **ESP-IDF**. No extra components required — uses standard IDF drivers:
- `driver/ledc` (PWM for servo)
- `driver/uart` (serial communication)
- `driver/i2c` (OLED)

---

## Configuration

In `gesture_motor_control.py`, set your ESP32's serial port:

```python
ESP32_PORT = '/dev/tty.usbserial-0001'  # macOS — adjust for your system
BAUD_RATE  = 115200
```

On Linux this is typically `/dev/ttyUSB0`; on Windows `COM3` (or similar).

---

## Running

1. Flash `main.cpp` to the ESP32 via ESP-IDF (`idf.py build flash`).
2. Connect the ESP32 via USB.
3. Activate your Python environment and run:

```bash
python gesture_motor_control.py
```

4. A camera window will open showing the live feed with hand landmarks and the detected gesture overlaid.
5. Press **`q`** in the camera window to quit.

> **macOS:** Make sure VS Code (or your terminal) has camera access granted in System Settings → Privacy & Security → Camera.
