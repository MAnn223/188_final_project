### Setup
In order to control the servo and OLED display the correct communication pins must be connected between the ESP32 and the components.  Here is a wiring diagram of our setup using the arduino as a 5V power source.

![Image](https://github.com/user-attachments/assets/2b4b5b56-b631-45b3-b0fc-29dfc5ba284a)

These componenets are then mounted to the box seen below and once the code is uploaded to the ESP32 gesture control of the box is enabled.

[![3D Model Preview](https://github.com/user-attachments/assets/7185eb25-9927-4595-94e1-c4d2132ea210)](Box.stl)
(Clicking this image takes you to a 3D view)

### Results
Each gesture was tested over 10 consecutive trials under normal lighting conditions. The correct servo response and OLED update were achieved in all 10 trials for every gesture. The lock/unlock mechanism functioned correctly in all trials, reliably blocking commands when locked and restoring control on Thumb Up.

### Demo
https://github.com/user-attachments/assets/dc004ea4-160c-4d41-baff-249c0f2abf3d

