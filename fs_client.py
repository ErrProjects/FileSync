from fs_classes import FS_FileSearch, Logging, FS_Object, FS_File, NetworkDataTransformer, ObjectTypeTransformer
from fs_consts import FileSyncRequests, FileSyncOperation, FileSyncStatus
from fs_sender import FileSyncSend
from fs_receiver import FileSyncReceive

import socket

class FileSyncClient:
    def __init__(self) -> None:
        self.MAX_SIZE = 2 ** 20

        self.check_flag = lambda data, status : data.decode('utf-8') == str(status)

        # Initialize Sender and Receiver
        self.sender = FileSyncSend(self.MAX_SIZE)
        self.receiver = FileSyncReceive(self.MAX_SIZE)
    
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
            self.send_msg(payload, dest_addr_or_alias)
        elif request == FileSyncRequests.SEND_FILE:
            self.send_files(payload, dest_addr_or_alias)
    
    def send_msg(self, message: str, dest_addr_or_alias: str):
        # Create FS_Object
        fs_obj = FS_Object()
        fs_obj.set_request(FileSyncRequests.CHANGE_ALIAS)
        fs_obj.set_payload(message)
        fs_obj.set_dest_ip_with_alias(dest_addr_or_alias, dest_addr_or_alias)

        # Send FS_Object
        self.sender.send_data(self.sock, fs_obj)
    
    def send_files(self, files_collection_str: str, dest_addr_or_alias: str):
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
        
        fs_objs_list = []
        for filepath in filepaths_list:
            # Get filecontent
            filecontent = None
            with open(filepath, 'rb') as rfile:
                filecontent = rfile.read()
            
            # Turn dicts to FS_Object
            fs_obj = FS_Object()
            fs_obj.set_request(FileSyncRequests.SEND_FILE)
            fs_obj.set_payload(FS_File(FileSyncOperation.ADD, filepath, filecontent))
            fs_obj.set_dest_ip_with_alias(dest_addr_or_alias, dest_addr_or_alias)

            fs_objs_list.append(fs_obj)
        
        # Send Objects
        for fs_obj in fs_objs_list:
            self.sender.send_data(self.sock, fs_obj)

    def handle_receiving(self):
        try:
            # Get all segments
            segment_list = self.get_all_segments()

            # Turn segments to FS_Object
            fs_obj_bytes = NetworkDataTransformer.Segments_To_Bytes(segment_list, self.MAX_SIZE)
            fs_obj = ObjectTypeTransformer.From_Bytes(fs_obj_bytes)

            # Pipe to receiver
            fs_obj = self.receiver.receive_file(fs_obj)
            
            # Return string
            return f"New File Received {fs_obj.payload.filename}"
        except Exception as ex:
            Logging.log(
                f"{ex}",
                Logging.ERROR
            )
    
    def get_all_segments(self):
        segment_list = []
            
        while True:
            data = self.sock.recv(self.MAX_SIZE)
            
            if len(data) == 0:
                raise Exception("No Data Received")

            if len(data) <= 2:
                if self.check_flag(data, FileSyncStatus.FINISHED):
                    break
                elif self.check_flag(data, FileSyncStatus.RESET):
                    segment_list.clear()
            segment_list.append(data)
            
        return segment_list