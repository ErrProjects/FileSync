from fs_server import FileSyncServer
import socket

server = FileSyncServer((socket.gethostbyname(socket.gethostname()), 9999))
server.start_server()