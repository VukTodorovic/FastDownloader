# FastDownloader

## Description
Project features fast download of files from server through multiple concurrent TCP connections. Server can serve multiple clients at the same time. Client and Server are both implemented in Python.

## Workflow
- Client handshakes with server that is listening on port 1337
- Server responds with available files in format:
```
1) file1.ext
2) file2.ext
3) file3.ext
...
```
- Client sends name of the file wanted for download
- Server processes the request:
    - Server validates the input and in case of wrong input responds with:
    ```
    WRONG_INPUT
    ```
    - Server calculates how many TCP streams are required depending on file size
    - Server opens calculated amount of sockets using ports chosen randomly from free ports pool
    - Server responds with connection requirements in following format:
    ```
    ACCEPTED N M PORT_1 PORT_2 ... PORT_N-1 PORT_N
    ```
    where: <br />
    **ACCEPTED** means that request is accepted <br />
    **N** is number of ports that the client need to connect to <br />
    **M** is number of data chunks that will be transmitted <br />
    **PORT_1 ... PORT_N** represents exact port numbers for connection <br />
    **Note**: Chunk size is constant 1024 bytes 
- Client creates N number of threads that connect to N ports provided by server
- Server is reading a file and sending chunks concurrently over N TCP streams in following format:
```
K BYTES
```
where: <br />
**K** is ordinal number of data chunk <br />
**BYTES** is a chunk of bytes that is being transmitted
- Client gets chunks of thata from server and writes them to a file in correct order. 
- When the file is fully downloaded all sockets are closed and client program is terminated

## Development notes
- Server could send file using round robin algorithm but using threads only for *socket.sendall()* since it's a bloking function
- Formula: M = size_in_bytes / 1000 + 1
- Num of streams: 1 - 8
- Calculate num of streams:
```
1. < 10MB
2. 10MB - 50MB
3. 50MB - 100MB
5. 100MB - 250MB
6. 400MB - 700MB
7. 700MB - 1GB
8. > 1GB
```