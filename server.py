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
        self.port = port
        self.pico_client = None
        self.pico_client_address = None
        self.mobile_pattern = re.compile(r'X11|Android|webOS|iPhone|iPad|iPod|BlackBerry|BB|PlayBook|IEMobile|Windows Phone|Kindle|Silk|Opera', re.I)
        self.desktop_pattern = re.compile(r'macOS|Windows|Linux', re.I)
        self.clients = list()
        self.current_client = None
        self.current_client_disconnected = False
        self.remove_clients = False
        self.cool_down_clients = list()
        self.MAX_TIME = 30
        self.MAX_WAIT = 10
        self.COOL_DOWN = 15
        self.TIME_OUT = 10
        self.timings = {}
        self.backlog = 5
        self.reestablish_timings = False
        # self.current_client_is_playing = True
        self.button_ids = ['forward','right','back','left','quit','stop']

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
        threading.Thread(target=self.client_join_prevention).start()
        while True:
            try:
                (client, address) = self.socket.accept()
                # print("Client connected: ",client)
                client.settimeout(self.TIME_OUT)
                if address[0] != self.pico_client_address and not self.remove_clients: # make sure no one joins during removal of clients
                    if self.current_client is None:
                        self.current_client = address[0] 
                    if address[0] not in self.cool_down_clients:
                        if address[0] not in self.clients:
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
        """
        html = kwargs.get('html', False)
        _json = kwargs.get('_json', False)
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
                    if req in self.button_ids and address[0] == self.current_client:
                        button_id = req  
                        print(button_id)  

                if req == 'disconnect':
                    if address[0] == self.clients[0]:
                        self.remove_clients = True
                        self.reestablish_timings = True
                        self.current_client_disconnected = True
                        resp = self.build_response(html=True,finish=True)
                        client.send(resp.encode('utf-8'))
                        self.cool_down_clients.append(address[0])
                        resp = self.build_response(html=True,close=True)
                        client.send(resp.encode('utf-8'))
                        client.close()
                        return
                    
                if req == 'ReadyToPlay':
                    # print(address[0]," is ready.")
                    if self.timings[self.current_client] <= 0 or address[0] == self.current_client:
                        if self.timings[address[0]] <= self.MAX_TIME:
                            if self.mobile_pattern.search(request):
                                resp = self.build_response(html=True,index_mobile=True)
                                client.send(resp.encode('utf-8'))
                                print("Mobile ready to end")
                                # print("Mobile user!")
                            else:
                                resp = self.build_response(html=True,index_desktop=True)
                                client.send(resp.encode('utf-8'))
                                print("Desktop ready to end")
                                # print("Desktop user!")
                            return
                        else:
                            client.send(str.encode('not ready'))
                            return
                    
                if req == 'ReadyToEnd':
                    if address[0] in self.cool_down_clients or address[0] in self.clients:
                        # while True:
                        if self.timings[address[0]] <= 0:
                            # self.cool_down_clients.append(address[0])
                            print("Ready to End")
                            resp = self.build_response(html=True,finish=True)
                            client.send(resp.encode('utf-8'))
                            self.cool_down_clients.append(address[0])
                            resp = self.build_response(html=True,close=True)
                            client.send(resp.encode('utf-8'))       
                            client.close()
                            return
                    else:
                        client.send(str.encode('not ready'))

                if req == 'reload':  
                    if self.current_client_disconnected:
                        if address[0] == self.current_client or address[0] in self.clients[1]:
                            data = {'status':' because someone left'}
                            resp = self.build_response(_json=True,json_data=data)
                            client.send(resp.encode('utf-8'))
                            self.current_client_disconnected = False
                        return
                    else:
                        return

                if req == 'time':
                    t_rem = self.timings[address[0]]
                    if address[0] == self.current_client:
                        data = {"time":t_rem}
                        resp = self.build_response(_json=True,json_data=data)
                        client.send(resp.encode('utf-8'))
                        return 
                    else:
                        data = {"time":t_rem - self.MAX_TIME}
                        resp = self.build_response(_json=True,json_data=data)
                        client.send(resp.encode('utf-8'))
                        return

                if "Pico" in request:
                    print("Pico connected")
                    self.pico_client = client
                    if address[0] in self.clients:
                        if self.current_client == self.pico_client_address:
                            if len(self.clients) == 0:
                                self.current_client = None
                            else:
                                self.current_client = self.clients[0]
                        self.pico_client_address = address[0]
                        indx = self.clients.index(address[0])
                        self.clients.pop(indx)
                        self.timings.pop(address[0])
                        return

                if client != str(self.pico_client):
                    if address[0] == self.clients[0]:
                        if self.mobile_pattern.search(request):
                            resp = self.build_response(html=True,index_mobile=True)
                            client.send(resp.encode('utf-8'))
                            print("Mobile user!")
                        else:
                            resp = self.build_response(html=True,index_desktop=True)
                            client.send(resp.encode('utf-8'))
                            print("Desktop user!")
                    else:           
                        resp = self.build_response(html=True,wait=True)
                        client.send(resp.encode('utf-8'))

                if button_id and address[0] == self.current_client:
                    if self.pico_client_address:
                        self.pico_client.send(str.encode(button_id)) # type: ignore
                elif button_id == 'stop':
                    if self.pico_client_address:
                        self.pico_client.send(str.encode(button_id)) # type: ignore

        except ConnectionAbortedError as cae:
            print("Client disconnected after listening:",cae)

        except Exception as e:
            print("General listening error:",e)

    def client_max_time(self):
        t_switch = 0
        while True:
            try:
                t_switch = 0
                if len(self.clients) != 0:
                    if self.remove_clients:
                        for gone_client in self.cool_down_clients:
                            for indx in range(len(self.clients)):
                                if self.clients[indx] == gone_client:
                                    self.clients.pop(indx)
                        self.remove_clients = False
                    print(self.timings)
                    # print("Current client:",self.current_client)
                    sleep(1)
                    t_switch += 1
                    for key,value in self.timings.items():
                        self.timings[key] -= t_switch

                    if self.reestablish_timings:
                        current_client = self.clients.pop(0)
                        self.cool_down_clients.append(current_client)
                        t = self.timings.pop(current_client)
                        self.current_client = self.clients[0]
                        for key,value in self.timings.items():
                            self.timings[key] -= t
                        self.reestablish_timings = False

                    if self.timings[self.current_client] <= -1:
                        size = len(self.clients)
                        if size - 1 == 0:
                            self.timings[self.current_client] = self.MAX_TIME
                        else:
                            prev_client = self.clients[len(self.clients) - 2]
                            t = self.timings[prev_client]
                            self.timings[self.current_client] = t + self.MAX_TIME * 2
                            current_client = self.clients.pop(0)
                            self.clients.append(current_client)
                            self.current_client = self.clients[0]
                    
                    t_switch = 0
                    # print("The current client is",self.current_client)
                    # print("Size:",len(self.clients))
            except Exception as e:
                print(e)
    
    def client_join_prevention(self):
        t_enable = 0
        while True:
            try:
                if len(self.cool_down_clients) != 0:
                    sleep(1)
                    t_enable += 1
                    if t_enable == self.COOL_DOWN:
                        self.cool_down_clients.pop(0)
                        t_enable = 0
            except:
                print("Something bad happened")

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