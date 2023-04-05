# 0-7 for possible expansion
class FileSyncStatus:
    RESET = 0
    RECEIVED = 1
    FINISHED = 2

    ERR_DEST_ADDR = 3
    SUCCESS = 4

# 8-15 for possible expansion
class FileSyncOperation:
    ADD = 8
    REMOVE = 9

# 16-23 for possible expansion
class FileSyncRequests:
    CHANGE_ALIAS = 16
    SEND_FILE = 17