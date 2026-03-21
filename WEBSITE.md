### Summary
We implemented a touchless control system that uses computer vision to recognize hand gestures and translate them into motor commands for opening and closing a box. Real-time gesture detection feeds into the ESP2, which executes precise servo control and triggers a visual emotion-based component through an OLED display. The system includes a lock/unlock mechanism to prevent unintended actions and improve reliability. This project was designed as a proof-of-concept, but can be extended to potential applications in accessible and hands-free control systems.

### Success Criteria
We defined our success criteria as the following:
1. Reliable recognition of hand gestures through the webcam
2. Gestures are mapped accurately to motor control signals
3. Motor control signals match physical motor actions
4. Emotional display on OLED matches motor action / lock
5. Lock successfully blocks gesture recognition until unlock gesture is detected

### Physical Components
- OLED
- ESP 32 microcontroller
- MCG995 motor
- 3d printed box
- Breadboard
- Arduino 

### Circuitry and CAD Design
In order to control the servo and OLED display, the correct communication pins must be connected between the ESP32 and the components.  Here is a wiring diagram of our setup using the arduino as a 5V power source.

![Image](https://github.com/user-attachments/assets/2b4b5b56-b631-45b3-b0fc-29dfc5ba284a)

These components are then mounted to the box seen below. Once the code is uploaded to the ESP32, gesture control of the box is enabled.

[![3D Model Preview](https://github.com/user-attachments/assets/7185eb25-9927-4595-94e1-c4d2132ea210)](Box.stl)

**Clicking the above image takes you to a 3D view of the model.**



### Demo
https://github.com/user-attachments/assets/3b3c72be-1814-4733-acac-004b1152ce3d

### Results
Each gesture was tested over 10 consecutive trials under normal lighting conditions. The correct servo response and OLED update were achieved in all 10 trials for every gesture. The lock/unlock mechanism functioned correctly in all trials, reliably blocking commands when locked and restoring control on Thumb Up.

### Future
Future iterations can be further optimized in both design and implementation.  Having a lower spec motor would take less space and require less strength in the parallel arms and connection points.  Additionally if we were to use a raspi the camera could be built in and no external power source for the servo would be required.  Other expansions to our project could include additional sensors and functionality such as ultrasonic sensors/ IR sensors and motors for movement.  With these capabilities additional functionality could be implemented such as mapping desired locations or even motion tracking and attempting to catch items within the box.

We hope to also explore applications like integrating the prototype with a waste disposal system for use in hospitals or industrial kitchens, or explore how the touchless aspect of a smart trash can system could help improve the quality of life for people with limited motor control. Another application is a smart lockbox, perhaps with added security features using the computer vision module so that only the owner is able to unlock the box. 

