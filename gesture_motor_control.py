import serial
import time
from gesture_recognition import gesture_recognizer

ESP32_PORT = '/dev/tty.usbserial-0001'
BAUD_RATE  = 115200

COLOURS = {
    "OPEN":   (0, 200, 0),
    "CLOSED": (0, 0, 220),
    "OTHER":  (0, 165, 255),
    None:     (180, 180, 180),
}

GESTURE_COMMANDS = {
    "Open_Palm":   b"OPEN\n",
    "Closed_Fist": b"CLOSE\n",
    "Pointing_Up": b"STOP\n",
    "Thumb_Up":    b"UNLOCK\n",
    "Thumb_Down":  b"LOCK\n",
    "Victory":     b"SET_50\n", # half open
    "ILoveYou":    b"SPEED_UP\n", 
}

def main():
    ser = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1)
    last_gesture = None

    def esp32_callback(gesture):
        nonlocal last_gesture
        if gesture != last_gesture:
            cmd = GESTURE_COMMANDS.get(gesture)
            if cmd:
                print(f"Sending: {cmd.strip()}")
                ser.write(cmd)
            last_gesture = gesture

    print("Running. Press q in the camera window to quit.")
    gesture_recognizer(esp32_callback)

    

if __name__ == "__main__":
    main()