import socket
from concurrent.futures import ThreadPoolExecutor
import logging
import argparse


logger = logging.getLogger("FTPService")


class MultiThreadedService:

    # número de hilos predeterminados de 10
    def __init__(self, address: str = "", port: int = 4444, max_threads=10) -> None:
        self.address = address
        self.port = port
        self.pool = ThreadPoolExecutor(thread_name_prefix="FTPService", max_workers=max_threads)

    def start(self):
        logger.info(f"Iniciando el servicio en {self.address}:{self.port}")
        logger.info(f"Usando un máximo de {self.pool._max_workers} hilos")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as service_socket:
            service_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            service_address = (self.address, self.port)
            service_socket.bind(service_address)
            service_socket.listen()
            logger.info("Esperando a la conexión...")
            while True:
                logger.info("Esperando a la conexión...")
                connection, client_address = service_socket.accept()
                self.pool.submit(self.process_connection, connection, client_address)

    # gestión del contexto
    def process_connection(self, connection: socket.socket, client_address: str):        
        with connection:
            self._process_connection(connection, client_address)

    # override this method to implement the service
    def _process_connection(self, connection: socket.socket, client_address: str):
        logger.info(f"Origen de la conexión: {client_address}")
        while (data := connection.recv(1024)):
            logger.info(f"Recibido el mensaje: {data}")
        logger.info(f"Cerrando conexion con: {client_address}")

    def run(self) -> None:
        try:
            self.start()
        except KeyboardInterrupt:
            logger.info(" Bye!")


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Servicio MultiThreaded")
    parser.add_argument("--address", "-a", default="0.0.0.0")
    parser.add_argument("--port", "-p", default=4444, type=int)
    parser.add_argument("--max-threads", "-m", default=10, type=int)
    args = parser.parse_args()

    service = MultiThreadedService(address=args.address, port=args.port, max_threads=args.max_threads)
    service.run()

if __name__ == "__main__":
    main()