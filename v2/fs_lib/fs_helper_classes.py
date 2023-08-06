import math
import pickle
import socket
import struct
import zlib

from .fs_models import FS_Object
from .fs_consts import FS_Flag


class Logging:
    DEFAULT = ("[Default]", "\033[0;32m")
    WARNING = ("[Warning]", "\033[0;33m")
    ERROR = ("[Error]", "\033[0;31m")

    def log(log_msg, severity):
        print(severity[1] + f"{severity[0]} - {log_msg}" + "\033[0;37m")


class FileSyncIO:
    def __cmp_flag(self, data: bytes, flag: FS_Flag):
        try:
            if data.decode('utf-8') == str(flag):
                return True
        except:
            pass
        return False


    def __to_bytes(self, object) -> bytes:
        return pickle.dumps(object)
    

    def __from_bytes(self, bytes_data: bytes):
        return pickle.loads(bytes_data)
    

    def __bytes_to_segments(self, _bytes, max_size):
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
        
        # Return Segments
        return segments


    def __segments_to_bytes(self, _segments, max_size):
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
    

    def receive_fs_object(self, sock_inst: socket.socket, max_size: int) -> FS_Object:
        segment_list = []
        
        # Loop to get all segments
        while True:
            data = sock_inst.recv(max_size)
                
            if len(data) == 0:
                raise Exception("No Data Received")

            if self.__cmp_flag(data, FS_Flag.FINISHED):
                break
            elif self.__cmp_flag(data, FS_Flag.RESET):
                segment_list = []
                continue
                
            segment_list.append(data)
        
        # Convert segments to FS_Object
        fs_obj_bytes = self.__segments_to_bytes(segment_list, max_size)
        fs_obj: FS_Object = self.__from_bytes(fs_obj_bytes)
                
        return fs_obj
    
    
    def send_fs_object(self, sock_inst: socket.socket, fs_obj: FS_Object, max_size: int) -> None:
        # Package FS_Object to bytes
        fs_obj_bytes = self.__to_bytes(fs_obj)
        fs_obj_segments = self.__bytes_to_segments(fs_obj_bytes, max_size)
        
        # Send segments
        for segment in fs_obj_segments:
            sock_inst.sendall(segment)
        
        # Send FINISHED Flag
        sock_inst.sendall(str(FS_Flag.FINISHED).encode('utf-8'))