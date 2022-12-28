import socket

DEFAULT_BUFLEN = 1024

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server
server_address = ('localhost', 1337)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)


# Receive all available file names
data = sock.recv(DEFAULT_BUFLEN)
text = data.decode('utf-8')

print('Available files to download:\n{}'.format(text))
print('--------------------------------')

# User input
fileName = input('Choose file name: ')

# Send the message to the server
sock.sendall(bytes(fileName, 'utf-8'))

# Receive and print the response from the server
data = sock.recv(DEFAULT_BUFLEN)
print('Received: {}'.format(data))

# Make new file
file = open(fileName, 'wb')

# Write data to new file
file.write(data)

# Close the connection
sock.close()
