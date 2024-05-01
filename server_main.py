from server import WebServer
import signal

print("Starting server, please wait a moment...")
server = WebServer(8080)

def handle_sigint():
    print("Shutting down server")
    server.shutdownServer()

signal.signal(signal.SIGINT, handle_sigint) # type: ignore

choice = input("Will you be using a webcam? [Y]es or [N]o or [S]hutdown\nAnswer:")
while choice != 'N' and choice != 'Y' and choice != 'S':
    choice = input("Please choose either 'Y' or 'N'. Will you be using a webcam? [Y]es or [N]o\nAnswer:")

if choice == 'Y':
    server.there_is_webcam = True
    print("Loading webcam, wait a moment...")
    server.initiate_camera()
elif choice == 'N':
    server.there_is_webcam = False
elif choice == 'S':
    server.shutdown()
    exit()
else:
    print("Something unexpected happened")
    server.shutdown()
    exit()



print("Press Ctrl+C to shut down server.")
server.start()