import socket
import sys
import threading
from datetime import datetime

DEFAULT_BUFLEN = 1024

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server
server_address = ('localhost', 1337)
print(f'connecting to {server_address[0]} port {server_address[1]}')
print('--------------------------------')
sock.connect(server_address)


# Receive and print all available file names
response = sock.recv(DEFAULT_BUFLEN).decode()
print(f'\nAvailable files to download:\n{response}')
print('--------------------------------')

# Get user input and send to the server
fileName = input('Choose file name: ')
sock.sendall(fileName.encode())

# Receive and print the response from the server
response = sock.recv(DEFAULT_BUFLEN).decode()
print(f'Server response: {response}')
responseValues = response.split(' ')

# If file doesn't exist on server
if response == 'WRONG_INPUT':
    sock.close()
    sys.exit()

# If request is accepted process connection requirements

streamPorts = []
for i in range(3, 3+int(responseValues[1])):
    streamPorts.append(int(responseValues[i]))

# Funtion for thread
k = int(responseValues[2])

chunksRecieved = 0
def connectToStream(portNumber):
    global chunksRecieved
    # Create a TCP/IP socket and connect to the stream
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stream_address = ('localhost', portNumber)
    clientSocket.connect(stream_address)
    print(f'Connected to stream on port: {portNumber}')

    # Client gets chunks of data and writes them to a file
    while(chunksRecieved < k):
        resp = clientSocket.recv(DEFAULT_BUFLEN)
        # print('--------------------------------')
        # print(f'[!]Server response on port {portNumber}: {resp}')
        response_parts = resp.split(b' ')
        # num = int(response_parts[0].decode())
        # num = response_parts[0].decode('utf-8')
        # print(num)
        # bytes = result_parts[1]
        if resp == b'':
            sys.exit()
        # mutex = threading.Lock()
        # mutex.acquire()
        chunksRecieved += 1
        # print(f'chunksRecieved: {chunksRecieved}')
        # mutex.release()

    clientSocket.close() #testing
    print(f'Socket on port {portNumber} has finished receiving')


# Calling threads
transferThreads = []
startTime = datetime.now()
for streamPort in streamPorts:
    transfer_thread = threading.Thread(target=connectToStream, args=(streamPort,))
    transfer_thread.start()
    transferThreads.append(transfer_thread)
# Join threads
for tr_thread in transferThreads:
    tr_thread.join()

transferTime = datetime.now() - startTime
print('--------------------------------')
print(f'Transfer time: {transferTime}')
print(f'Chunks expected: {k}')
print(f'Chunks received: {chunksRecieved}')
print(f'File size: {(chunksRecieved/1024)} KB')

# Close the connection
sock.close()







# Write bytes to new file
# file = open(fileName, 'wb')
# file.write(data)