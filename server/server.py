import socket
import threading
import sys
import random

DEFAULT_BUFLEN = 1024
MAX_CLIENTS = 10
FILE_NAMES = ["test.txt", "CaleDoktorNauka.c", "test_slika.png", "south_park.mkv"]

killSwitch = 0 # Just for testing
usedPorts = []


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 1337)
print(f'Server is listening on {server_address[0]}:{server_address[1]}...')
sock.bind(server_address)

# Listen for incoming connections
sock.listen(MAX_CLIENTS)



# Function for serving clients independetly
def client_handler(client_socket, client_address):
    # Send all available file names to the client
    startupMessage = ''
    x = 1
    for filename in FILE_NAMES:
        startupMessage += str(x) + ') ' + filename + '\n'
        x+=1

    client_socket.sendall(startupMessage.encode())

    # Receives client input
    data = client_socket.recv(DEFAULT_BUFLEN)
    filename = data.decode()
    print('received {}'.format(filename))

    # Checks if selected filename exists on the server
    if filename not in FILE_NAMES:
        client_socket.sendall('WRONG_INPUT'.encode())
        
    else:
        # Calculate file size
        file = open(filename, 'rb')
        fileSize = 0
        chunk = file.read(1024)
        while chunk:
            fileSize += len(chunk)
            chunk = file.read(1024)
        file.close()
        
        # Calculate number of data chunks (M)
        chunkAmount = int(fileSize / 1000) + 1

        # Calculate number of sockets (N)
        socketAmount = 0
        if fileSize < 10*1024*1024: # <10MB
            socketAmount = 1
        elif fileSize < 50*1024*1024: # <50MB
            socketAmount = 2
        elif fileSize < 100*1024*1024: # <100MB
            socketAmount = 3
        elif fileSize < 250*1024*1024: # <250MB
            socketAmount = 4
        elif fileSize < 400*1024*1024: # <400MB
            socketAmount = 5
        elif fileSize < 700*1024*1024: # <700MB
            socketAmount = 6
        elif fileSize < 1000*1024*1024: # <1GB
            socketAmount = 7
        else: # >1GB
            socketAmount = 8

        # Make list of ports for data transfer
        portNumbers = []
        for i in range(socketAmount):
            port = random.randint(49152, 65535)
            while(port in usedPorts):
                port = random.randint(49152, 65535)
            portNumbers.append(port)
        
        # Listen on all ports for client to connect
        portsConnected = []

        # Funtion for thread
        def waitForConnection(portNumber):
            print('123') # When connected change bool to True

        # Calling threads
        for portNumber in portNumbers:
            portsConnected.append(False)
            transfer_thread = threading.Thread(target=waitForConnection, args=(portNumber))
            transfer_thread.start()
            transfer_thread.join()

        # while 

        # Accept download an respond with connection data
        response = f'ACCEPTED {socketAmount} {chunkAmount}'
        for portNumber in portNumbers:
            response += ' ' + str(portNumber)

        client_socket.sendall(response.encode())

        # # Read all bytes into variable
        # file = open(filename, 'rb')
        # fileBytes = file.read()
        # file.close()
    


# The infinite loop to accept and handle incoming connections
while sock:
    # Wait for a connection
    print('Waiting for a connection...')
    client_socket, client_address = sock.accept()

    print('connection from', client_address)
    killSwitch += 1

    # Create a new thread to handle the client
    client_thread = threading.Thread(target=client_handler, args=(client_socket, client_address))

    # Start and join the client thread
    client_thread.start()
    client_thread.join()

    # JUST FOR TESTING
    if killSwitch == 1:
        break


sock.close()