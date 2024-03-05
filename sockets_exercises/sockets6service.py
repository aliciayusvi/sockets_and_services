import socket
import os
import logging
from alicia_sockets.service import Service

logger = logging.getLogger("Ejercicio6Service")


class ServiceEj6(Service):
    def process_connection(self, connection: socket.socket, client_address: str):
        # morsa
        while len(data := connection.recv(1024)) > 0:
            # descodificación de bytes a string
            response = self.get_directory_contents(data.decode())
            connection.sendall(response.encode())

    def get_directory_contents(self, directory: str):
        logger.info(f"Directorio solicitado: {directory}")
        if os.path.isdir(directory):
            files = os.listdir(directory)
            return "\n".join(files)
        else:
            return "Directorio no encontrado"


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    service = ServiceEj6()
    service.run()


if __name__ == "__main__":
    main()
