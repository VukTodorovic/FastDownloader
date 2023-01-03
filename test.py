import socket
import time

DEFAULT_BUFLEN = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', 3000))
sock.listen(1)

print('Server is listening on port 3000...')

connection, client_address = sock.accept()

try:
    print('connection from', client_address)

    file = open('index.html', 'r')
    html = file.read()
    file.close()

    data = connection.recv(DEFAULT_BUFLEN)
    request = data.decode('utf-8')
    print('Request: {}'.format(request))

    response = f"HTTP/1.1 200 OK\nContent-Type: text/html\nContent-Length: {len(html)}\n\n{html}"
    connection.sendall(response.encode())
finally:
    time.sleep(3)
    connection.close()