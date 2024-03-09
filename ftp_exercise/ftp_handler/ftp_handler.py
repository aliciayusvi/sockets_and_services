import logging
import socket

from .commands import (
    FTPCommand,
    FTP_IMPLEMENTED_COMMANDS,
    FTP_NOT_IMPLEMENTED_COMMANDS,
    FTPCommandUnknown,
    FTPCommandUnsupported,
    FTPDisconnect
)

logger = logging.getLogger("FTPHandler")

# gestiona una lista de comandos
class FTPHandler:

    def __init__(self, connection: socket.socket, local_address: str) -> None:
        self.connection = connection
        self.data_connection: socket.socket | None = None
        # diccionario de comandos
        self.commands: dict[str, type[FTPCommand]] = {}
        self.register_commands(FTP_IMPLEMENTED_COMMANDS)
        for command in FTP_NOT_IMPLEMENTED_COMMANDS:
            self.register_unsupported_command(command)

    def register_commands(self, commands: list[type[FTPCommand]]) -> None:
        for command in commands:
            self.commands[command.__name__] = command
    
    def register_unsupported_command(self, command: str) -> None:
        self.commands[command] = FTPCommandUnsupported

    # petición y ejecución de comandos
    def execute(self) -> None:
        try:
            logger.info("Cliente conectado")
            self.connection.sendall('220 Welcome!\r\n'.encode())
            while True:
                logger.info("Waiting for command...")
                command = self.get_command()
                logger.info(f"Command received: {command}")
                keyword = self.get_keyword(command)
                # selección de un valor del diccionario de comandos
                ftp_command_class = self.commands.get(keyword, FTPCommandUnknown)
                # instanciar el objeto de la clase asociada a la keyword
                ftp_command = ftp_command_class(self)
                # ejecutar el comando execute
                ftp_command.execute(command)
        except FTPDisconnect:
            logger.info("Disconnected client")

    def get_command(self) -> str:
        command = self.connection.recv(1024).decode()
        return command

    def get_keyword(self, command: str) -> str:
        command = command.strip()
        tokens = command.split()
        if len(tokens) == 0:
            raise ValueError("Empty command")
        keyword = tokens[0].upper()
        return keyword

    def validate_keyword(self, keyword: str) -> bool:
        return keyword in self.commands
