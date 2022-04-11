import asyncio
from socket import create_connection
from _overlapped import NULL
import socket
import sys
import websockets


async def message():
    async with websockets.connect("ws://localhost:10000") as socket:
        msg = input("What do you want to send: ")
        await socket.send(msg)
        print(await socket.recv())

asyncio.get_event_loop().run_until_complete(message())


""""


class MyProtocol(asyncio.Protocol):

    def __init__(self, on_con_lost):
        self.transport = None
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        print("Received:", data.decode())

        # We are done: close the transport;
        # connection_lost() will be called automatically.
        self.transport.close()

    def connection_lost(self, exc):
        # The socket has been closed
        self.on_con_lost.set_result(True)


async def main():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()
    on_con_lost = loop.create_future()

    # Create a pair of connected sockets
    #rsock, wsock = socket.socketpair()

    # Register the socket to wait for data.
    transport, protocol = await loop.open_connection(
        lambda: MyProtocol(on_con_lost), host='127.0.0.1', port=10000)
    print("Connected with Server, Waiting for data from  server")
    # Simulate the reception of data from the network.
    #loop.call_soon(wsock.send, 'abc'.encode())

    try:
        await protocol.on_con_lost
    finally:
        transport.close()
        #wsock.close()

asyncio.run(main())




async def tcp_echo_client():
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 10000)

    #print(f'Send: {message!r}')
    #writer.write(message.encode())
    print('connected!!', file= sys.stderr)
    data = await reader.read(100)
    print(f'Received: {data.decode()}')

    #print('Close the connection')
    #writer.close()

asyncio.run(tcp_echo_client())



# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_name = sys.argv[1]
server_address = (server_name, 10000)
print('connecting to %s port %s' % server_address, file = sys.stderr) 
sock.connect(server_address)
print('connected!!', file= sys.stderr)
full_msg = ''
while True:
    
    data = sock.recv(1024)
    if len(data) <= 0:
        break
    print('received "%s"' % data, file = sys.stderr) 

print(full_msg)
sock.close()


async def message():
    
    #socket = create_connection('wss://127.0.0.1:52432', headers=NULL)
    async with websockets.connect('wss://localhost:52432') as socket:
        print(await socket.recv())
        #msg = input("What do you want to send: ")
        #await socket.send(msg)
    

asyncio.get_event_loop().run_until_complete(message())

# Send data
    message = 'This is the message.  It will be repeated.'
    print('sending "%s"' % message, file = sys.stderr) 
    sock.sendall(message)

    # Look for the response
    amount_received = 0
    amount_expected = len(message)
    
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        print('received "%s"' % data, file = sys.stderr) 
"""    