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
        self.payload: None | str | list[FS_File] = None

        # For Sending File
        self.dest_ip_addr: None | str = None
        self.dest_alias: None | str = None
    
    def set_request(self, _req: int):
        self.request = _req
    
    def set_payload(self, _payload: str | list[FS_File]):
        self.payload = _payload
    
    def set_dest_ip_with_alias(self, _dest_ip_addr = None, _dest_alias = None):
        self.dest_ip_addr = _dest_ip_addr
        self.dest_alias = _dest_alias
