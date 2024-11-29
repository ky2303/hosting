# hosting
This is a simple wrapper for Python's http.server module. It is modified to include a CLI and allow for uploads via HTTP PUT.

Main help:
```
python3 hosting.py --help
VPN: OFF
IP : 172.30.20.207
usage: hosting.py [-h] [-p PORT] [-d DIRECTORY]

hosting script

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Port for the HTTP server (default: 8000)
  -d DIRECTORY, --directory DIRECTORY
                        Directory for the HTTP server root (default: current directory)
```

Starting and CLI help:
```
 python3 hosting.py
VPN: OFF
IP : 10.10.10.10
HTTP server started at http://localhost:8000

Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
Welcome to the file search CLI. Type help or ? to list commands.
>> help

Documented commands (type help <topic>):
========================================
downloads  exit  help  logs  search  uploads

Undocumented commands:
======================
d  l  s  u

>>
```
