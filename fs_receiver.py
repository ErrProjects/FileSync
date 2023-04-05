from fs_consts import FileSyncOperation
from fs_classes import FS_Object, FS_File

import os
import socket

class FileSyncReceive:
    def __init__(self, _max_size) -> None:
        self.max_size = _max_size
        self.get_ip = socket.gethostbyname(socket.gethostname())
    
    def receive_file(self, fs_obj: FS_Object):
        # Check if this is the final destination of fs_obj via IP comparison
        # If true, perform place_on_dir, Otherwise, return back fs_obj
        if fs_obj.dest_ip_addr == self.get_ip:
            self.place_on_dir(fs_obj.payload)
        return fs_obj

    def place_on_dir(self, fs_file: FS_File):
        # Determine correct operation for file and apply such operation
        fs_file_op = fs_file.operation

        if fs_file_op == FileSyncOperation.ADD:
            os.makedirs(os.path.dirname(fs_file.filename), exist_ok=True)
            with open(fs_file.filename, 'wb') as add_file:
                add_file.write(fs_file.filecontent)
        elif fs_file_op == FileSyncOperation.REMOVE:
            os.remove(fs_file.filename)