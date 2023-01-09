import socket
import threading
import sys
import random
import time

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
        clientSockets = []
        for i in range(socketAmount):
            port = random.randint(49152, 65535)
            while(port in usedPorts):
                port = random.randint(49152, 65535)
            portNumbers.append(port)

        # Accept download an respond with connection data
        response = f'ACCEPTED {socketAmount} {chunkAmount}'
        for portNumber in portNumbers:
            response += ' ' + str(portNumber)

        client_socket.sendall(response.encode())
        
        # Listen on all ports for client to connect
        portsConnected = []

        # Funtion for thread
        def waitForConnection(portNumber, listPosition):
            # Create a TCP/IP socket
            signleStream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            streamAddress = ('localhost', portNumber)
            signleStream.bind(streamAddress)
            print(f'Listening stream on port: {portNumber}')
            signleStream.listen(1)

            # Accept connection
            cli_socket, cli_address = signleStream.accept() # client_socket <-- send over this
            clientSockets.append(cli_socket)
            portsConnected[listPosition] = True
            print(f'Connected stream on port: {portNumber}')

            




        # Calling threads
        for i in range(0, len(portNumbers)): # for portNumber in portNumbers:
            portsConnected.append(False)
            transfer_thread = threading.Thread(target=waitForConnection, args=(portNumbers[i], i))
            transfer_thread.start()
        # Join threads
        

        # Function that checks if all ports are connected
        def connectionFinished():
            for connPort in portsConnected:
                if connPort == False:
                    return False
            return True

        # Wait for connection to finish (maybe use conditional variable later)
        while not connectionFinished():
            continue

        print('All ports connected')

        # Divide file into chunks and send over streams

        # Function for thread that sends bytes
        def sendBytesToStream(pos, data):
            clientSockets[pos].sendall(data)

        # Dividing the file and creating threads
        file = open(filename, 'rb')
        chunk = file.read(1000)
        j = 0
        k = 0
        while chunk:
            chunk = file.read(1000)
            # bytesToSend = int.to_bytes(k) + chunk
            bytesToSend = chunk
            
            sending_thread = threading.Thread(target=sendBytesToStream, args=(j, bytesToSend))
            sending_thread.start()

            k += 1
            if j == len(clientSockets)-1:
                j = 0
            else:
                j += 1
        file.close()

        # Closing connections
        for cliSock in clientSockets:
            cliSock.close()

        # testing
        print('sleeping')
        time.sleep(1) 

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