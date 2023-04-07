from fs_lib.fs_consts import FileSyncStatus
from fs_lib.fs_aux_classes import NetworkDataTransformer, ObjectDataTransformer
from fs_lib.fs_models import FS_Object
import socket

def cmp_flag(data: bytes, flag: int):
    try:
        if data.decode('utf-8') == str(flag):
            return True
    except:
        pass
    return False

def segments_to_fs_object(sock_inst: socket.socket, max_size: int) -> FS_Object:
    segment_list = []
    
    # Loop to get all segments
    while True:
        data = sock_inst.recv(max_size)
            
        if len(data) == 0:
            raise Exception("No Data Received")

        if cmp_flag(data, FileSyncStatus.FINISHED):
            break
        elif cmp_flag(data, FileSyncStatus.RESET):
            segment_list = []
            
        segment_list.append(data)
    
    # Convert segments to FS_Object
    fs_obj_bytes = NetworkDataTransformer.Segments_To_Bytes(segment_list, max_size)
    fs_obj: FS_Object = ObjectDataTransformer.From_Bytes(fs_obj_bytes)
            
    return fs_obj