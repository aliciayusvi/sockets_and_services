import logging

from alicia_sockets.client import Client


class ClientEj2(Client):
    def receive(self) -> bytes:
        return self.socket.recv(1024)


def main():
    logging.basicConfig(level=logging.INFO)
    # los parámetros se pueden omitir porque son los predeterminados
    with ClientEj2("server", 4444) as client:
        data = client.receive()
        print(data.decode())


# lo primero en la ejecución
if __name__ == "__main__":
    main()
