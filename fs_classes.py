import math
import os
import pickle
import socket
import struct
import zlib

class ObjectTypeTransformer:
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

class FS_File:
    def __init__(self, _operation = None, _filename = None, _filecontent = None) -> None:
        self.operation: None | int = _operation
        self.filename: None | str = _filename
        self.filecontent: None | bytes = _filecontent

    def set_filename(self, _filename):
        self.filename = _filename
    
    def set_filecontent(self, _filecontent):
        self.filecontent = _filecontent

class FS_Object:
    def __init__(self) -> None:
        self.request: None | int = None
        self.payload: None | str | FS_File = None

        # For Sending File
        self.dest_ip_addr: None | str = None
        self.dest_alias: None | str = None
    
    def set_request(self, _req: int):
        self.request = _req
    
    def set_payload(self, _payload: str | FS_File):
        self.payload = _payload
    
    def set_dest_ip_with_alias(self, _dest_ip_addr = None, _dest_alias = None):
        self.dest_ip_addr = _dest_ip_addr
        self.dest_alias = _dest_alias

class Logging:
    DEFAULT = ("[Default]", "\033[0;32m")
    WARNING = ("[Warning]", "\033[0;33m")
    ERROR = ("[Error]", "\033[0;31m")

    def log(log_msg, severity):
        print(severity[1] + f"{severity[0]} - {log_msg}" + "\033[0;37m")


class FS_FileSearch:
    def parse_fsignore_file(_filepath):
        ignored_dirs = []
        ignored_files = []
        ignored_ext = []

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