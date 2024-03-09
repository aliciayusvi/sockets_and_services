import socket
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger("MultithreadedService")

# creación de la conexión para los comandos
class MultiThreadedService:

    # número de hilos predeterminados de 10
    def __init__(self, address: str = "", port: int = 4444, max_threads=10) -> None:
        self.address = address
        self.port = port
        # reserva de ejecutores en hilos
        self.pool = ThreadPoolExecutor(thread_name_prefix="MultithreadedService", max_workers=max_threads)

    def start(self):
        logger.info(f"Starting the service in {self.address}:{self.port}")
        # máximo de hilos concurrentes
        logger.info(f"Using a maximum of {self.pool._max_workers} threads")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as service_socket:
            service_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            service_address = (self.address, self.port)
            service_socket.bind(service_address)
            service_socket.listen()
            logger.info("Waiting for connections...")
            while True:
                connection, client_address = service_socket.accept()
                # envío de tarea a la cola del pool de ejecutores
                self.pool.submit(self.process_connection, connection, client_address)

    # gestión del contexto
    def process_connection(self, connection: socket.socket, client_address: str):        
        #with connection:
        self._process_connection(connection, client_address)

    # override this method to implement the service
    def _process_connection(self, connection: socket.socket, client_address: str):
        logger.info(f"Connection origin: {client_address}")
        while (data := connection.recv(1024)):
            logger.info(f"Message received: {data}")
        logger.info(f"Closing connection with {client_address}")

    # este es el punto de entrada del servicio (donde arranca)
    def run(self) -> None:
        try:
            self.start()
        except KeyboardInterrupt:
            # ctrl + C
            logger.info(" Bye!")
