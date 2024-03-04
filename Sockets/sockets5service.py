import logging
import os
import socket
from alicia_sockets.service import Service

logger = logging.getLogger("Ejercicio4Service")

CMD_CPU_LOAD = b"get_cpu_load"
CMD_DISK_USAGE = b"get_disk_usage"

class ServiceEj4(Service):
    def process_connection(self, connection: socket.socket, client_address: str):        
        logger.info(f"Origen de la conexión: {client_address}")
        while (data := connection.recv(1024)):
            logger.info(f"Recibido el mensaje: {data}")
            # data puede ser dos cosas:
            # b"get_cpu_load"
            # b"get_disk_usage <mount_point>"
            if data == CMD_CPU_LOAD:
                cpu_load = self.get_cpu_load()
                system_info = f"CPU: {cpu_load:.2f}%"
                connection.sendall(system_info.encode())
            elif data.startswith(CMD_DISK_USAGE):
                start_position = len(CMD_DISK_USAGE)
                mount_point = data[start_position:]
                disk_usage = self.get_disk_usage(mount_point.decode())
                connection.sendall(disk_usage.encode())
            else:
                connection.sendall(f"error: unknown command {data}".encode())

    # porcentaje de ocupación/uso de la cpu
    def get_cpu_load(self):
        # https://www.linuxhowtos.org/System/procstat.htm
        # user nice system idle
        with open('/proc/stat', 'r') as stat_file:
            cpu_data = stat_file.readline().split()[1:]
            total_cpu_time = sum(int(x) for x in cpu_data)
            idle_cpu_time = int(cpu_data[3])
            cpu_load = 100 - (idle_cpu_time /  total_cpu_time * 100)
        return cpu_load

    # ocupación del disco (particiones)
    def get_disk_usage(self, mount_point: str) -> str:
        all_lines = os.popen("df -h")
        header = all_lines.readline().strip()
        # comprehnsion expresion
        filtered_lines = [line.strip() for line in all_lines if line.strip().endswith(mount_point)]
        if len(filtered_lines) == 0:
            return "Error: Mount point not found"
        return "\n".join([header, filtered_lines[0]])


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    service = ServiceEj4()
    service.run()


if __name__ == "__main__":
    main()
