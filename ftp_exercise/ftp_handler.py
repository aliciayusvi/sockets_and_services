import grp
import logging
import os
import pwd
import socket
import time
from pathlib import Path

logger = logging.getLogger("FTPHandler")

class FTPDisconnect(Exception):
    pass


class FTPCommand:
    COMMAND: str = "UNKNOWN"
    def __init__(self, connection: socket.socket) -> None:
        self.connection = connection

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


class FTPHandler:

    def __init__(self, connection: socket.socket) -> None:
        self.connection = connection
        
        # la clave es un string y el valor es una función
        self.commands: dict[str, type[FTPCommand]] = {}
        self.register_commands([
            FTPCommandQuit,  # quit
            FTPCommandPWD,  # print working directory
            FTPCommandCWD,  # change working directory
            FTPCommandUSER,  # user
            FTPCommandPASS,  # password
            FTPCommandSYST,  # system
            FTPCommandFEAT,  # features
            FTPCommandLIST,  # list
        ])
        self.register_unsupported_command("EPSV")
        self.register_unsupported_command("PORT")
        self.register_unsupported_command("PASV")

    def register_commands(self, commands: list[type[FTPCommand]]) -> None:
        for command in commands:
            self.commands[command.COMMAND] = command
    
    def register_unsupported_command(self, command: str) -> None:
        self.commands[command] = FTPCommandUnknown

    def execute(self) -> None:
        try:
            logger.info("Cliente conectado")
            self.connection.sendall('220 Welcome!\r\n'.encode())
            while True:
                logger.info("Waiting for command...")
                command = self.get_command()
                logger.info(f"Command received: {command}")
                keyword = self.get_keyword(command)
                #if not self.validate_keyword(keyword):
                #    self.connection.sendall("500 Syntax error, command unrecognized\r\n".encode())
                #    continue

                # selección de un valor del diccionario de comandos
                ftp_command_class = self.commands.get(keyword, FTPCommand)
                # instanciar el objeto de la clase asociada a la keyword
                ftp_command = ftp_command_class(self.connection)
                # ejecutar el comando execute
                ftp_command.execute(command)
        except FTPDisconnect:
            logger.info("Disconnected client")
            pass

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


class FTPCommandQuit(FTPCommand):
    COMMAND = "QUIT"

    def execute(self, _: str) -> None:
        self.send_response(221, "Bye!")
        raise FTPDisconnect()


class FTPCommandPWD(FTPCommand):
    COMMAND = "PWD"
    def execute(self, _: str) -> None:
        current_dir = os.getcwd()
        self.send_response(257, f'"{current_dir}"')


# string del directorio como parámetro
class FTPCommandCWD(FTPCommand):
    COMMAND = "CWD"
    def execute(self, command: str) -> None:
        new_dir = self.extract_arguments(command)
        path = Path(new_dir)
        # comprobación de que hay una ruta válida
        if new_dir == "":
            self.send_response(550, "No directory provided")
            return
        if not path.is_dir():
            self.send_response(550, f"Directory {new_dir} doesn't exist")
            return
        os.chdir(new_dir)
        self.send_response(250, f"Directory changed to {new_dir}")


class FTPCommandUSER(FTPCommand):
    COMMAND = "USER"
    def execute(self, command: str) -> None:
        user = self.extract_arguments(command)
        self.send_response(331, f"User {user} OK. Password required")


class FTPCommandPASS(FTPCommand):
    COMMAND = "PASS"
    def execute(self, command: str) -> None:
        password = self.extract_arguments(command)
        self.send_response(230, f"Password correct")


class FTPCommandSYST(FTPCommand):
    COMMAND = "SYST"
    def execute(self, _: str) -> None:
        self.send_response(215, "UNIX Type: L8")


class FTPCommandFEAT(FTPCommand):
    COMMAND = "FEAT"
    def execute(self, _: str) -> None:
        self.connection.sendall("211-Features:\r\n UTF8\r\n".encode())
        self.send_response(211, "End")


class FTPCommandLIST(FTPCommand):
    COMMAND = "LIST"
    def format_file(self, filename):
        file_stats = os.stat(filename)
        fullmode = "rwxrwxrwx"
        mode = ""
        for i in range(9):
            mode += ((file_stats.st_mode >> (8 - i)) & 1) and fullmode[i] or "-"
        dir_flag = os.path.isdir(filename) and "d" or "-"
        permissions = dir_flag + mode
        owner_uid = file_stats.st_uid
        owner = pwd.getpwuid(file_stats.st_uid).pw_name
        group = grp.getgrgid(file_stats.st_gid).gr_name
        file_time = time.strftime("%b %d %H:%M", time.gmtime(file_stats.st_mtime))
        file_size = str(file_stats.st_size)
        base_name = os.path.basename(filename)
        data = [permissions, owner_uid, owner, group, file_size, file_time, base_name]
        formatted_data = "\t".join(str(x) for x in data) + "\r\n"
        return formatted_data

    def execute(self, _: str) -> None:
        # listado de archivos en el directorio actual
        files = os.listdir()
        self.send_response(150, "List transfer started")
        for filename in files:
            formatted_file = self.format_file(filename)
            self.connection.sendall(formatted_file.encode())
        self.send_response(226, "List transfer done")


class FTPCommandUnknown(FTPCommand):
    COMMAND = "UNKNOWN"
    def execute(self, command: str) -> None:
        self.send_response(500, f"Command {command} not recognized")

# comandos a implementar
#"get": FTPCommand,
#"put": FTPCommand,
