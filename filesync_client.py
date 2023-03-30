from filesync_lib import FS_File, FileSyncStatus
import math
import socket
import struct
import zlib
import os

class FileSyncClient:
    def __init__(self, server_info) -> None:
        self.MAX_SIZE = (2 ** 16) - 64
        self.server_info = server_info
    
    def ask_user_for_filepath(self) -> FS_File:
        print(os.getcwd())
        curr_path = None
        __r_path = ""

        while True:
            __r_path = input('Input Filename here or relative path: ')
            curr_path = os.path.join(os.getcwd(), __r_path)

            # Check if file
            if os.path.isfile(curr_path) and os.path.exists(curr_path):
                break
            else:
                print('Input may not be a valid relative path/filename or it may not exist')
        
        # Get Path and Contents
        data: bytes = None
        with open(curr_path, 'rb') as rfile:
            data = rfile.read()
        fs_file_obj = FS_File(__r_path, data)

        return fs_file_obj
    
    def run(self):
        # Get Filename and Filecontents
        fs_file_obj = self.ask_user_for_filepath()

        # Convert to seg arr
        seg_list = self.convert_FS_File_to_segments(
            FS_File.To_Bytes(fs_file_obj)
        )

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Send Flag First
            s.sendto(str(FileSyncStatus.RESET).encode('utf-8'), self.server_info)

            # Wait for Acknowledgement
            data, addr = s.recvfrom(1024)

            # Send Data
            for segments in seg_list:
                # Send Segment
                s.sendto(segments, self.server_info)

                # Wait for Acknowledgement
                data, addr = s.recvfrom(1024)
            
            # Send Finished Flag
            s.sendto(str(FileSyncStatus.FINISHED).encode('utf-8'), self.server_info)

            # Wait for Acknowledgement
            data, addr = s.recvfrom(1024)
            
    def convert_FS_File_to_segments(self, data_obj):
        fs_file_segments = []

        # Turn FS File object to bytes
        fs_file_bytes = FS_File.To_Bytes(data_obj)

        # Compress frame bytes
        fs_file_bytes = zlib.compress(fs_file_bytes)
        size = len(fs_file_bytes)

        # Segment bytes
        segments_count = math.ceil(size / self.MAX_SIZE)
        for i in range(segments_count):
            segment_start = i * self.MAX_SIZE
            segment_end = min(size, segment_start + self.MAX_SIZE)
            fs_file_segments.append(
                struct.pack("B", segments_count) +
                fs_file_bytes[segment_start:segment_end]
                )
        return fs_file_segments

if __name__ == "__main__":
    client = FileSyncClient(('127.0.0.1', 7000))
    client.run()