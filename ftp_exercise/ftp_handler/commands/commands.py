import grp
import logging
import os
import pwd
import socket
import time
from pathlib import Path

from .base import FTPCommand, FTPDisconnect

logger = logging.getLogger("FTP_COMMANDS")


FEATURES = ["UTF8", "EPSV"]

class NoAvailablePorts(Exception):
    pass


class QUIT(FTPCommand):
    COMMAND = "QUIT"

    def execute(self, _: str) -> None:
        self.send_response(221, "Bye!")
        raise FTPDisconnect()


class PWD(FTPCommand):
    COMMAND = "PWD"
    def execute(self, _: str) -> None:
        current_dir = os.getcwd()
        self.send_response(257, f'"{current_dir}"')


# string del directorio como parámetro
class CWD(FTPCommand):
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


class USER(FTPCommand):
    COMMAND = "USER"
    def execute(self, command: str) -> None:
        user = self.extract_arguments(command)
        self.send_response(331, f"User {user} OK. Password required")


class PASS(FTPCommand):
    COMMAND = "PASS"
    def execute(self, command: str) -> None:
        password = self.extract_arguments(command)
        self.send_response(230, f"Password correct")


class SYST(FTPCommand):
    COMMAND = "SYST"
    def execute(self, _: str) -> None:
        self.send_response(215, "UNIX Type: L8")


class FEAT(FTPCommand):
    COMMAND = "FEAT"
    def execute(self, _: str) -> None:
        message_list = ["211-Features"] + [f" {feature}" for feature in FEATURES] + [""]
        message ="\r\n".join(message_list)
        self.connection.sendall(message.encode())
        self.send_response(211, "End")


class LIST(FTPCommand):
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


class EPSV(FTPCommand):
    COMMAND="EPSV"
    # returns a socket if exist
    def get_free_socket(self) -> socket.socket:
        # iterate over a range of port numbers starting from 1024
        for port in range(1024, 65536):
            try:
                # create a socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # attempt to bind the socket to the current port
                s.bind(("0.0.0.0", port))
                s.listen()
                # if successful, return the socket
                return s
            except OSError as e:
                # if the port is already in use, close the socket and continue iterating
                s.close()
        raise NoAvailablePorts

    def update_data_connection(self) -> int:
        if self.handler.data_connection is not None:
            self.handler.data_connection.close()
        
        data_socket = self.get_free_socket()
        self.handler.data_connection = data_socket
        # sockname is a tuple that looks like: ('0.0.0.0', 1234)
        socket_port = data_socket.getsockname()[1]
        return socket_port

    def execute(self, _: str) -> None:
        try:
            port = self.update_data_connection()
            self.send_response(229, f"Entering Extended Passive Mode (|||{port}|).")
        except NoAvailablePorts:
            logger.error("No available ports")
            self.send_response(421, "Service not available, closing control connection.")


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
]


FTP_NOT_IMPLEMENTED_COMMANDS = [
    "EPRT",
    "PASV",
    "PORT",
]
