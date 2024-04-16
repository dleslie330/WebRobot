from time import sleep, time
from machine import Pin, PWM

flag = True

pin_EN_r = Pin('GP13', Pin.OUT)
pwmr = PWM(pin_EN_r)
pwmr.freq(1000000)

pin_1A_r = Pin('GP14', Pin.OUT)
pin_2A_r = Pin('GP15', Pin.OUT)

pin_EN_l = Pin('GP18', Pin.OUT)
pwml = PWM(pin_EN_l)
pwml.freq(1000000)

pin_1A_l = Pin('GP17', Pin.OUT)
pin_2A_l = Pin('GP16', Pin.OUT)

def forward(duty):
    pin_1A_r.low()
    pin_2A_r.high()
    pin_1A_l.high()
    pin_2A_l.low()
    
    pwmr.duty_u16(duty)
    pwml.duty_u16(duty)

def backward(duty):
    pin_1A_r.high()
    pin_2A_r.low()
    pin_1A_l.low()
    pin_2A_l.high()

    pwmr.duty_u16(duty)
    pwml.duty_u16(duty)

def left(duty):
    pin_1A_r.low()
    pin_2A_r.high()
    pin_1A_l.low()
    pin_2A_l.high()

    pwmr.duty_u16(duty)
    pwml.duty_u16(duty)

def right(duty):
    pin_1A_r.high()
    pin_2A_r.low()
    pin_1A_l.high()
    pin_2A_l.low()

    pwmr.duty_u16(duty)
    pwml.duty_u16(duty)

def main():
    global flag

    maxduty = 65535



    flag = False

try:
    button = Pin('GP22', Pin.IN, Pin.PULL_DOWN)

    while flag:
        if button.value():
            sleep(.5)
            main()

except KeyboardInterrupt:
    print("quitting program")

finally:
    pwmr.duty_u16(0)
    pwmr.deinit()
    pin_EN_r = Pin('GP13', Pin.OUT)
    pin_EN_r.low()

    pin_1A_r.low()
    pin_2A_r.low()

    pwml.duty_u16(0)
    pwml.deinit()
    pin_EN_l = Pin('GP18', Pin.OUT)
    pin_EN_l.low()

    pin_1A_l.low()
    pin_2A_l.low()

    print("Going quietly into that good night.")
