import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import serial
import time
from hand_gesture_detector import GestureDetector, _draw_landmarks, classify_gesture, HAND_CONNECTIONS

ESP32_PORT = '/dev/tty.usbserial-0001'
BAUD_RATE  = 115200

COLOURS = {
    "OPEN":   (0, 200, 0),
    "CLOSED": (0, 0, 220),
    "OTHER":  (0, 165, 255),
    None:     (180, 180, 180),
}

def main():
    ser      = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1) # Open serial connection to ESP32
    detector = GestureDetector(camera_index=0) # open webcam and load gesture model
    last_gesture = None

    print("Running. Q to quit.")

    while True:
        ok, frame = detector._cap.read() # read one frame from webcam
        if not ok:
            break

        frame  = cv2.flip(frame, 1) # mirror
        rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # convert to RGB
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb) # wrap in mediapipe Image
        result = detector._detector.detect(mp_img) # run hand landmark detection

        gesture = None
        # classify gesture and draw landmarks if hand detected
        if result.hand_landmarks:
            lms     = result.hand_landmarks[0]
            gesture = classify_gesture(lms)
            _draw_landmarks(frame, lms)

        # draw label
        label  = gesture if gesture else "–"
        colour = COLOURS.get(gesture, (180, 180, 180))
        cv2.putText(frame, f"Gesture: {label}", (20, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, colour, 3)

        cv2.imshow("Gesture -> Servo Control  (Q to quit)", frame)

        # only send command to ESP32 if gesture has changed since last frame
        if gesture != last_gesture:
            if gesture == "OPEN":
                ser.write(b"OPEN\n")
            elif gesture == "CLOSED":
                ser.write(b"CLOSED\n")
            else:
                ser.write(b"STOP\n")
            last_gesture = gesture

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    ser.write(b"STOP\n")
    ser.close()
    detector.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()