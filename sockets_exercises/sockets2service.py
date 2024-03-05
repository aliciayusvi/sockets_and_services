import socket
import time
import logging

from alicia_sockets.service import Service

logger = logging.getLogger("Ejercicio2Service")


class ServiceEj2(Service):

    def process_connection(self, connection: socket.socket, client_address: str):
        logger.info(f"Origen de la conexión: {client_address}")
        current_time = time.ctime(time.time())
        logger.info(f"Hora de conexión: {current_time}")
        connection.sendall(current_time.encode())
        logger.info(f"Conexión con el cliente {client_address} finalizada")


# programa principal
def main():
    logging.basicConfig(level=logging.INFO)
    service = ServiceEj2()
    service.run()


if __name__ == "__main__":
    main()
