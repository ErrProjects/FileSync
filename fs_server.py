from fs_classes import Logging, ObjectTypeTransformer, NetworkDataTransformer, FS_Object
from fs_consts import FileSyncStatus, FileSyncRequests
from fs_sender import FileSyncSend
from fs_receiver import FileSyncReceive

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
        self.client_list: list[FSSClient] = []          # List of clients currently connected to the network
        self.MAX_SIZE = 2 ** 20

        self.check_flag = lambda data, status : data.decode('utf-8') == str(status)

        # Initialize Sender and Receiver
        self.sender = FileSyncSend(self.MAX_SIZE)
        self.receiver = FileSyncReceive(self.MAX_SIZE)
    
    def start_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt( socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        try:
            # Bind Server Info
            sock.bind(self.server_info)

            # Server Log Binded Info
            Logging.log(
                f"FileSyncServer is running at {self.server_info}",
                Logging.DEFAULT
            )

            # Listen and Accept Clients
            sock.listen()

            while True:
                conn, addr = sock.accept()

                Logging.log(
                    f"New Connection at {addr[0]}",
                    Logging.DEFAULT
                )

                # Create new client object for connecting clients
                client_obj = FSSClient(conn, addr)
                self.client_list.append(client_obj)

                # Handle client on new thread
                t = threading.Thread(target=self.handle_clients, args=(client_obj,))
                t.start()

        except Exception as ex:
            Logging.log(
                f"Server running at {self.server_info} had encountered an exception: {ex}",
                Logging.ERROR
            )
        
        sock.close()

    def handle_clients(self, client_obj: FSSClient):
        try:
            while True:
                # Receive Data from Client
                segment_list = self.get_all_segments(client_obj)

                # Turn Segments to FS_Object
                fs_obj_bytes = NetworkDataTransformer.Segments_To_Bytes(segment_list, self.MAX_SIZE)
                fs_obj: FS_Object = ObjectTypeTransformer.From_Bytes(fs_obj_bytes)

                # Handle Client Requests
                client_req = fs_obj.request

                if client_req == FileSyncRequests.CHANGE_ALIAS:
                    # Set New Alias
                    client_obj.set_alias(fs_obj.payload)

                elif client_req == FileSyncRequests.SEND_FILE:
                    # Determine Destination
                    status_code, dest_client_obj = self.determine_dest_client_obj(fs_obj.dest_ip_addr, fs_obj.dest_alias)

                    if dest_client_obj is not None:
                        self.sender.send_data(dest_client_obj.get_conn(), fs_obj)
                    else:
                        Logging.log(
                            f"Error Occurred: Invalid Ip Address, Status Code {status_code}",
                            Logging.WARNING
                        )
                    
        except Exception as ex:
            Logging.log(
                f"Client [Alias: {client_obj.get_alias()}, Addr: {client_obj.get_addr()}] was disconnected due to: {ex}",
                Logging.ERROR
            )
        
        Logging.log(
            f"Client [Alias: {client_obj.get_alias()}, Addr: {client_obj.get_addr()}] Connection Ended",
            Logging.DEFAULT
        )
        self.client_list.remove(client_obj)

    def get_all_segments(self, client_obj: FSSClient):
        segment_list = []
            
        while True:
            data = client_obj.get_conn().recv(self.MAX_SIZE)
            
            if len(data) == 0:
                raise Exception("No Data Received")

            if len(data) <= 2:
                if self.check_flag(data, FileSyncStatus.FINISHED):
                    break
                elif self.check_flag(data, FileSyncStatus.RESET):
                    segment_list.clear()
            segment_list.append(data)
            
        return segment_list

    def determine_dest_client_obj(self, obj_dest_ip = None, obj_dest_alias = None) -> FSSClient:

        if obj_dest_ip is None and obj_dest_alias is None:
            return FileSyncStatus.ERR_DEST_ADDR, None
        
        if obj_dest_ip is None and len(self.client_list) == 0:
            return FileSyncStatus.ERR_DEST_ADDR, None
        
        dest_client_obj = None

        for client_obj in self.client_list:
            if obj_dest_ip is not None and obj_dest_ip == client_obj.get_addr()[0]:
                dest_client_obj = client_obj
                break
            if obj_dest_alias is not None and obj_dest_alias == client_obj.get_alias():
                dest_client_obj = client_obj
                break

        if dest_client_obj is None:
            return FileSyncStatus.ERR_DEST_ADDR, None

        return FileSyncStatus.SUCCESS, dest_client_obj
