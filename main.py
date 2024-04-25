import utime
import math
from time import sleep
import uasyncio
import _thread
import machine
from machine import Pin
import network
from robot_functions.functions import functions as fct
from html_.index import html
from network_.server_cred import server_cred as server_secrets
from network_.wifi_cred import wifi as wifi_secrets

start_pin = Pin(0,Pin.OUT)
start_pin_con = Pin(1,Pin.IN, Pin.PULL_DOWN)

def inter(gate):
    global flag
    flag = True

start_pin_con.irq(handler=inter,trigger=start_pin.IRQ_RISING)

# connect to WiFi
def connect_to_wifi(ssid, password, ip):
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
        print("no?")
        wlan.ifconfig((ip, '255.255.255.0', '192.168.0.1', '8.8.8.8'))
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


# Function to handle incoming requests
async def handle_request(client, writer):
    print("Client connected from:", client)
    request = await client.read(1024)
    request = str(request)
    button_id = None
    if 'GET /' in request:
        button_id = request.split(' ')[1][1:]
    protocol = 'HTTP/1.1 200 OK\n'
    protocol += 'Content-Type: text/html\n'
    protocol += 'Connection: close\n\n'
    writer.write(protocol)
    writer.write(html)
    await writer.drain()
    await writer.wait_closed()
    if button_id:
        print("Button", button_id, "clicked")
        fun.set_operation(button_id)

async def main():
    wc = wifi_secrets()
    sc = server_secrets()
    ssid = wc.ssid
    password = wc.password
    port = sc.port
    ip = sc.ip
    ip = connect_to_wifi(ssid,password,sc.ip)
    while ip is None:
        ip = connect_to_wifi(ssid,password,sc.ip)
    print('Setting up webserver...')
    fun.is_ready = True
    fun.set_status_ready()
    global ready 
    ready = True
    server = uasyncio.start_server(handle_request, ip, port) # type: ignore
    print(ip)
    print(port)
    uasyncio.create_task(server)
    print("Server is online")
    while True:
        if fun.is_on:
            await uasyncio.sleep(0)
        else:
            break

def robot_mobility():
    while True:
        if ready:
            print("ready!")
            while True:
                if fun.operation:
                    print(fun.operation)
                    fun.do_operation()
                    fun.set_operation("")

flag = False
start_pin.high()
while not flag:
    print("Waiting to connect.")
    utime.sleep(1)
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
finally:
    uasyncio.new_event_loop()
    fun.shut_off()
    machine.reset()