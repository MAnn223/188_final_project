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
    "Thumb_Up":    b"SPEED_UP\n",
    "Thumb_Down":  b"SPEED_DOWN\n",
    "Victory":     b"SET_50\n", # half open
    "ILoveYou":    b"LOCK\n", # lock
}

def main():
    ser      = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1) # Open serial connection to ESP32
    last_gesture = None
    locked = False

    def esp32_callback(gesture):
        nonlocal last_gesture, locked

        if gesture != last_gesture:
            if gesture == "ILoveYou":
                locked = not locked
                print("LOCKED" if locked else "UNLOCKED")
                ser.write(b"STOP\n")

            elif not locked:
                cmd = GESTURE_COMMANDS.get(gesture, b"STOP\n")
                ser.write(cmd)
            
            elif locked:
                print("Ignored gesture (locked):", gesture)

            last_gesture = gesture

    gesture_recognizer(esp32_callback)

    print("Running. q to quit.")

    

if __name__ == "__main__":
    main()