SET UP AND RUNNING:
Set up a new venv (I used conda) and activate.
Use Python3.10 for compatibility.

In terminal:
Run conda install opencv
Run python -m pip install mediapipe==0.10.9 inside the venv (specify version for compatibility).
Run the python file. (make sure to enable camera access for vscode).



Download HandGestureClassifier bundle from https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer/index#models into your local directory. 

Download hand landmark detection model from https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/index#models into your local directory.