import socket
import sys
import threading
import html_.index_mobile as html_mobile
import html_.index_desktop as html_pc
import html_.wait as html_wait  
import html_.finish as html_finish
import re
from time import time as timer
from time import sleep
import cv2
import pickle
import struct
import json
# from flask import jsonify

class WebServer(object):
    def __init__(self, port=8080):
        hostname = socket.gethostname() # type: ignore
        self.host = socket.gethostbyname(hostname) # type: ignore
        self.camera = None
        self.port = port
        self.pico_client = None
        self.pico_client_address = None
        self.mobile_pattern = re.compile(r'X11|Android|webOS|iPhone|iPad|iPod|BlackBerry|BB|PlayBook|IEMobile|Windows Phone|Kindle|Silk|Opera', re.I)
        self.desktop_pattern = re.compile(r'macOS|Windows|Linux', re.I)
        self.clients = list()
        self.current_client_address = None
        self.current_client_disconnected = False
        self.remove_clients = False
        self.cool_down_clients = list()
        self.MAX_TIME = 60
        self.COOL_DOWN = 30
        self.TIME_OUT = 500
        self.timings = {}
        self.backlog = 5
        self.reestablish_timings = False
        # self.current_client_is_playing = True
        self.button_ids = ['forward','right','back','left','quit','stop']
        self.there_is_webcam = False

    def initiate_camera(self):
        self.camera = cv2.VideoCapture(0)

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print("Starting server on {host}:{port}".format(host=self.host, port=self.port))
            self.socket.bind((self.host, self.port))
            print("Server started on port {port}.".format(port=self.port))
        except Exception as e:
            print("Error: Could not bind to port {port}".format(port=self.port))
            self.shutdown()
            sys.exit(1)
        self._listen() 

    def shutdown(self):
        try:
            print("Shutting down server")
            self.socket.close()
        except Exception as e:
            pass 

    def _listen(self):
        self.socket.listen(self.backlog)
        threading.Thread(target=self.client_max_time).start()
        # threading.Thread(target=self.client_join_prevention).start()
        while True:
            try:
                (client, address) = self.socket.accept()
                # print("Client connected: ",client)
                client.settimeout(self.TIME_OUT)
                if address[0] != self.pico_client_address and not self.remove_clients: # make sure no one joins during removal of clients
                    if self.current_client_address is None and address[0] not in self.cool_down_clients:
                        self.current_client_address = address[0] 
                    # if address[0] not in self.cool_down_clients:
                    if address[0] not in self.clients and address[0] not in self.cool_down_clients:
                        self.clients.append(address[0])
                        size = len(self.clients) 
                        if size == 1:
                            self.timings[address[0]] = self.MAX_TIME
                        else:
                            prev_client = self.clients[size - 2]
                            t = self.timings[prev_client]
                            self.timings[address[0]] = t + self.MAX_TIME
                    threading.Thread(target=self._handle_client, args=(client, address)).start()

            except ConnectionAbortedError as cae:
                print("Client timed out:",address[0])
                self.cool_down_clients.append(address[0])
            except Exception as e:
                print("Error occured:",e)

    def build_response(self, **kwargs):
        """
        html : 
            wait : waiting screen
            index_desktop : playing robot on pc. 
            index_mobile : playing robot on phone. 
            finish : after playing robot.  
            refresh : refreshes clients page.
            close : Indicate a connection close with the client
        _json :
            json_data : dict like object. {'hello':'world'}
        video : 
            Sends a MJPEG frame of a connected Webcam (Returns a tuple(http_response, web_data))
        """
        html = kwargs.get('html', False)
        _json = kwargs.get('_json', False)
        video = kwargs.get('video', False)
        html_content = ""
        content_length = 0
        
        if html: 
            wait = kwargs.get('wait', False)
            index_desktop = kwargs.get('index_desktop', False)
            index_mobile = kwargs.get('index_mobile', False)
            finish = kwargs.get('finish', False)
            refresh = kwargs.get('refresh', False)
            counter = kwargs.get('counter', False)
            close = kwargs.get('close', False)

            if wait:
                html_content = html_wait.html
            elif index_desktop:
                html_content = html_pc.html
            elif index_mobile:
                html_content = html_mobile.html
            elif finish:
                html_content = html_finish.html
            elif refresh:
                html_content = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html\r\n"
                    "Refresh: 4;\r\n"  # Refresh the page after 4 seconds
                    "\r\n"
                    "<html><body>Page will refresh in 4 seconds...</body></html>"
                )
                return html_content
            elif close:
                html_content = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                )
                return html_content
            
            content_length = len(html_content.encode('utf-8'))
            http_response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                "Content-Length: {}\r\n"
                "\r\n"
                "{}".format(content_length, html_content)
            )            

        elif _json:
            json_data = kwargs.get('json_data', {})
            json_string = json.dumps(json_data)
            html_content = json_string
            content_length = len(json_string.encode('utf-8'))
            http_response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: {}\r\n"
            "\r\n"
            "{}".format(content_length, html_content)
            )
        
        elif video:
            ret, frame = self.camera.read()  # Capture a frame from the webcam
            if ret:
                # Compress the frame to WebP with lower quality (e.g., 5)
                _, encoded_frame = cv2.imencode('.webp', frame, [cv2.IMWRITE_WEBP_QUALITY, -1000])

                webp_data = encoded_frame.tobytes()
                data_size = len(webp_data)

                # Send HTTP headers
                headers = [
                    "HTTP/1.1 200 OK",
                    "Content-Type: image/webp",  # Use image/webp for WebP
                    f"Content-Length: {data_size}",
                    "",
                    ""
                ]
                http_response = "\r\n".join(headers).encode()

                # # Send headers
                # self.current_client.sendall(http_response)

                # # Send response data in chunks
                # self.current_client.sendall(webp_data)

                return http_response, webp_data
            
        return http_response


    def _handle_client(self, client, address):
        try:
            if address[0] in self.clients:
                PACKET_SIZE = 1024
                button_id = ""
                req = ""
                request = client.recv(PACKET_SIZE).decode()

                if 'GET /' in request:
                    req = request.split(' ')[1][1:]
                    if req in self.button_ids and address[0] == self.current_client_address:
                        button_id = req  
                        print(button_id) 

                if button_id and address[0] == self.current_client_address:
                    if self.pico_client_address:
                        self.pico_client.send(str.encode(button_id)) # type: ignore
                    return
                
                if button_id == 'stop':
                    if self.pico_client_address:
                        self.pico_client.send(str.encode(button_id)) # type: ignore 
                    return

                if req == 'video_stream':
                    if address[0] == self.current_client_address and self.there_is_webcam:
                        print("Sent a video request")
                        resp, data = self.build_response(video=True)
                        client.sendall(resp)
                        client.sendall(data)
                    return
                    
                if req == 'disconnect':
                    if address[0] == self.clients[0]:
                        self.remove_clients = True
                        self.reestablish_timings = True
                        self.current_client_disconnected = True
                        resp = self.build_response(html=True,finish=True)
                        client.send(resp.encode('utf-8')) # type: ignore
                        self.cool_down_clients.append(address[0])
                        resp = self.build_response(html=True,close=True)
                        client.send(resp.encode('utf-8')) # type: ignore
                        client.close()
                    return
                
                if req == 'wait_time':
                    if address[0] in self.cool_down_clients:
                        t = self.COOL_DOWN
                        data = {"time":t}
                        resp = self.build_response(_json=True,json_data=data)
                        client.send(resp.encode('utf-8')) # type: ignore
                    return
                    
                if req == 'ReadyToPlay':
                    # print(address[0]," is ready.")
                    if self.timings[self.current_client_address] <= 0 or address[0] == self.current_client_address:
                        if self.timings[address[0]] <= self.MAX_TIME:
                            if self.mobile_pattern.search(request):
                                resp = self.build_response(html=True,index_mobile=True)
                                client.send(resp.encode('utf-8')) # type: ignore
                                print("Mobile ready to end")
                                # print("Mobile user!")
                            else:
                                resp = self.build_response(html=True,index_desktop=True)
                                client.send(resp.encode('utf-8')) # type: ignore
                                print("Desktop ready to end")
                                # print("Desktop user!")
                            return
                        else:
                            client.send(str.encode('not ready'))
                            return
                    return
                    
                if req == 'ReadyToEnd':
                    if address[0] in self.cool_down_clients or address[0] in self.clients:
                        # while True:
                        if self.timings[address[0]] <= 0:
                            # self.cool_down_clients.append(address[0])
                            print(address[0]," is ready to end")
                            resp = self.build_response(html=True,finish=True)
                            client.send(resp.encode('utf-8')) # type: ignore
                            self.cool_down_clients.append(address[0])
                            resp = self.build_response(html=True,close=True)
                            client.send(resp.encode('utf-8'))        # type: ignore
                            client.close()
                            return
                    else:
                        client.send(str.encode('not ready'))
                        return
                    return

                if req == 'reload':  
                    if self.current_client_disconnected:
                        if address[0] == self.current_client_address or address[0] in self.clients[1]:
                            data = {'status':' because someone left'}
                            resp = self.build_response(_json=True,json_data=data)
                            client.send(resp.encode('utf-8')) # type: ignore
                            self.current_client_disconnected = False
                    return

                if req == 'time':
                    t_rem = self.timings[address[0]]
                    if address[0] == self.current_client_address:
                        data = {"time":t_rem}
                        resp = self.build_response(_json=True,json_data=data)
                        client.send(resp.encode('utf-8')) # type: ignore
                        return 
                    else:
                        data = {"time":t_rem - self.MAX_TIME}
                        resp = self.build_response(_json=True,json_data=data)
                        client.send(resp.encode('utf-8')) # type: ignore
                        return

                if "Pico" in request:
                    print("Pico connected")
                    self.pico_client = client
                    if address[0] in self.clients:
                        self.pico_client_address = address[0]
                        if address[0] == self.current_client_address:
                            if len(self.clients) == 1:
                                self.current_client_address = None
                            else:
                                self.current_client_address = self.clients[0]
                        return
                    return

                if client != str(self.pico_client):
                    if address[0] == self.clients[0]:
                        # self.current_client = client
                        if self.mobile_pattern.search(request):
                            resp = self.build_response(html=True,index_mobile=True)
                            client.send(resp.encode('utf-8')) # type: ignore
                            print("Mobile user!")
                        else:
                            resp = self.build_response(html=True,index_desktop=True)
                            client.send(resp.encode('utf-8')) # type: ignore
                            print("Desktop user!")
                    else:           
                        resp = self.build_response(html=True,wait=True)
                        client.send(resp.encode('utf-8')) # type: ignore
                    return

        except ConnectionAbortedError as cae:
            print("Client disconnected after listening:",cae)
            # self.cool_down_clients.append(address[0])
            # self.remove_clients = True

        except Exception as e:
            print("General listening error:",e)
            print(client)

    def client_max_time(self):
        t_switch = 0
        t_enable = 0
        while True:
            try:
                t_switch = 0
                if len(self.clients) != 0:

                    if self.remove_clients:
                        for gone_client in self.cool_down_clients:
                            for indx in range(len(self.clients)):
                                if self.clients[indx] == gone_client:
                                    addr = self.clients.pop(indx)
                                    self.timings.pop(addr)
                        self.remove_clients = False

                    if self.pico_client_address in self.clients:
                        for indx in range(len(self.clients)):
                            if self.clients[indx] == self.pico_client_address:
                                self.clients.pop(indx)
                                self.timings.pop(self.pico_client_address)
                                break

                    print(self.timings)
                    # print("Current client:",self.current_client_address)
                    sleep(1)
                    t_switch += 1

                    if len(self.cool_down_clients) != 0:
                        t_enable += 1
                        if t_enable == self.COOL_DOWN:
                            self.cool_down_clients.pop(0)
                            t_enable = 0

                    for key,value in self.timings.items():
                        self.timings[key] -= t_switch

                    if self.reestablish_timings:
                        current_client = self.clients.pop(0)
                        self.cool_down_clients.append(current_client)
                        t = self.timings.pop(current_client)
                        self.current_client_address = self.clients[0]
                        for key,value in self.timings.items():
                            self.timings[key] -= t
                        self.reestablish_timings = False

                    if self.timings[self.current_client_address] <= -1:
                        size = len(self.clients)
                        if size - 1 == 0:
                            self.timings[self.current_client_address] = self.MAX_TIME
                        else:
                            # prev_client = self.clients[len(self.clients) - 2]
                            # t = self.timings[prev_client]
                            # self.timings[self.current_client_address] = t + self.MAX_TIME * 2
                            # current_client = self.clients.pop(0)
                            # self.clients.append(current_client)
                            # self.current_client_address = self.clients[0]
                            self.current_client_address = self.clients[1]
                            # current_client = self.clients.pop(0)
                            # self.cool_down_clients.append(current_client)
                            # self.timings.pop(current_client)
                            self.remove_clients = True
                            self.cool_down_clients.append(self.clients[0])
                    
                    t_switch = 0
                    if t_enable > self.COOL_DOWN:
                        t_enable = 0
                    # print("The current client is",self.current_client_address)
                    # print("Size:",len(self.clients))
            except Exception as e:
                print(e)
    
    # def client_join_prevention(self):
    #     t_enable = 0
    #     while True:
    #         try:
    #             if len(self.cool_down_clients) != 0:
    #                 sleep(1)
    #                 t_enable += 1
    #                 if t_enable == self.COOL_DOWN:
    #                     self.cool_down_clients.pop(0)
    #                     t_enable = 0
    #         except:
    #             print("Something bad happened")

    # def reestablish_timings(self, t):
    #     # t = 0.5 * t
    #     while True:
    #         try:
    #             for key,value in self.timings.items():
    #                 self.timings[key] -= t
    #             break
    #         except:
    #             print("client_max_time is blocking this operation")

    def shutdownServer(self):
        self.shutdown()
        sys.exit(1)