from fs_lib.fs_aux_classes import Logging, FS_FileHandler, FS_FileSearch
from fs_lib.fs_consts import FileSyncRequests, FileSyncOperation
from fs_lib.fs_funcs import segments_to_fs_object
from fs_lib.fs_models import FS_Object, FS_File
import socket
import threading

class FileSyncClient:
    def __init__(self) -> None:
        self.MAX_SIZE = 2 ** 20

        # Initialize Sender and Receiver
        self.file_handler = FS_FileHandler(self.MAX_SIZE)
    
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

    def handle_sending(self, dest_addr_or_alias: str, request: int, payload: str):
        if request == FileSyncRequests.CHANGE_ALIAS:
            self._send_msg(payload, dest_addr_or_alias)
        elif request == FileSyncRequests.SEND_FILE:
            self._send_files(payload, dest_addr_or_alias)
    
    def _send_msg(self, message: str, dest_addr_or_alias: str):
        # Create FS_Object
        fs_obj = FS_Object()
        fs_obj.set_request(FileSyncRequests.CHANGE_ALIAS)
        fs_obj.set_payload(message)
        fs_obj.set_dest_ip_with_alias(dest_addr_or_alias, dest_addr_or_alias)

        # Send FS_Object
        self.file_handler.send_data(self.sock, fs_obj)
    
    def _send_files(self, files_collection_str: str, dest_addr_or_alias: str):
        # Turn file_collection_str to proper list
        # Check for special symbols, if none found, check for file names/paths that are comma-separated
        filepaths_list = []
        if files_collection_str == "*":
            filepaths_list = FS_FileSearch.search_files()
        elif files_collection_str == ".":
            filepaths_list = FS_FileSearch.search_files(curr_dir_only=True)
        else:
            files_collection = files_collection_str.split(',')
            for files in files_collection:
                filepaths_list.append(files.strip())
        
        fs_files_list: list[FS_File] = []
        for filepath in filepaths_list:
            # Get filecontent as bytes
            filecontent = None
            with open(filepath, 'rb') as rfile:
                filecontent = rfile.read()
            
            # Turn to FS_File
            fs_file = FS_File(FileSyncOperation.ADD, filepath, filecontent)
            fs_files_list.append(fs_file)
        
        # Construct FS_Object
        fs_obj = FS_Object()
        fs_obj.set_request(FileSyncRequests.SEND_FILE)
        fs_obj.set_payload(fs_files_list)
        fs_obj.set_dest_ip_with_alias(dest_addr_or_alias, dest_addr_or_alias)
        
        # Send FS_Object
        self.file_handler.send_data(self.sock, fs_obj)
            

    def handle_receiving(self):
        try:
            fs_obj = segments_to_fs_object(self.sock, self.MAX_SIZE)

            # Push to receiver
            fs_obj = self.file_handler.receive_file(fs_obj)
            
            # Return get files
            fs_files_list = fs_obj.payload

            # Loop filenames
            str_ls = []
            for fs_file in fs_files_list:
                str_ls.append(f"New File Received {fs_file.filename}")
            return str_ls
        
        except Exception as ex:
            Logging.log(
                f"{ex}",
                Logging.ERROR
            )
        return ["Error, detected"]
    