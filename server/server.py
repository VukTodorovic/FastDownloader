import socket
import sys

DEFAULT_BUFLEN = 1024
FILE_NAMES = ["test.txt", "CaleDoktorNauka.c", "test_slika.png"]

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 1337)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

# Wait for a connection
print('waiting for a connection')
connection, client_address = sock.accept()
# connection - socket object, client_address - ip adresa i port klijenta
try:
    print('connection from', client_address)

    # Send all available file names to the client
    startupMessage = ''
    x = 1
    for filename in FILE_NAMES:
        startupMessage += str(x) + ')' + filename + '\n'
        x+=1

    connection.sendall(bytes(startupMessage, 'utf-8'))
    

    # Receives client input
    data = connection.recv(DEFAULT_BUFLEN)
    filename = data.decode('utf-8')
    print('received {}'.format(filename))
    
    # Checks if selected filename exists on the server
    if filename not in FILE_NAMES:
        connection.sendall(bytes('Wrong input', 'utf-8'))
        sys.exit()

    print('sending file {} to the client'.format(filename))

    # Open the file in text mode
    file = open(filename, 'rb')

    # Read all bytes of the file into a variable
    fileBytes = file.read()

    # Close the file
    file.close()

    connection.sendall(fileBytes)
        
finally:
    # Clean up the connection
    connection.close()
