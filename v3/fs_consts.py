# 0-8 for possible expansion
class FileSyncStatus:
    RESET = 0
    RECEIVED = 1
    FINISHED = 2
    ERR_DEST_ADDR = 3

# 9-16 for possible expansion
class FileSyncOperation:
    ADD = 9
    UPDATE = 10
    REMOVE = 11

# 17-24 for possible expansion
class FileSyncRequests:
    CHANGE_ALIAS = 17
    SEND_FILE = 18