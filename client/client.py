import socket
import sys
import threading
from datetime import datetime
import time
from queue import Queue

DEFAULT_BUFLEN = 1400
mutexFile = threading.Lock()
mutexConn = threading.Lock()

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


downloadedFile = open('./files/' + fileName, 'wb')
chunksRecieved = 0
nextChunkToWrite = 0
finishedReceiving = False
chunkQueue = []

# testing
fileWrites = 0
linearInserts = 0
kill = False
insertedFromQueue = 0
firstElemTest = 0
lastWritten = 0

# Function for file write
def writeBytesToFile(bytesToWrite):
    mutexFile.acquire()
    global fileWrites
    fileWrites += 1
    global nextChunkToWrite
    
    downloadedFile.write(bytesToWrite)
    nextChunkToWrite += 1

    mutexFile.release()

# Function for inserting new chunk in sorted order
def linear_search_insert(arr, orderNum):
    global linearInserts
    linearInserts += 1
    for i in range(len(arr)):
        try:
            currentItem = arr[i]
        except:
            i=0
            currentItem = arr[i]
        if currentItem[0] > orderNum:
            return i
    return len(arr)

# Testing
def printCurrentProgress():
    print('Progress:')
    while not finishedReceiving:
        print('\n\n--------------------------')
        print(f'fileWrites: {fileWrites} & linearInserts: {linearInserts}')
        print('--------------------------')
        print(f'Puta usao u drugi if: {insertedFromQueue}')
        print('--------------------------')
        print(f'Queue size: {len(chunkQueue)}')
        print('--------------------------')
        print(f'firstElemTest: {firstElemTest}')
        print('--------------------------')
        print(f'Next chunk to write: {nextChunkToWrite}')
        print('--------------------------')
        print(f'Chunks expected: {k}')
        print('--------------------------')
        print(f'Chunks received: {chunksRecieved}')
        print('--------------------------')
        print('Queue:')
        for i in range(len(chunkQueue)):
            cq = chunkQueue[i]
            print(cq[0])
            if i == 10:
                break
        time.sleep(5)  # Wait for 5 seconds
    

# Funtion for thread
k = int(responseValues[2])

def connectToStream(portNumber):
    global chunksRecieved
    global finishedReceiving
    global kill

    # Create a TCP/IP socket and connect to the stream
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stream_address = ('localhost', portNumber)
    clientSocket.connect(stream_address)
    print(f'Connected to stream on port: {portNumber}')

    # Client gets chunks of data and writes them to a file
    while not finishedReceiving:
        resp = clientSocket.recv(DEFAULT_BUFLEN)
        if resp == b'':
            finishedReceiving = True
            kill = True
            sys.exit()
        response_parts = resp.split(b'$SEPARATOR$') 
        try:
            ordinalNumber = int(response_parts[0].decode('utf-8'))
        except:
            print(response_parts[0])
        chunk = response_parts[1]
        # print('----------------')
        # print(response_parts)
        # print('----------------')

        if nextChunkToWrite == ordinalNumber:
            writeBytesToFile(chunk)
        else:
            posInQueue = linear_search_insert(chunkQueue, ordinalNumber)
            values = [ordinalNumber, chunk]

            chunkQueue.insert(posInQueue, values)
        
        chunksRecieved += 1
        if chunksRecieved >= k:
            finishedReceiving = True


    clientSocket.close() #testing
    print(f'Socket on port {portNumber} has finished receiving')
    print('--------------------------')
    print(f'fileWrites: {fileWrites}')
    print('--------------------------')
    print(f'linearInserts: {linearInserts}')
    

def insertFromQueue():
    global insertedFromQueue
    global firstElemTest

    print('Usao u insertFromQueue()')
    while (not finishedReceiving or not len(chunkQueue)==0) and kill==False:
        if not len(chunkQueue)==0:
            firstElem = chunkQueue[0]
            if firstElem[0] == nextChunkToWrite:
                insertedFromQueue += 1
                writeBytesToFile(firstElem[1])
                chunkQueue.pop(0)
            else:
                firstElemTest = firstElem[0]


# Calling threads
transferThreads = []
startTime = datetime.now()
for streamPort in streamPorts:
    transfer_thread = threading.Thread(target=connectToStream, args=(streamPort,))
    transfer_thread.start()
    transferThreads.append(transfer_thread)

queueThread = threading.Thread(target=insertFromQueue)
queueThread.start()


# progressThread = threading.Thread(target=printCurrentProgress)
# progressThread.start()
# progressThread.join()

queueThread.join()

# Join threads
for tr_thread in transferThreads:
    tr_thread.join()

downloadedFile.close()

# Writing k ordinals to a file
# ordinalsFile = open('ordinals.txt', 'w')

# for co in chunkOrdinals:
#     ordinalsFile.write(str(co) + '\n')

# ordinalsFile.close()



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