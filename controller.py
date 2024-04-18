from socket import *

serverName = '192.168.0.1'
serverPort = 8080
clientSocket = socket(AF_INET, SOCK_DGRAM)
message = bytes("connection", 'utf-8')
clientSocket.sendto(message,(serverName, serverPort))
print("message should be sent")
clientSocket.close()
print("socket is now closed")
