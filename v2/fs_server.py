from fs_lib.fs_helper_classes import FileSyncIO, Logging
from fs_lib.fs_models import FS_Object, FS_Identity
from fs_lib.fs_consts import FS_Type
import socket
import threading

class FSSClient:
    def __init__(self, _conn: socket.socket, _addr: tuple) -> None:
        self.conn = _conn
        self.addr = _addr
        self.alias = _addr

    def get_conn(self) -> socket.socket:
        return self.conn
    
    def get_addr(self) -> tuple:
        return self.addr
    
    def set_alias(self, _new_alias: str):
        self.alias = _new_alias
    
    def get_alias(self) -> str:
        return self.alias

class FS_Server(FileSyncIO):
    def __init__(self, _server_info) -> None:
        super().__init__()
        self.server_info = _server_info                 # The information needed to set up this server
        self.client_list: list[FSSClient] = []          # List of clients currently connected to the network
        self.MAX_SIZE = 2 ** 20
    
    def start_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

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

                # Create new client object for connecting clients
                client_obj = FSSClient(conn, addr)
                self.client_list.append(client_obj)

                # Handle client on new thread
                t = threading.Thread(target=self.handle_client, args=(client_obj,))
                t.start()

        except Exception as ex:
            Logging.log(
                f"Server running at {self.server_info} had encountered an exception: {ex}",
                Logging.ERROR
            )
    
        # Close Socket 
        sock.close()
    
    
    def handle_client(self, client_obj: FSSClient):
        Logging.log(
            f"Client [Alias: {client_obj.get_alias()}, Addr: {client_obj.get_addr()}] Connected to Server",
            Logging.DEFAULT
        )
        try:
            while True:
                # Receive Data from Client
                # Turn Segments to FS_Object
                request: FS_Object = self.receive_fs_object(client_obj.get_conn(), self.MAX_SIZE)

                # Handle Client Requests
                payload_type = request.payload_type

                if payload_type == FS_Type.MESSAGE:
                    self.__parse_message(client_obj, request.payload)
                
                elif payload_type == FS_Type.FILE:
                    dest_client = self.__resolve_client_address(request.receiver)

                    if dest_client is not None:
                        response: FS_Object = FS_Object()
                        response.sender = request.sender
                        response.receiver = request.receiver
                        response.set_payload(FS_Type.FILE, request.payload)
                        self.send_fs_object(dest_client.get_conn(), response, self.MAX_SIZE)

        except Exception as ex:
            Logging.log(
                f"Client [Alias: {client_obj.get_alias()}, Addr: {client_obj.get_addr()}] was disconnected due to: {ex}",
                Logging.ERROR
            )
        
        self.client_list.remove(client_obj)
        Logging.log(
            f"Client [Alias: {client_obj.get_alias()}, Addr: {client_obj.get_addr()}] Connection Ended",
            Logging.DEFAULT
        )
        Logging.log(
            f'Remaining Clients Connected: {len(self.client_list)}',
            Logging.DEFAULT
        )
    

    def __parse_message(self, client: FSSClient, msg: str):
        # Set-Alias Command
        if msg.startswith("Set-Alias"):
            new_alias = msg[len("Set-Alias"):].strip()
            client.set_alias(new_alias)
            self.__broadcast(client, f"{client.get_addr()[0]} has switched alias to {client.get_alias()}", True)
            return

        self.__broadcast(client, msg)
    

    def __broadcast(self, sender: FSSClient, msg: str, include_sender=False):
        for client in self.client_list:
            if client == sender and not include_sender:
                continue

            response: FS_Object = FS_Object()
            response.sender = FS_Identity(sender.get_alias(), sender.get_addr()[0])
            response.receiver = FS_Identity(client.get_alias(), client.get_addr()[0])
            response.set_payload(FS_Type.MESSAGE, msg)
            self.send_fs_object(client.get_conn(), response, self.MAX_SIZE)
    

    def __resolve_client_address(self, receiver: FS_Identity) -> None | FSSClient:
        # Minimum Requirement is to have either ipv4 address or alias set
        # Additionally, address/alias must be also present in the server
        dest_client: FSSClient = None

        if receiver.alias is None and receiver.ipv4_addr is None:
            return None
        
        for client in self.client_list:
            if client.get_alias() == receiver.alias:
                dest_client = client
                break
            
            if client.get_addr()[0] == receiver.ipv4_addr:
                dest_client = client
                break

        return dest_client