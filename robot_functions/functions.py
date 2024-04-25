# H-Bridge and using PWM to navigate a maze 

from utime import sleep
from machine import Pin, PWM
from math import pi

class functions():
    def __init__(self) -> None:
        self.pin_EN2 = Pin(12, Pin.OUT) # enable pin for CS pin
        self.pin_EN1 = Pin(13, Pin.OUT) # enable pin for CS pin
        self.pin_1A_r = Pin(14, Pin.OUT)
        self.pin_2A_r = Pin(15, Pin.OUT)
        self.pin_1A_l = Pin(16, Pin.OUT)
        self.pin_2A_l = Pin(17, Pin.OUT)
        self.status = Pin("LED", Pin.OUT)
        self.pwm_r = PWM(self.pin_EN1) # PWM object
        self.pwm_l = PWM(self.pin_EN2)
        self.MAX_DC = 65535
        self.MAX_FREQ = 10000
        self.operation = ""
        self.is_on = True
        self.is_ready = False

    def set_status_thinking(self,time): 
        while True:
            self.status.toggle()
            sleep(time)
            if self.is_ready:
                break

    def set_status_ready(self):
        self.status.high()

    def set_operation(self, operation):
        self.operation = operation

    def get_max_freq_var(self):
        return self.MAX_FREQ

    def get_max_dc_var(self):
        return self.MAX_DC

    def set_freq_var(self,freq):
        self.freq = freq

    def set_dc_var(self,dc):
        self.dc = dc

    def set_freq(self):
        self.pwm_r.freq(self.freq)
        self.pwm_l.freq(self.freq)

    def set_duty(self,dc=None):
        if dc is not None:
            self.pwm_r.duty_u16(dc)
            self.pwm_l.duty_u16(dc)
        else:    
            self.pwm_r.duty_u16(self.dc)
            self.pwm_l.duty_u16(self.dc)


    def setup(self):
        self.pin_EN2 = Pin(12, Pin.OUT) 
        self.pin_EN1 = Pin(13, Pin.OUT) 
        self.pin_1A_r = Pin(14, Pin.OUT)
        self.pin_2A_r = Pin(15, Pin.OUT)
        self.pin_1A_l = Pin(16, Pin.OUT)
        self.pin_2A_l = Pin(17, Pin.OUT)
        self.pwm_r = PWM(self.pin_EN1) 
        self.pwm_l = PWM(self.pin_EN2)
 

    # def determine_run_linear(d):
    #     """
    #     d = C * R * G
    #     T = D / (C * R * G)
    #     d = (distance to travel in cm)
    #     C = pi*d
    #     R = 3.33333 RPS or 200 RPM
    #     G = 1:48
    #     """
    #     RPM = 150
    #     RPS = RPM / 60
    #     G = 48 
    #     diameter = 6 # cm
    #     C = pi*diameter
    #     T = d / (C * RPS)
    #     return T

    # def determine_run_angular(d):
    #     """
    #     ::param d:: degrees
    #     d = C * R * G
    #     T = D / (C * R * G)
    #     d = (distance to travel in cm)
    #     C = pi*d
    #     R = 3.33333 RPS or 200 RPM
    #     G = 1:48
    #     """
    #     diameter = 10.8 # d between robot wheels in cm
    #     C = pi*diameter # circumference of robots wheels in cm
    #     d = (C * d) / 360
    #     RPM = 126
    #     RPS = RPM / 60
    #     G = 48 
    #     diameter = 6 # cm
    #     C = pi*diameter
    #     T = d / (C * RPS)
    #     return T

    # # Routines
    def forward(self):
        self.set_duty()
        self.set_freq()
        self.pin_1A_r.low()
        self.pin_2A_r.high()
        self.pin_1A_l.high()
        self.pin_2A_l.low()
        
    def full_stop(self):
        self.set_duty(0)

    def backward(self):
        self.set_duty()
        self.set_freq()
        self.pin_1A_r.high()
        self.pin_2A_r.low()
        self.pin_1A_l.low()
        self.pin_2A_l.high()

    def left(self):
        self.set_duty()
        self.set_freq()
        self.pin_1A_r.low()
        self.pin_2A_r.high()
        self.pin_1A_l.low()
        self.pin_2A_l.high()
        

    def right(self):
        self.set_duty()
        self.set_freq()
        self.pin_1A_r.high()
        self.pin_2A_r.low()
        self.pin_1A_l.high()
        self.pin_2A_l.low()

    def wait_for_a_second(self):
        sleep(1)

    # def operate_until_t(t):
    #     sleep(t)


    def shut_off(self):
        self.pin_1A_r.low()
        self.pin_2A_r.low()
        self.pin_1A_l.low()
        self.pin_2A_l.low()
        self.pwm_r.duty_u16(0) # set dc to 0%
        self.pwm_r.deinit() # turn OFF pwm
        self.pwm_l.duty_u16(0)
        self.pwm_l.deinit()
        motor = Pin(13,Pin.OUT) # reset the motor pin to an output
        motor.low() # force the motor pin LOW
        motor = Pin(12,Pin.OUT)
        motor.low()

    def do_operation(self):
        if self.operation == "forward":
            self.forward()
        elif self.operation == "right":
            self.right()
        elif self.operation == "left":
            self.left()
        elif self.operation == "back":
            self.backward()
        elif self.operation == "stop":
            self.full_stop()
        elif self.operation == "quit":
            self.shut_off()
            self.is_on = False