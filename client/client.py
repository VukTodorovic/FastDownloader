import socket

DEFAULT_BUFLEN = 1024

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server
server_address = ('localhost', 1337)
# print('connecting to {} port {}'.format(*server_address))
print(f'connecting to {server_address[0]} port {server_address[1]}')
print('--------------------------------')
sock.connect(server_address)


# Receive all available file names
data = sock.recv(DEFAULT_BUFLEN)
text = data.decode('utf-8')

print('\nAvailable files to download:\n',text)
print('--------------------------------')

# User input
fileName = input('Choose file name: ')

# Send the message to the server
sock.sendall(bytes(fileName, 'utf-8'))

# Receive and print the response from the server
data = sock.recv(DEFAULT_BUFLEN)
text = data.decode('utf-8')
print('Server response:', text)

# Make new file
file = open(fileName, 'wb')

# Write data to new file
file.write(data)

# Close the connection
sock.close()
