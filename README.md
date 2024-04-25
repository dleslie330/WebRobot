# WebRobot
Our Microcontrollers project where we are building and programming a robot to be controlled over a wifi connection

## Steps to operate
* Turn on your devices hotspot, and store the SSID and Password in `network_\wifi_cred.py`
* Plug the Pico in via the micro-USB, ensuring that pins 0 and 1 are being jumped with a wire
* Copy `html_`, `robot_functions`, `network_` and `main.py` onboard the Pico
## Todo:

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
