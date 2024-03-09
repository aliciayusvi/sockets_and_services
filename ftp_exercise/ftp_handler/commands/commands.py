import grp
import logging
import os
import pwd
import time
from pathlib import Path

from .base import FTPCommand, FTPDisconnect
from .connection_commands import PASV, EPSV


logger = logging.getLogger("FTP_COMMANDS")


FEATURES = ["UTF8", "EPSV", "PASV"]


class QUIT(FTPCommand):
    def execute(self, _: str) -> None:
        self.send_response(221, "Bye!")
        # lanzar una excepción
        raise FTPDisconnect()


class PWD(FTPCommand):
    def execute(self, _: str) -> None:
        current_dir = os.getcwd()
        self.send_response(257, f'"{current_dir}"')


# string del directorio como parámetro
class CWD(FTPCommand):
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


class USER(FTPCommand):
    def execute(self, command: str) -> None:
        user = self.extract_arguments(command)
        self.send_response(331, f"User {user} OK. Password required")


class PASS(FTPCommand):
    def execute(self, command: str) -> None:
        password = self.extract_arguments(command)
        self.send_response(230, f"Password correct")


class SYST(FTPCommand):
    def execute(self, _: str) -> None:
        self.send_response(215, "UNIX Type: L8")


class FEAT(FTPCommand):
    def execute(self, _: str) -> None:
        message_list = ["211-Features"] + [f" {feature}" for feature in FEATURES] + [""]
        message ="\r\n".join(message_list)
        self.connection.sendall(message.encode())
        self.send_response(211, "End")


class LIST(FTPCommand):
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
        if self.handler.data_connection is None:
            self.send_response(425, "Use EPSV first.")
            return
        files = os.listdir()
        self.send_response(150, "List transfer started")
        send_socket, address = self.handler.data_connection.accept()
        with send_socket:
            logger.info(f"Passive connection from {address}")
            for filename in files:
                formatted_file = self.format_file(filename)
                send_socket.sendall(formatted_file.encode())
        self.handler.data_connection = None
        self.send_response(226, "List transfer done")


# get (para bajar archivos) es retrieve
class RETR(FTPCommand):
    def execute(self, command: str) -> None:
        if self.handler.data_connection is None:
            self.send_response(425, "Use EPSV first.")
            return
        filename = self.extract_arguments(command)
        filepath = Path(filename)
        if not filepath.is_file():
            self.send_response(550, f"File {filename} not found")
            return

        self.send_response(150, f"Opening BINARY mode data connection for {filename}")
        send_socket, address = self.handler.data_connection.accept()
        with send_socket, open(filename, "rb") as file:
            logger.info(f"Passive connection from {address}")
            send_socket.sendfile(file)

        self.handler.data_connection = None
        self.send_response(226, f"Transfer complete for {filename}")


class TYPE(FTPCommand):
    def execute(self, command: str) -> None:
        type_ = self.extract_arguments(command)
        if type_ == "I":
            self.send_response(200, "Type set to I")
        else:
            self.send_response(504, "Type not implemented")


# put (para subir archivos) es stor
class STOR(FTPCommand):
    def execute(self, command: str) -> None:
        # nos aseguramos de que hay un socket escuchando
        if self.handler.data_connection is None:
            self.send_response(425, "Use EPSV first.")
            return
    
        # nombre y ruta de destino
        filename = self.extract_arguments(command)
        filepath = Path(filename)
        if not filepath.parent.exists():
            self.send_response(550, f"Directory {filepath.parent} not found")
            return

        self.send_response(150, f"Opening BINARY mode data connection for {filename}")
        recv_socket, address = self.handler.data_connection.accept()
        with recv_socket, open(filename, "wb") as file:
            logger.info(f"passive connection from {address}")
            while (data := recv_socket.recv(1024)):
                file.write(data)
            logger.info("File received")
            
        self.handler.data_connection = None
        self.send_response(226, f"Transfer complete for {filename}")


FTP_IMPLEMENTED_COMMANDS = [
    CWD,
    PWD,
    LIST,
    QUIT,
    USER,
    PASS,
    SYST,
    FEAT,
    EPSV,
    PASV,
    RETR,
    TYPE,
    STOR
]


FTP_NOT_IMPLEMENTED_COMMANDS = [
    "EPRT",
    "PORT",
    "PUT",
]
