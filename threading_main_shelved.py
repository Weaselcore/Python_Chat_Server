"""
A server that can serve multiple clients through websockets
"""

from socket import AF_INET, SOL_SOCKET, SO_REUSEADDR, socket, SOCK_STREAM
from threading import Thread
import time
from person import Person


# GLOBAL VARIABLES
persons_list = []

# GLOBAL CONSTANTS
HOST = ''
PORT = 5504
BUFFERSIZE = 512
ADDRESS = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
SERVER.bind(ADDRESS)


def accept_incoming_connections():
    """
    Allows for handling of clients that connect to the server
    """

    msg = 'initialise'
    byte = bytes(msg, 'utf-8')
    print(byte)

    while True:
        try:

            client, client_address = SERVER.accept()
            person = Person(client, client_address)
            persons_list.append(person)
            print(
                f"{client_address} has connected at {time.strftime('%H:%M:%S - %d/%m/%Y', time.localtime())}.")
            greeting = "Greetings, type your name and press enter."
            client.send(bytes(greeting, 'utf8'))
            Thread(target=handle_client, args=(person,)).start()
        except Exception as e:
            print("[CONNECTION EXCEPTION]", e)
            break
    print("[FATAL] Server crashed!")


def handle_client(person):
    """
    This function handles one client at a time.
    """

    client = person.client
    name = client.recv(BUFFERSIZE).decode("utf8")
    person.set_name(name)

    welcome = f'Welcome {name}! If you want to quit, type {quit} to exit'
    client.send(bytes(welcome, 'utf-8'))

    msg = f'{name} has joined the chat!'
    broadcast(msg, "")

    while True:
        name = client.recv(BUFFERSIZE).decode("utf8")
        if msg != bytes("{quit}", "utf8"):
            broadcast(msg, name)
            print(f"{name}: ", msg)
        else:
            client.close()
            persons_list.remove(person)
            broadcast(f'{client.name} has left the chat', "")
            print(f"[DISCONNECTED] {name} disconnected")
            break


def broadcast(msg, name):
    """
    Broadcasts a message to all clients.
    """
    for person in persons_list:
        client = person.client
        try:
            client.send(bytes(f'{name}: {msg}', 'utf-8'))
        except Exception as e:
            print("[BROADCAST EXCEPTION]", e)


# if __name__ == "__main__":
#     SERVER.listen(5)
#     print("[Started] Waiting for connection")
#     ACCEPT_THREAD = Thread(target=accept_incoming_connections)
#     ACCEPT_THREAD.start()
#     ACCEPT_THREAD.join()
#     SERVER.close()
