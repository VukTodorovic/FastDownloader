import socket
import threading
import sys
import random
import time
from queue import Queue

DEFAULT_BUFLEN = 1024
MAX_CLIENTS = 10
FILE_NAMES = ["CaleDoktorNauka.c", "slika1.png", "gamefile.dll", "analiza2.pdf", "south_park.mkv"]

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

        #socketAmount = 6 #OBRISATI

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
    

        # Funtion for thread
        def waitForConnection(portNumber):
            # Create a TCP/IP socket
            signleStream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            streamAddress = ('localhost', portNumber)
            signleStream.bind(streamAddress)
            print(f'Listening stream on port: {portNumber}')
            signleStream.listen(1)

            # Accept connection
            cli_socket, cli_address = signleStream.accept() # client_socket <-- send over this
            clientSockets.append(cli_socket)
            print(f'Connected stream on port: {portNumber}')


        transferThreads = []
        # Calling threads
        for i in range(0, socketAmount):
            transfer_thread = threading.Thread(target=waitForConnection, args=(portNumbers[i],))
            transfer_thread.start()
            transferThreads.append(transfer_thread)
        # Join threads
        print(f'Active threads: {threading.enumerate()}')
        for t in transferThreads:
            t.join()

        print('All ports connected')

        # Divide file into chunks and send over streams
        finished = False
        chunk_queues = []
        queue_max = []
        for i in range(0, socketAmount):
            q = Queue() # Set max size later
            chunk_queues.append(q) 
            queue_max.append(0)

        # Function for thread that sends bytes
        def sendBytesToStream(pos):
            x = 0
            #print('1')
            while((not finished) or (not chunk_queues[pos].empty())):
                # if x == 0:
                #     print('123')
                #     x = 1
                if not chunk_queues[pos].empty():
                    if x == 0:
                        print('123')
                        x = 1
                    next_chunk = chunk_queues[pos].get()
                    clientSockets[pos].sendall(next_chunk)
                    
                
        
        # Create threads
        max_thread_count = 0
        sendingThreads = []
        for i in range(0, socketAmount):
            sending_thread = threading.Thread(target=sendBytesToStream, args=(i,))
            sending_thread.start()
            sendingThreads.append(sending_thread)
        print(f'Active threads: {threading.enumerate()}')


        # Dividing the file and filling the queues
        file = open(filename, 'rb')
        chunk = file.read(1000)
        j = 0
        k = 0
        while chunk:
            chunk = file.read(1000)
            # bytesToSend = int.to_bytes(k) + chunk
            bytesToSend = chunk
            
            # clientSockets[j].sendall(bytesToSend)
            chunk_queues[j].put(bytesToSend)

            qsize = chunk_queues[j].qsize()
            if(qsize > queue_max[j]):
                queue_max[j] = qsize

            tcsize = threading.active_count()
            if(tcsize > max_thread_count):
                max_thread_count = tcsize

            k += 1
            if j == socketAmount-1:
                j = 0
            else:
                j += 1
        file.close()
        finished = True

        # Closing connections
        for cliSock in clientSockets:
            cliSock.close()

        # testing


        print('done')
        print('--------------------------------')
        for qm in queue_max:
            print(f'Queue max: {qm}')
        
        print('--------------------------------')
        for cq in chunk_queues:
            print(f'Queue size: {cq.qsize()}')

        print('--------------------------------')
        print(f'Max tread count: {max_thread_count}')   
    


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