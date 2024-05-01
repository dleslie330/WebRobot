import utime
import usocket as socket
from time import sleep
import uasyncio
import _thread
import machine
from machine import Pin
import network
from robot_functions.functions import functions as fct
from network_.server_cred import server_cred as server_secrets
from network_.wifi_cred import wifi as wifi_secrets

start_pin = Pin(0,Pin.OUT)
start_pin_con = Pin(1,Pin.IN, Pin.PULL_DOWN)

def inter(gate):
    global flag
    flag = True

start_pin_con.irq(handler=inter,trigger=start_pin.IRQ_RISING)

# connect to WiFi
def connect_to_wifi(ssid, password):
    start = utime.time()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print('Connecting to network...')
    while not wlan.isconnected():
        fun.status.toggle()
        utime.sleep(0.1)
        if utime.time() - start > 10:
            return None
    if wlan.status() == 3:
        status = wlan.ifconfig()
        print("Connected as {}".format(status[0]))
        return wlan.ifconfig()[0]
    else:
        print("Failed:\n")
        print("Idle:",network.STAT_IDLE)
        print("Connecting:",network.STAT_CONNECTING)
        print("Wrong Password:",network.STAT_WRONG_PASSWORD)
        print("No AP found:",network.STAT_NO_AP_FOUND)
        print("Connection Failed:",network.STAT_CONNECT_FAIL)
        print("IP assigned:",network.STAT_GOT_IP)
        print("Resetting...")
        raise Exception('network connection failed')

async def receive_data_from_server(sock):
    
    try:
        while True:
            data = sock.recv(1024) # buffer size is 1024 bytes
            print("received message: %s" % data.decode())
    except Exception as e:
        print(e)

async def main():
    print("hi!")
    wc = wifi_secrets()
    sc = server_secrets()
    ssid = wc.get_ssid()
    password = wc.get_password()
    port = sc.get_port()
    ip = sc.get_ip()
    connecting = connect_to_wifi(ssid,password)
    while connecting is None:
        connecting = connect_to_wifi(ssid,password)
        print(connecting)
    fun.is_ready = True
    fun.set_status_ready()
    global ready 
    ready = True 
    # ip = "192.168.1.21"
    # port = 8080
    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_STREAM) # TCP
    sock.connect((ip, port))
    print("Connected to host")
    sock.send("I'm the Pico!")
    while True:
        if fun.is_on:
            data = sock.recv(1024) # buffer size is 1024 bytes
            operation = data.decode()
            print("received message: %s" % operation)
            fun.operation = operation
            await uasyncio.sleep(0)
        else:
            break

def robot_mobility():
    curr_operation = ""
    while True:
        if ready:
            while True:
                if fun.operation != curr_operation:
                    print(fun.operation)
                    fun.do_operation()
                    curr_operation = fun.operation

flag = False
start_pin.high()
start = utime.time()
while not flag and utime.time() - start < 10:
    print("Waiting to connect.")
    utime.sleep(1)
if utime.time() - start:
    machine.reset()
    
start_pin_con.irq(handler=None)

# Setup PicoBot
fun = fct()
fun.set_dc_var(fun.get_max_dc_var())
fun.set_freq_var(fun.get_max_freq_var())
fun.set_duty()
fun.set_freq()

global ready
ready = False
second_thread = _thread.start_new_thread(robot_mobility, ())

try:
    # start asyncio tasks on first core
    uasyncio.run(main())

except Exception as e:
    print(e)
finally:
    uasyncio.new_event_loop()
    fun.shut_off()
    machine.reset()