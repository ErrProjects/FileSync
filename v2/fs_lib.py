import os
import math
import ipaddress
import pickle
import struct
import zlib

class BaseClass:
    @staticmethod
    def To_Bytes(object) -> bytes:
        return pickle.dumps(object)
    
    @staticmethod
    def From_Bytes(bytes_data: bytes):
        return pickle.loads(bytes_data)


class FS_File(BaseClass):
    def __init__(self, _filename = None, _filecontent = None) -> None:
        self.filename: None | str = _filename
        self.filecontent: None | bytes = _filecontent

    def set_filename(self, _filename):
        self.filename = _filename
    
    def set_filecontent(self, _filecontent):
        self.filecontent = _filecontent


class FileSyncStatus:
    RESET = 0
    RECEIVED = 1
    FINISHED = 2


class NetworkDataTransformer:
    @staticmethod
    def bytes_to_segments(_bytes, max_size):
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

    def segments_to_bytes(_segments, max_size):
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
    


def ask_user_for_server_client_setup():
    ip_addr = None
    port = None

    while True:
        ip_addr = input('Set Server IP Address [Default: 127.0.0.1]: ')

        if ip_addr is None or ip_addr == '':
            ip_addr = '127.0.0.1'
            
        try:
            ipaddress.ip_address(ip_addr)
            break
        except:
            print('Invalid IP Address')
            os.system('cls')

    while True:
        port = input('Set Server Port [Default: 7000]: ')

        if port is None or port == '':
            port = 7000
            
        try:
            port = int(port)
            break
        except:
            print('Invalid Port')
            os.system('cls')
    
    return ip_addr, port