from fs_lib import FS_File, FileSyncStatus, NetworkDataTransformer, ask_user_for_server_client_setup
import math
import socket
import struct
import zlib
import os

class FileSyncClient:
    def __init__(self, server_info) -> None:
        self.MAX_SIZE = (2 ** 16) - 64
        self.server_info = server_info

    def prepare_and_send_files(self, files_list):
        # Get File(s) from current directory where this program is executed, will be receiving FS_File in bytes
        fs_files_bytes = self.retrieve_files(files_list)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(1)
            self.log_handler(f"Client is Listening at { self.server_info } [UDP]")
            
            # Loop through fs_files
            for ind, fs_file_byte in enumerate(fs_files_bytes):
                while True:
                    try:
                        self.send_file_sync(sock, fs_file_byte)
                        self.log_handler(f"Finished Sending File [{ind+1}]")
                        break
                    except:
                        self.log_handler(f"Server had timed out, Resending File [{ind+1}]")
                        continue

    def retrieve_files(self, files_list):
        self.log_handler(f"Searching files at { os.getcwd() }")

        fs_files_bytes = []
        for file in files_list:
            # Construct file path
            curr_path = os.path.join(os.getcwd(), file)

            # Check file validity
            if not (os.path.isfile(curr_path) and os.path.exists(curr_path)):
                self.log_handler(f"File: { curr_path } is not found, given string may be malformed. [Skip File]")
                continue

            # Turn File into FS_File
            data = None
            with open(curr_path, 'rb') as rfile:
                data = rfile.read()
            fs_file_obj = FS_File(file, data)

            # Turn FS_File obj to Bytes
            fs_file_bytes = FS_File.To_Bytes(fs_file_obj)
            
            # Add To List
            fs_files_bytes.append(fs_file_bytes)

        return fs_files_bytes

    def send_file_sync(self, sock_inst: socket.socket, fs_file_byte):
        # Transform fs_file_byte to segments
        fs_file_segments = NetworkDataTransformer.bytes_to_segments(fs_file_byte, self.MAX_SIZE)

        # Send Reset Flag to Server
        print(self.server_info)
        sock_inst.sendto(str(FileSyncStatus.RESET).encode('utf-8'), self.server_info)

        # Wait for Acknowledgement
        data, addr = sock_inst.recvfrom(1024)

        for fs_file_segment in fs_file_segments:
            # Send segments
            sock_inst.sendto(fs_file_segment, self.server_info)

            # Wait For Acknowledgement Flag from Server
            data, addr = sock_inst.recvfrom(1024)
        
        # Send Finished Flag
        sock_inst.sendto(str(FileSyncStatus.FINISHED).encode('utf-8'), self.server_info)

    def log_handler(self, log):
        print(log)


if __name__ == "__main__":
    ip_addr, port = ask_user_for_server_client_setup()
    fs_client = FileSyncClient((ip_addr, port))

    files_list = []
    while True:
        files = input('Input Filename here or relative path: ').strip()
        
        if files is None or files == '':
            break
        
        files_list.append(files)

    os.system('cls')
    fs_client.prepare_and_send_files(files_list)