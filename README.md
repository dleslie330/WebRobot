# WebRobot
Our Microcontrollers project where we are building and programming a robot to be controlled over a wifi connection

## Steps to operate
* Install dependencies from `requirements.txt`. **Note: cv2 module needed to have webcam.**
* Run `server_main.py`, and choose to create a server with a webcam (I used a Logitech HD1080p webcam), or not. **Note: if a webcam is chosen, be sure to have it plugged into the computer running as server.**
* After the server started, copy the IP and Port# displayed in the console. Put these as the attributes for `network_\server_cred.py`. 
* Setup a hotspot on the server machine, and get the wifi credentials SSID and PASSWORD and put these as the attributes for `network_\wifi.py`. 
* Copy `main.py`, `network_`, and `robot_functions` onboard the Pico. **Note: please see the correct way to build the PicoBot, since `robot_functions\functions.py` relies on the particular circuit.**
* Plug the PicoBot in via micro USB, and short out pins 0 and 1 to launch the IRQ. The PicoBot's onboard LED should start to flash. After the LED has become solid green, the PicoBot is good to go and should have already connected to the server.
* In your web browser, visit XXX.XXX.XXX.XXX:#### (IP:PORT), and control the robot.

### Tips
* FORWARD : moves bot forward
* RIGHT : turns the bot right
* BACK : moves the bot backward
* LEFT : turns the bot left
* DISCONNECT : disconnects you from server, and allows the next player to play
* QUIT : shuts the bot off
##

## Todo:
    Poster
        - explain project
        - explain solutions
        - cool pictures of robot
            -I grabbed one image of the robot so far. 
        - some circuit diagrams?
        - some very simple flow charts for code?
##

<!-- What is here:

    Outline of code that works with Dakota's D-O bot from lab 14

    Use README.md to share resources, track progress, break up tasks, and
    up-date the group

TO-DO:

    learn how to wifi with the Pico
        - network package
        - socket package
            - UDP socket

    code basic wifi functionality to see what data is like and how we want to
    interface with robot controlls

    build code for computer wifi interface with bot
        - socket for python
            - UDP socket
        - send data on arrow-key? Do we want WASD?
        - when to send:
            - nothing pressed (stop)
            - forward pressed (go forward)
            - backward pressed (go backward)
            - right pressed (go right)
            - left pressed (go left)
            - make them continual send, so bot keeps moving until change in instruction

    get the robot moving from controls sent over wifi
        - demo and record

    Poster
        - explain project
        - explain solutions
        - cool pictures of robot
            -I grabbed one image of the robot so far. 
        - some circuit diagrams?
        - some very simple flow charts for code? -->
