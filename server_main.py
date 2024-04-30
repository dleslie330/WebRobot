from server import WebServer
import signal

server = WebServer(8080)

def handle_sigint():
    print("Shutting down server")
    server.shutdownServer()

signal.signal(signal.SIGINT, handle_sigint) # type: ignore

print("Press Ctrl+C to shut down server.")
server.start()