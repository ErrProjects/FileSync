from fs_classes import FS_Object, ObjectTypeTransformer, NetworkDataTransformer
from fs_consts import FileSyncRequests, FileSyncStatus

import socket
import threading


class FSSClient:
    def __init__(self, _conn, _addr) -> None:
        self.conn = _conn
        self.addr = _addr
        self.alias = _addr

    def get_conn(self) -> socket.socket:
        return self.conn
    
    def get_addr(self) -> tuple:
        return self.addr
    
    def set_alias(self, _new_alias):
        self.alias = _new_alias
    
    def get_alias(self) -> str:
        return self.alias


class FileSyncServer:
    def __init__(self, _server_info) -> None:
        self.server_info = _server_info                 # The information needed to set up this server
        self.client_list: list[FSSClient] = []         # List of clients currently connected to the network
        self.MAX_SIZE = 2 ** 20

        self.check_flag = lambda data, status : data.decode('utf-8') == str(status)
    
    def start_server(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                # Bind Server Info
                sock.bind(self.server_info)

                # Server Log Binded Info
                self.__server_log(f"FileSyncServer is running at {self.server_info}")

                # Listen and Accept Clients
                sock.listen()
                conn, addr = sock.accept()

                # Create new client object for connecting clients
                client_obj = FSSClient(conn, addr)
                self.client_list.append(client_obj)

                # Handle client on new thread
                t = threading.Thread(self.handle_clients, args=(client_obj,))
                t.start()
        except:
            self.__server_log(f"Server running at {self.server_info} had encountered an exception. Shutting down...")

    def handle_clients(self, client_obj: FSSClient):
        try:
            while True:
                # Receive Client Messages
                data = self.handle_data_recv(client_obj)

                # Turn data to class
                fs_obj: FS_Object = ObjectTypeTransformer.From_Bytes(data)

                # Check requests from client
                client_req = fs_obj.request

                if client_req == FileSyncRequests.CHANGE_ALIAS:
                    client_obj.set_alias(fs_obj.payload)
                
                elif client_req == FileSyncRequests.SEND_FILE:
                    code = self.handle_file_send(fs_obj)

                    client_obj.get_conn().sendall(code)
                
        except:
            self.__server_log(f"Client [Alias: {client_obj.get_alias()}, Addr: {client_obj.get_addr()}] was disconnected due to an error")
            self.client_list.remove(client_obj)

    def handle_data_recv(self, client_obj):
        # Loop until all data had been received
        segment_list = []
        while True:
            data = client_obj.get_conn().recv(self.MAX_SIZE)

            if len(data) <= 3:
                if (self.check_flag(data, FileSyncStatus.FINISHED)):
                    break
        
        # Merge segments to one bytes object
        bytes_obj = NetworkDataTransformer.Segments_To_Bytes(segment_list, self.MAX_SIZE)

        return bytes_obj

    def handle_file_send(self, fs_obj: FS_Object):
        # Get Client Object To Send
        dest_client_obj = None
        dest_ip_addr = fs_obj.dest_ip_addr
        dest_alias = fs_obj.dest_alias
        
        for client in self.client_list:
            if dest_ip_addr is not None:
                if client.get_addr()[0] == dest_ip_addr:
                    dest_client_obj = client
                    break
            if dest_alias is not None:
                if client.get_alias() == dest_alias:
                    dest_client_obj = client
                    break
        
        if dest_client_obj is None:
            return FileSyncStatus.ERR_DEST_ADDR

        # Package Data
        fs_file = fs_obj.payload
        fs_file_bytes = ObjectTypeTransformer.To_Bytes(fs_file)
        fs_file_segments = NetworkDataTransformer.Bytes_To_Segments(fs_file_bytes, self.MAX_SIZE)

        # Send Data
        for fs_file_segment in fs_file_segments:
            dest_client_obj.get_conn().sendall(fs_file_segment)
        
        return FileSyncStatus.FINISHED


    def __server_log(self, _log):
        print(f"[TCP] {_log}")
