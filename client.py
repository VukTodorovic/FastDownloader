import socket

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server
server_address = ('localhost', 1337)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

while True:
    # Wait for user input
    message = input('Enter a message: ')

    # Send the message to the server
    sock.sendall(bytes(message, 'utf-8'))

    # Receive and print the response from the server
    # data = sock.recv(1024)
    # print('Received: {!r}'.format(data))

# Close the connection
sock.close()
