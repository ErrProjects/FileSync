v1
- basic sending of files
- single send then relaunch applications (client and server) to send again new file

v2
- added proper exception handlers
- allows for repeated sending and receiving files without restarting application (Client will need to be reopened if files entered are sent)

v3 (Expected Changes) (In Development)
- change architecture for client and server
- add live file(s) syncing
- add .fsignore (ignore files in syncing)
- switching from udp to tcp connections for easier implementation