import logging

from alicia_sockets.client import Client


class ClientEj4(Client):
    def get_time(self):
        self.socket.sendall(b"get_time")
        # 1K
        data = self.socket.recv(1024)
        return data.decode()


def main():
    logging.basicConfig(level=logging.INFO)
    with ClientEj4() as client:
        while (input("Desea obtener la hora? (s/n): ").lower() == "s"):
            print(f"Hora actual: {client.get_time()}")


if __name__ == "__main__":
    main()
