import socket
import sys

connectSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serverSocket = ('localhost', 8000)
print >> sys.stderr, 'initializing server socket on %s port %s' % serverSocket
connectSocket.bind(serverSocket)

connectSocket.listen(5)

while True:
    print >> sys.stderr, 'awaiting connection'
    (clientSocket, clientAddress) = connectSocket.accept()

    try:
        print >> sys.stderr, 'connection from', clientAddress

        while True:
            data = clientSocket.recv(16)
            print >> sys.stderr, 'received "%s"' % data

            if data:
                print >> sys.stderr, 'sending data back to client'
                clientSocket.sendall(data)
            else:
                print >> sys.stderr, 'no more data from', clientAddress
                break

    finally:
        clientSocket.close()
