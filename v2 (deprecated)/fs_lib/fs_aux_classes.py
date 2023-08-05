import math
import os
import pickle
import socket
import struct
import zlib
from fs_lib.fs_consts import FileSyncStatus, FileSyncOperation
from fs_lib.fs_models import FS_Object, FS_File

class ObjectDataTransformer:
    @staticmethod
    def To_Bytes(object) -> bytes:
        return pickle.dumps(object)
    
    @staticmethod
    def From_Bytes(bytes_data: bytes):
        return pickle.loads(bytes_data)

class NetworkDataTransformer:
    @staticmethod
    def Bytes_To_Segments(_bytes, max_size):
        segments = []

        # Compress bytes
        compressed_bytes = zlib.compress(_bytes)
        size = len(compressed_bytes)

        # Segment bytes
        segments_count = math.ceil(size / max_size)
        for i in range(segments_count):
            segment_start = i * max_size
            segment_end = min(size, segment_start + max_size)
            segments.append(
                struct.pack("B", segments_count) +
                compressed_bytes[segment_start:segment_end]
                )
        
        return segments

    def Segments_To_Bytes(_segments, max_size):
        segment_arr = []
        
        # Loop all segments received
        for byte_data in _segments:
        
            # Unpack the data
            segments_count = struct.unpack("B", byte_data[:1])[0]
            segments = byte_data[1:]
            
            # Reconstruct the data from its segments
            for i in range(segments_count):
                segment_start = i * max_size
                segment_end = min(len(segments), segment_start + max_size)
                segment_arr.append(segments[segment_start:segment_end])
        
        # Combine all bytes to a single byte
        s_bytes = b"".join(segment_arr)

        # Decompress
        decompressed_bytes = zlib.decompress(s_bytes)
        
        # Send Back Bytes
        return decompressed_bytes


class Logging:
    DEFAULT = ("[Default]", "\033[0;32m")
    WARNING = ("[Warning]", "\033[0;33m")
    ERROR = ("[Error]", "\033[0;31m")

    def log(log_msg, severity):
        print(severity[1] + f"{severity[0]} - {log_msg}" + "\033[0;37m")


class FS_FileSearch:
    def search_files(curr_dir_only=False):
        os_walk_res = []
        
        for root, dirs, files in os.walk('.', topdown=True):
            os_walk_res = files
            break
        
        if not curr_dir_only:
            for root, dirs, files in os.walk('.', topdown=True):
                if root == '.':
                    continue
                
                for file in files:
                    os_walk_res.append(os.path.join(root, file))
        
        return os_walk_res


class FS_FileHandler:
    def __init__(self, _max_size) -> None:
        self.max_size = _max_size
        self.get_ip = socket.gethostbyname(socket.gethostname())
    
    def send_data(self, sock_inst: socket.socket, fs_obj: FS_Object) -> int:
        # Package FS_Object to bytes
        fs_obj_bytes = ObjectDataTransformer.To_Bytes(fs_obj)
        fs_obj_segments = NetworkDataTransformer.Bytes_To_Segments(fs_obj_bytes, self.max_size)
        
        # Send segments
        for segment in fs_obj_segments:
            sock_inst.sendall(segment)
        
        # Send FINISHED Flag
        sock_inst.sendall(str(FileSyncStatus.FINISHED).encode('utf-8'))
    
    def receive_file(self, fs_obj: FS_Object):
        # Check if this is the final destination of fs_obj via IP comparison
        # If true, perform place_on_dir, Otherwise, return back fs_obj
        if fs_obj.dest_ip_addr == self.get_ip or True:
            self.place_on_dir(fs_obj.payload)
        return fs_obj

    def place_on_dir(self, fs_files_list: list[FS_File]):
        for fs_file in fs_files_list:
            # Determine correct operation for file and apply such operation
            fs_file_op = fs_file.operation

            if fs_file_op == FileSyncOperation.ADD:
                dirs_file_path = os.path.dirname(fs_file.filename)
                if dirs_file_path != '':
                    os.makedirs(dirs_file_path, exist_ok=True)
                with open(fs_file.filename, 'wb') as add_file:
                    add_file.write(fs_file.filecontent)
            elif fs_file_op == FileSyncOperation.REMOVE:
                os.remove(fs_file.filename)