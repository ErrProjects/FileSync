'''
Description: This shit was produced since the developer is lazy to learn sftp/ftp stuffs :>

This is only intended for files with small sizes as memory issues may be encountered when loading large files

v0.0.1, may encounter many bugs
'''

from filesync_server import FileSyncServer
from filesync_client import FileSyncClient

print('---------------')
print('   [a] server')
print('   [b] client')
print('---------------')
choice = input('Chosen: ')

if choice == 'a':
    FileSyncServer(('127.0.0.1', 7000)).run()
elif choice == 'b':
    FileSyncClient(('127.0.0.1', 7000)).run()
else:
    print('Out of bounds!')