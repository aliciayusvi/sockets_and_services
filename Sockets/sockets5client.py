import logging

from alicia_sockets.client import Client
from sockets5service import CMD_CPU_LOAD, CMD_DISK_USAGE


class ClientEj5(Client):
    def get_cpu_load(self) -> str:
        self.send(CMD_CPU_LOAD)
        response = self.receive()
        return response.decode()

    def get_disk_usage(self, mount_point: str) -> str:
        command = CMD_DISK_USAGE + f" {mount_point}".encode()
        self.send(command)
        response = self.receive()
        return response.decode()


def select_main_menu_option() -> str:
    print("Introduce 1 para ver la carga de la cpu")
    print("Introduce 2 para ver el uso de un volumen")
    print("Introduce 3 para salir")
    while (option := input()) not in {"1", "2", "3"}:
        pass
    return option


def main():
    logging.basicConfig(level=logging.INFO)
    with ClientEj5("server", 4444) as client:
        while (option := select_main_menu_option()):
            if option == "1":
                print(client.get_cpu_load())
            elif option == "2":
                mount_point = input("Introducir mountpoint: ")
                print(client.get_disk_usage(mount_point))
            elif option == "3":
                break


if __name__ == "__main__":
    main()
