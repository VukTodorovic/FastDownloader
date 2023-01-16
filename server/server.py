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
        file = open('./files/' + filename, 'rb')
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
        # print(f'Active threads: {threading.enumerate()}')
        for t in transferThreads:
            t.join()

        print('All ports connected')

        # Initialize queues and variables for sending
        finished = False
        chunk_queues = []
        for i in range(0, socketAmount):
            q = Queue() # Set max size later
            chunk_queues.append(q) 
        chunks_sent = []    # Testing queued chunks
        for pn in portNumbers:
            chunks_sent.append(0)



        # Function for thread that sends bytes
        def sendBytesToStream(pos):
            while((not finished) or (not chunk_queues[pos].empty())):
                if not chunk_queues[pos].empty():
                    next_chunk = chunk_queues[pos].get()
                    try:
                        clientSockets[pos].sendall(next_chunk)
                        print(f'[*]Chunk success: {pos}')
                        chunks_sent[pos] += 1
                        # time.sleep(0.1)
                    except Exception as e:
                        print(f'[!]Chunk failed: {pos}')
                        time.sleep(2)
                        sys.exit()
                else:
                    time.sleep(0.1)
                    print(123)

                
        
        # Create threads
        sendingThreads = []
        for i in range(0, socketAmount):
            sending_thread = threading.Thread(target=sendBytesToStream, args=(i,))
            sending_thread.start()
            sendingThreads.append(sending_thread)
        # print(f'Active threads: {threading.enumerate()}')


        # Dividing the file and filling the queues
        file = open('./files/' + filename, 'rb')
        j = 0
        k = 0

        chunks_queued = []    # Testing queued chunks
        for pn in portNumbers:
            chunks_queued.append(0)

        firstTime = True
        while chunk or firstTime:
            if firstTime:
                firstTime = False
            chunk = file.read(1000)
            # bytesToSend = int.to_bytes(k) + chunk
            bytesToSend = chunk
            
            chunk_queues[j].put(bytesToSend)

            k += 1
            chunks_queued[j] += 1
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
        for chq in chunks_queued:
            print(f'Chunks queued: {chq}')

        print('--------------------------------')
        for cs in chunks_sent:
            print(f'Chunks sent: {cs}')
        
        print('--------------------------------')
        for cq in chunk_queues:
            print(f'Queue size: {cq.qsize()}, Empty: {cq.empty()}') 

        
    


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