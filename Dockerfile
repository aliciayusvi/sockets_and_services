FROM python:3.12

RUN apt update && apt install -y iproute2 netcat-openbsd nmap iputils-ping dnsutils
