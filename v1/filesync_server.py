from filesync_lib import FS_File, FileSyncStatus
import socket
import struct
import os
import zlib

class FileSyncServer:
    def __init__(self, server_info) -> None:
        self.MAX_SIZE = (2 ** 16) - 64
        self.server_info = server_info

        self.check_if_flag = lambda data, status : data.decode('utf-8') == str(status)
    
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(self.server_info)
            print(f'Running on {self.server_info}')

            # List of FS segments
            seglist = []

            # Loop to get all bytes of data
            while True:
                # Receive Contents from client
                data, addr = s.recvfrom(self.MAX_SIZE)

                # Send Acknowledgment if received
                s.sendto(bytes(str(FileSyncStatus.RECEIVED).encode('utf-8')), addr)

                # Skip if Sent Bytes is too long (May not be a flag)
                if len(data) <= 2:
                    # Reset seglist if Reset Flag is sent
                    if self.check_if_flag(data, FileSyncStatus.RESET):
                        seglist.clear()
                        continue

                    # Break if sent data is Finished Flag
                    if self.check_if_flag(data, FileSyncStatus.FINISHED):
                        break

                # Add File Segment to list
                if data is not None:
                    seglist.append(data)
            
        # Parse seglist into FS File
        fs_file: FS_File = self.parse_segments_to_FS_File(seglist)

        # Generate path for destination and check if it exists, create file if it does not exist
        full_path = os.path.join(os.getcwd(), fs_file.filename)
        if not os.path.exists(full_path):
            new_file = open(full_path, 'x')
            new_file.close()
            
        # Overwrite file content
        with open(full_path, 'wb') as file_obj:
            file_obj.write(fs_file.filecontent)
    
    def parse_segments_to_FS_File(self, data_arr) -> FS_File:
        fs_file_segment_arr = []
        
        # Loop all segments received
        for byte_data in data_arr:
        
            # Unpack the FS_File data
            segments_count = struct.unpack("B", byte_data[:1])[0]
            fs_file_segments = byte_data[1:]
            
            # Reconstruct the FS_File from its segments
            for i in range(segments_count):
                segment_start = i * self.MAX_SIZE
                segment_end = min(len(fs_file_segments), segment_start + self.MAX_SIZE)
                fs_file_segment_arr.append(fs_file_segments[segment_start:segment_end])
        
        # Combine all bytes to a single FS_File byte
        fs_file_bytes = b"".join(fs_file_segment_arr)

        # Decompress
        fs_file_bytes = zlib.decompress(fs_file_bytes)
        
        # Decode the byte data to FS_File
        fs_file_obj = FS_File.From_Bytes(fs_file_bytes)
        return FS_File.From_Bytes(fs_file_obj)

if __name__ == "__main__":
    server = FileSyncServer(('127.0.0.1', 7000))
    server.run()