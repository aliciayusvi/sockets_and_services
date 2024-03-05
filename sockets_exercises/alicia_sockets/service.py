import socket
import logging

logger = logging.getLogger("AliciaService")


class Service:

    # init sirve de constructor
    def __init__(self, address: str = "", port: int = 4444) -> None:
        # self equivale a this
        self.address = address
        self.port = port

    # inicio del servicio
    def start(self):
        # gestor de contextos para sustituir al try-finally
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as service_socket:
            service_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # ip y puerto del servidor que escucha
            service_address = (self.address, self.port)
            # asociación del socket al puerto
            service_socket.bind(service_address)
            service_socket.listen()
            logger.info("Esperando a la conexión...")
            while True:
                self.process_connections(service_socket)

    def process_connections(self, service_socket: socket.socket) -> None:
        connection, client_address = service_socket.accept()
        with connection:
            self.process_connection(connection, client_address)

    # para hacer override en las clases derivadas
    def process_connection(self, connection: socket.socket, client_address: str):
        logger.info(f" Origen de la conexión: {client_address}")

    def run(self) -> None:
        try:
            self.start()
        except KeyboardInterrupt:
            # cierre del programa
            logger.info(" Bye!")
