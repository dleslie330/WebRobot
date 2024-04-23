# WebRobot
Our Microcontrollers project where we are building and programming a robot to be controlled over a wifi connection

## Steps to operate
### Wired
* run `main.py` while tethered to Pico
* Read ip address from terminal or look at `address.txt` generated once Pico is connected 
* Paste the credentials in a web browser
### Wireless
* ensure `main.py` and `robot_functions` and `html_` are onboard the Pico
* once power is connected to Pico, wait for onboard LED to be solid green
* refresh web page in browser if nothing is displayed
* control the PicoBot
##


## Todo:
* webcam 
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
        - some circuit diagrams?
        - some very simple flow charts for code? -->
