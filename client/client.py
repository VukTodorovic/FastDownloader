import socket
import sys

DEFAULT_BUFLEN = 1024

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server
server_address = ('localhost', 1337)
# print('connecting to {} port {}'.format(*server_address))
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
print(f'Server response:\n{response}')

# If file doesn't exist on server
if response == 'Wrong input':
    sock.close()
    sys.exit()

# If request is accepted process connection requirements


# Close the connection
sock.close()







# Write bytes to new file
# file = open(fileName, 'wb')
# file.write(data)