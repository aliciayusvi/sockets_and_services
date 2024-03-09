import socket
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..ftp_handler import FTPHandler
else:
    FTPHandler = Any

class FTPDisconnect(Exception):
    pass


class FTPCommand:
    COMMAND: str = "__BASE_COMMAND__"
    def __init__(self, handler: FTPHandler) -> None:
        self.connection = handler.connection
        self.handler = handler

    def send_response(self, code: int, response: str) -> None:
        # formateo
        full_response = f"{code} {response}\r\n"
        self.connection.sendall(full_response.encode())

    def extract_arguments(self, command: str) -> str:
        keyword_len = len(self.COMMAND)
        command_args = command[keyword_len:].strip()
        return command_args

    def execute(self, command: str) -> None:
        self.send_response(200, f"Command {command} not implemented")


class FTPCommandUnknown(FTPCommand):
    COMMAND = "UNKNOWN"
    def execute(self, command: str) -> None:
        self.send_response(500, f"Command {command} not recognized")