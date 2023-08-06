v1
- basic sending of files
- single send then relaunch applications (client and server) to send again new file

v1.1
- added proper exception handlers
- allows for repeated sending and receiving files without restarting application (Client will need to be reopened if files entered are sent)

v2
- change architecture for client and server
- switching from udp to tcp connections for easier implementation

v2.1 (Expected Changes) (Future Development)
- add groups
- added * and . for easier file inclusion
- break down payload in FS_Object to handle appropriate amount of files without putting too much load

v2.2 (Future Development)
- add live file(s) syncing
- add .fsignore (ignore files in syncing)