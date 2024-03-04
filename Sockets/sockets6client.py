import logging

from alicia_sockets.client import Client


class ClientEj6(Client):
    def get_directory_content(self, directory: str):
        self.socket.sendall(directory.encode())
        # 4K
        files = self.socket.recv(4096)
        return files.decode()


def main():
    logging.basicConfig(level=logging.INFO)
    with ClientEj6("server", 4444) as client:
        while (directory := input("Introduce un directorio (vacío para salir): ")):
            files = client.get_directory_content(directory)
            print(files)


if __name__ == "__main__":
    main()
