# un módulo es un archivo y un paquete es una carpeta
import argparse
import logging
import socket
from .service import MultiThreadedService
from .ftp_handler import FTPHandler

logger = logging.getLogger("FTPService")

class FTPService(MultiThreadedService):

    def _process_connection(self, connection: socket.socket, client_address: str):
        logger.info(f"Connection from {client_address}")
        ftp_handler = FTPHandler(connection)
        ftp_handler.execute()


def main():
    logging.basicConfig(level=logging.INFO)

    # indicar el valor de los parámetros para pasar los datos de la configuración
    # ejemplo: python service.py -a 0.0.0.0 -p 21
    parser = argparse.ArgumentParser(description="MultiThreaded Service")
    parser.add_argument("--address", "-a", default="0.0.0.0")
    parser.add_argument("--port", "-p", default=4444, type=int)
    parser.add_argument("--max-threads", "-m", default=10, type=int)
    args = parser.parse_args()

    service = FTPService(address=args.address, port=args.port, max_threads=args.max_threads)
    service.run()

if __name__ == "__main__":
    main()
