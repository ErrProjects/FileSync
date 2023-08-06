from .fs_consts import FS_Type

class FS_Identity:
    alias: str
    ipv4_addr: str

    def __init__(self, alias: str, ipv4_addr: str):
        self.alias = alias
        self.ipv4_addr = ipv4_addr

class FS_File:
    filename: str
    filedata: bytes

    def __init__(self, filename: str, filedata: bytes) -> None:
        self.filename = filename
        self.filedata = filedata


class FS_Object:
    sender: FS_Identity
    receiver: FS_Identity
    payload_type: FS_Type
    payload: list[FS_File] | str

    def set_payload(self, payload_type: FS_Type, payload: list[FS_File] | str):
        self.payload_type = payload_type
        self.payload = payload
