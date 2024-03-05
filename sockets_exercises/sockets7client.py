import logging
import socket
from typing import Self
from alicia_sockets.client import Client

logger = logging.getLogger("AliciaClient")


class ClientEj7(Client):
    def __init__(self, host: str = "localhost", port: int = 4444) -> None:
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self) -> None:
        service_address = (self.host, self.port)
        logger.info(f"Conectando a {self.host}:{self.port}")
        self.socket.connect(service_address)

    def send_message(self, message: str) -> None:
        encoded_message = message.encode()
        self.socket.sendall(encoded_message)

    def receive_message(self, buffer_size: int = 1024) -> str:
        data = self.socket.recv(buffer_size)
        return data.decode()

    def close(self) -> None:
        logger.info("Cerrando conexión")
        self.socket.close()

    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

def main():
    pass

if __name__ == "__main__":
    main()
