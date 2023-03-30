import pickle

class BaseClass:
    @staticmethod
    def To_Bytes(object) -> bytes:
        return pickle.dumps(object)
    
    @staticmethod
    def From_Bytes(bytes_data):
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