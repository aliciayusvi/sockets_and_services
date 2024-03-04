import logging
import socket

logger = logging.getLogger("Ejercicio7Service")


class ServiceEj7:
    def __init__(self, address: str = "", port: int = 4444) -> None:
        self.address = address
        self.port = port

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as service_socket:
            service_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            service_address = (self.address, self.port)
            service_socket.bind(service_address)
            service_socket.listen()
            logger.info("Esperando a la conexión...")
            while True:
                self.process_connections(service_socket)

    def process_connections(self, service_socket: socket.socket) -> None:
        connection, client_address = service_socket.accept()
        with connection:
            self.process_connection(connection, client_address)

    def process_connection(self, connection: socket.socket, client_address: str) -> None:
        logger.info(f"Origen de la conexión: {client_address}")
        while True:
            message = connection.recv(1024).decode()
            if not message:
                break
            logger.info(f"Mensaje de {client_address}: {message}")
            response = input("Respuesta: ")
            connection.sendall(response.encode())

    def run(self) -> None:
        try:
            self.start()
        except KeyboardInterrupt:
            logger.info("Bye!")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    service = ServiceEj7()
    service.run()


if __name__ == "__main__":
    main()
