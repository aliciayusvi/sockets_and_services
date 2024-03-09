import socket
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..ftp_handler import FTPHandler
else:
    FTPHandler = Any

class FTPDisconnect(Exception):
    pass


class FTPCommand:
    def __init__(self, handler: FTPHandler) -> None:
        self.connection = handler.connection
        self.handler = handler

    def send_response(self, code: int, response: str) -> None:
        # formateo del mensaje de salida
        full_response = f"{code} {response}\r\n"
        self.connection.sendall(full_response.encode())

    def extract_arguments(self, command: str) -> str:
        keyword_len = len(self.__class__.__name__)
        command_args = command[keyword_len:].strip()
        return command_args

    def execute(self, command: str) -> None:
        self.send_response(200, f"Command {command} not implemented")


# excepción de los comandos no reconocidos
class FTPCommandUnknown(FTPCommand):
    def execute(self, command: str) -> None:
        self.send_response(500, f"Command {command} not recognized")

# excepción de los comandos no implementados
class FTPCommandUnsupported(FTPCommand):
    def execute(self, command: str) -> None:
        self.send_response(500, f"Command {command} not supported")
