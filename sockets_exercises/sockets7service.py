import logging
import socket

from alicia_sockets.service import Service

logger = logging.getLogger("Ejercicio7Service")

class ServiceEj7(Service):

    def process_connection(self, connection: socket.socket, client_address: str) -> None:
        logger.info(f"Origen de la conexión: {client_address}")
        while True:
            message = connection.recv(1024).decode()
            if not message:
                break
            logger.info(f"Mensaje de {client_address}: {message}")
            response = input("Respuesta: ")
            connection.sendall(response.encode())


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    service = ServiceEj7()
    service.run()


if __name__ == "__main__":
    main()
