import socket
import sys

connectSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serverSocket = ('localhost', 8000)
print >> sys.stderr, 'connecting to %s port %s' % serverSocket
connectSocket.connect(serverSocket)

try:
    message = 'This is the message. It will be repeated.'
    print >> sys.stderr, 'sending "%s"' % message
    connectSocket.sendall(message)

    received = 0
    expected = len(message)

    while(received < expected):
        data = connectSocket.recv(16)
        received += len(data)
        print >> sys.stderr, 'received "%s"' % dat

finally:
    print >> sys.stderr, 'closing socket'
    connectSocket.close()
