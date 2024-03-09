import socket
import logging
from .base import FTPCommand

logger = logging.getLogger("FTP_COMMANDS")


class NoAvailablePorts(Exception):
    pass


# gestión del socket de la conexión de datos
class OpenDataConnection(FTPCommand):
    # devuelve un socket si existe
    def get_free_socket(self) -> socket.socket:
        # iteración en un rango de puertos empezando por el 2024
        for port in range(1024, 65536):
            try:
                # creación de un socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # asignación de socket al puerto
                #s.bind((self.handler.local_address, port))
                s.bind(("0.0.0.0", port))
                s.listen()
                return s
            except OSError as e:
                # cierre del socket
                s.close()
        raise NoAvailablePorts

    def update_data_connection(self) -> int:
        if self.handler.data_connection is not None:
            logger.info(f"closing previous connection: {self.handler.data_connection.getsockname()}")
            self.handler.data_connection.close()
        
        data_socket = self.get_free_socket()
        self.handler.data_connection = data_socket
        # sockname is a tuple that looks like: ('0.0.0.0', 1234)
        socket_port = data_socket.getsockname()[1]
        return socket_port


# comando para la conexión pasiva extendida
class EPSV(OpenDataConnection):
    def execute(self, _: str) -> None:
        try:
            port = self.update_data_connection()
            self.send_response(229, f"Entering Extended Passive Mode (|||{port}|).")
        except NoAvailablePorts:
            logger.error("No available ports")
            self.send_response(421, "Service not available, closing control connection.")


# comando para la conexión pasiva
class PASV(OpenDataConnection):    

    # gestión de la creación del socket en data_conecction (bind)
    def execute(self, _: str) -> None:
        try:
            port = self.update_data_connection()
        except NoAvailablePorts:
            logger.error("No available ports")
            self.send_response(421, "Service not available, closing control connection.")
            return

        address = [127, 0, 0, 1]
        encoded_port = [port // 256, port % 256]
        all_values = address + encoded_port
        self.send_response(227, f"Entering Passive Mode ({','.join(map(str, all_values))}).")
