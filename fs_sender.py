from fs_classes import ObjectTypeTransformer, NetworkDataTransformer, FS_Object
from fs_consts import FileSyncStatus

import socket

class FileSyncSend:
    def __init__(self, _max_size) -> None:
        self.max_size = _max_size
    
    def send_data(self, sock_inst: socket.socket, fs_obj: FS_Object) -> int:
        # Package FS_Object to bytes
        fs_obj_bytes = ObjectTypeTransformer.To_Bytes(fs_obj)
        fs_obj_segments = NetworkDataTransformer.Bytes_To_Segments(fs_obj_bytes, self.max_size)
        
        # Send segments
        for segment in fs_obj_segments:
            sock_inst.sendall(segment)
        
        # Send FINISHED Flag
        sock_inst.sendall(str(FileSyncStatus.FINISHED).encode('utf-8'))

