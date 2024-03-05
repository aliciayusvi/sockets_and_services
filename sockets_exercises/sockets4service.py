import socket
import time
import logging
from alicia_sockets.service import Service

logger = logging.getLogger("Ejercicio4Service")


class ServiceEj4(Service):
    def process_connection(self, connection: socket.socket, client_address: str):        
        logger.info(f"Origen de la conexión: {client_address}")
        # mientras el valor asignado a data sea verdadero (no este vacío)
        while (data := connection.recv(1024)):
            # información sobre que se recibió una petición de hora
            logger.info(f"Recibido el mensaje: {data}")
            if data == b"get_time":
                current_time = f"{time.ctime(time.time())}"
                # codificación de un string
                logger.info(f"Enviando: {current_time}")
                connection.sendall(current_time.encode())
            else:
                logger.warning(f"Comando no reconocido: {data}")
                connection.sendall("Comando no reconocido".encode())


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    service = ServiceEj4()
    service.run()


if __name__ == "__main__":
    main()
