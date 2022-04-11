import socket 
import argparse

parser = argparse.ArgumentParser(description = "This is the client for the multi threaded socket server!")
parser.add_argument('--host', metavar = 'host', type = str, nargs = '?', default = "localhost")
parser.add_argument('--port', metavar = 'port', type = int, nargs = '?', default = 10000)
args = parser.parse_args()

print(f"Connecting to server: {args.host} on port: {args.port}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sck:
    try:
        sck.connect((args.host, args.port))
    except Exception as e:
        raise SystemExit(f"We have failed to connect to host: {args.host} on port: {args.port}, because: {e}")

    while True:
        msg = input("Ready to receive message! ")
        data = sck.recv(1024)
        print(f"The server's response was: {data.decode()}")
        
"""
 sck.sendall(msg.encode('utf-8'))
        if msg =='exit':
            print("Client is saying goodbye!")
            break
"""