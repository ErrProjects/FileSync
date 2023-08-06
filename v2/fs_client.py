from fs_lib.fs_helper_classes import FileSyncIO, Logging
from fs_lib.fs_models import FS_Object, FS_Identity, FS_File
from fs_lib.fs_consts import FS_Type
import os
import socket

class FS_Client(FileSyncIO):
    def __init__(self) -> None:
        self.MAX_SIZE = 2 ** 20
    
    def connect_to_server(self, server_info):
        self.server_info = server_info
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Connect to Server
            Logging.log(
                f"Connecting to Server {self.server_info}",
                Logging.DEFAULT
            )
            self.sock.connect(self.server_info)

        except Exception as ex:
            Logging.log(
                f"Exception detected: {ex}",
                Logging.ERROR
            )
    
    def close_connection(self):
        Logging.log(
            f"Closing Connection to {self.server_info}",
            Logging.DEFAULT
        )
        self.sock.close()
    
    def send_msg(self, dest_addr_or_alias: str, message: str):
        # Create FS_Object
        fs_obj = FS_Object()
        fs_obj.sender = FS_Identity('', self.sock.getsockname())
        fs_obj.receiver = FS_Identity(dest_addr_or_alias, dest_addr_or_alias)
        fs_obj.set_payload(FS_Type.MESSAGE, message)

        # Send FS_Object
        self.send_fs_object(self.sock, fs_obj, self.MAX_SIZE)

    def send_files(self, dest_addr_or_alias: str, path_list: list[str]):
        files: list[FS_File] = []

        # Get all files
        for file_path in path_list:
            with open(file_path, "rb") as file:
                content = file.read()
                filename = file_path.split("/")[-1]
                files.append(FS_File(filename, content))

        # Create FS_Object
        fs_obj = FS_Object()
        fs_obj.sender = FS_Identity('', self.sock.getsockname())
        fs_obj.receiver = FS_Identity(dest_addr_or_alias, dest_addr_or_alias)
        fs_obj.set_payload(FS_Type.FILE, files)

        # Send FS_Object
        self.send_fs_object(self.sock, fs_obj, self.MAX_SIZE)

    def handle_receiving(self):
        try:
            # Get FS_Object
            str_ls = []
            fs_obj = self.receive_fs_object(self.sock, self.MAX_SIZE)

            # Check Payload Type
            payload_type = fs_obj.payload_type
            if payload_type == FS_Type.MESSAGE:
                str_ls.append(str(fs_obj.payload))
            elif payload_type == FS_Type.FILE:
                for fs_file in fs_obj.payload:
                    str_ls.append(f"New File Received {fs_file.filename}")

                    dirs_file_path = os.path.dirname(fs_file.filename)
                    if dirs_file_path != '':
                        os.makedirs(dirs_file_path, exist_ok=True)
                    with open(fs_file.filename, 'wb') as add_file:
                        add_file.write(fs_file.filecontent)

            return str_ls
        
        except Exception as ex:
            Logging.log(
                f"{ex}",
                Logging.ERROR
            )
        return ["Error, detected"]
    