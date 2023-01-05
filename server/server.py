import socket
import threading
import sys

DEFAULT_BUFLEN = 1024
MAX_CLIENTS = 10
FILE_NAMES = ["test.txt", "CaleDoktorNauka.c", "test_slika.png"]

killSwitch = 0 # Just for testing


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
        client_socket.sendall('ACCEPTED'.encode())
        # print(f'sending file {filename} to the client')

        # # Read all bytes into variable
        # file = open(filename, 'rb')
        # fileBytes = file.read()
        # file.close()

        # # Send file bytes over socket
        # client_socket.sendall(fileBytes)
    


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