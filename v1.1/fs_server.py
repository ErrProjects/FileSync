from fs_lib import FS_File, FileSyncStatus, NetworkDataTransformer, ask_user_for_server_client_setup
import socket
import os

class FileSyncServer:
    def __init__(self, server_info) -> None:
        self.MAX_SIZE = (2 ** 16) - 64
        self.server_info = server_info

        self.check_if_flag = lambda data, status : data.decode('utf-8') == str(status)
    
    def receive_files(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(self.server_info)
            self.log_handler(f'Server up on {self.server_info} [UDP]')

            # Run Loop To Keep Receiving Files
            while True:
                self.recv_file_sync(sock)
    
    def recv_file_sync(self, sock_inst: socket.socket):
        # List of FS segments
        segment_list = []

        # Loop to get all bytes of data
        while True:
            # Receive Contents from client
            data, addr = sock_inst.recvfrom(self.MAX_SIZE)

            # Send Acknowledgment if received
            sock_inst.sendto(bytes(str(FileSyncStatus.RECEIVED).encode('utf-8')), addr)

            # Skip if Sent Bytes is too long (May not be a flag)
            if len(data) <= 2:
                # Reset seglist if Reset Flag is sent
                if self.check_if_flag(data, FileSyncStatus.RESET):
                    segment_list.clear()
                    continue

                # Break if sent data is Finished Flag
                if self.check_if_flag(data, FileSyncStatus.FINISHED):
                    break

            # Add File Segment to list
            if data is not None:
                segment_list.append(data)

        # Show Log
        self.log_handler("New File Received")

        # Process File
        self.write_to_current_dir(segment_list)
    
    def write_to_current_dir(self, segment_list):
        # Parse seglist into FS File
        fs_file_bytes = NetworkDataTransformer.segments_to_bytes(segment_list, self.MAX_SIZE)
        fs_file_obj = FS_File.From_Bytes(fs_file_bytes)

        # Generate path for destination and check if it exists, create file if it does not exist
        full_path = os.path.join(os.getcwd(), fs_file_obj.filename)
        if not os.path.exists(full_path):
            new_file = open(full_path, 'x')
            new_file.close()
            
        # Overwrite file content
        with open(full_path, 'wb') as file_obj:
            file_obj.write(fs_file_obj.filecontent)

    def log_handler(self, log):
        print(log)

if __name__ == "__main__":
    ip_addr, port = ask_user_for_server_client_setup()
    fs_server = FileSyncServer((ip_addr, port))

    #os.system('cls')
    fs_server.receive_files()