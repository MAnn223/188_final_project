import cv2
import mediapipe as mp
import time
from mediapipe.framework.formats import landmark_pb2


""" Code attributions: 
    https://lotalutfunnahar.medium.com/hand-recognition-with-python-guide-with-code-samples-a0b17f4cd813 -> basic_camera_hand_recognition()
    https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer/index#models
    https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer/python#live-stream """

latest_landmarks = None
latest_gesture = None

def hand_callback(result, output_image, timestamp_ms):
    global latest_landmarks
    latest_landmarks = result.hand_landmarks

# result listener called after each video frame processes -- detection result and input img as parameters
def print_result(result, output_image: mp.Image, timestamp_ms: int):
    global latest_gesture
    #print('gesture recognition result: {}'.format(result))
    if result.gestures:
        latest_gesture = result.gestures[0][0].category_name
        print("Gesture:", latest_gesture)

def gesture_recognizer(gesture_callback = None):
    """ Uses GestureRecognizer from MediaPipe """
    gesture_model = "/Users/nikitasenthil/Documents/Nikita/College/CS188/Final/gesture_recognizer.task"
    hand_model = "/Users/nikitasenthil/Documents/Nikita/College/CS188/Final/hand_landmarker.task"
    BaseOptions = mp.tasks.BaseOptions
    VisionRunningMode = mp.tasks.vision.RunningMode
    GestureRecognizer = mp.tasks.vision.GestureRecognizer
    GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
    GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
    HandLandmarker = mp.tasks.vision.HandLandmarker
    HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    options = GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path=gesture_model),
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=print_result
    )

    hand_options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=hand_model),
        running_mode=VisionRunningMode.LIVE_STREAM,
        num_hands=2,
        result_callback=hand_callback
    )
 
    # hand and gesture recognizers initialized
    with GestureRecognizer.create_from_options(options) as recognizer, HandLandmarker.create_from_options(hand_options) as hand_detector: 
        cap = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)

        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            # convert OpenCV frame to MediaPipe image object (incl conversion BGR to RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

            # Send live image data to perform gesture recognition.
            # The results are accessible via the `result_callback` provided in
            # the `GestureRecognizerOptions` object.
            frame_timestamp_ms = int(time.time() * 1000)
            recognizer.recognize_async(mp_image, frame_timestamp_ms)
            
            hand_detector.detect_async(mp_image, frame_timestamp_ms)
            if latest_landmarks:
                for landmarks in latest_landmarks:
                    landmark_proto = landmark_pb2.NormalizedLandmarkList()

                    landmark_proto.landmark.extend([
                        landmark_pb2.NormalizedLandmark(
                            x=l.x,
                            y=l.y,
                            z=l.z
                        )
                        for l in landmarks
                    ])

                    mp_drawing.draw_landmarks(
                        frame,
                        landmark_proto,
                        mp_hands.HAND_CONNECTIONS
                    )

            # Overlay detected gesture
            cv2.putText(
                frame,
                f"Gesture: {latest_gesture}",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            if gesture_callback and latest_gesture:
                gesture_callback(latest_gesture)

            cv2.imshow("Gesture Recognition", frame)

            # Exit when 'q' is pressed
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        # Release the video capture object and close the OpenCV windows
        cap.release()
        cv2.destroyAllWindows()

        pass


def main():
    #basic_camera_hand_recognition()
    gesture_recognizer()


if __name__ == "__main__":
    main()