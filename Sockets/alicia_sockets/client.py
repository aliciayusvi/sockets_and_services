import socket
import logging
from typing import Self

logger = logging.getLogger("AliciaClient")


class Client:
    # la firma incluye los parámetros entre paréntesis y el retorno tras la flecha
    def __init__(self, host: str = "server", port: int = 4444) -> None:
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self) -> None:
        service_address = (self.host, self.port)
        logger.info(f"Conectando a {self.host}:{self.port}")
        self.socket.connect(service_address)

    def send(self, data: bytes) -> bytes:
        self.socket.sendall(data)

    def receive(self, buffer_size: int = 1024) -> bytes:
        return self.socket.recv(buffer_size)

    def close(self) -> None:
        logger.info("Cerrando conexión")
        self.socket.close()

    # métodos que sirven para poder usar el cliente como un contexto
    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
