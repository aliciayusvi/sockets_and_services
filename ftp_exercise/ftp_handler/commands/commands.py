import grp
import os
import pwd
import time
from pathlib import Path

from .base import FTPCommand, FTPDisconnect


class FTPCommandQUIT(FTPCommand):
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


FTP_IMPLEMENTED_COMMANDS = [
    FTPCommandCWD,
    FTPCommandPWD,
    FTPCommandLIST,
    FTPCommandQUIT,
    FTPCommandUSER,
    FTPCommandPASS,
    FTPCommandSYST,
    FTPCommandFEAT,
]

FTP_NOT_IMPLEMENTED_COMMANDS = [
    "EPSV",
    "EPRT",
    "PASV",
]