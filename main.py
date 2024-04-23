import utime
import json
import uasyncio
import _thread
import random
import machine
import network
from robot_functions.functions import functions as fct
from html_.index import html

# connect to WiFi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print('Connecting to network...')
    while not wlan.isconnected():
        pass
    if wlan.status() == 3:
        # wlan.ifconfig((UDP_IP, '255.255.255.0', "192.168.12.1", '192.168.1.1'))
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
        raise RuntimeError('network connection failed')


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
    ssid = "AJAY-DESKTOP"
    password = "1687Hv?0"
    port = 5878
    ip = connect_to_wifi(ssid,password)
    print("Uploading wifi credentials...")
    with open('address.txt', "w") as file:
        file.write(ip+":")
        file.write(str(port))
    file.close()
    print('Setting up webserver...')
    server = uasyncio.start_server(handle_request, ip, port) # type: ignore
    uasyncio.create_task(server)
    print("Server is online")
    fun.is_ready = True
    fun.set_status_ready()
    while True:
        if fun.is_on:
            await uasyncio.sleep(0)
        else:
            break

def robot_mobility():
    while True:
        if fun.operation:
            print(fun.operation)
            fun.do_operation()
            fun.set_operation("")
        if not fun.is_on:
            while not fun.is_ready:
                fun.set_status_thinking(0.5)

# Setup PicoBot
fun = fct()
fun.set_dc_var(fun.get_max_dc_var())
fun.set_freq_var(fun.get_max_freq_var())
fun.set_duty()
fun.set_freq()

second_thread = _thread.start_new_thread(robot_mobility, ())

try:
    # start asyncio tasks on first core
    uasyncio.run(main())
finally:
    uasyncio.new_event_loop()
    fun.shut_off()
    machine.reset()