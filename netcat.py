#!/usr/bin/env python3

import argparse
import sys
from support.ncFns import listenMode
from support.ncFns import clientMode

# Color Settings
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
PURPLE  = "\033[35m"
RESET   = "\033[0m"


def checkArgs (parser, args):

    retVal = True
    if not args.listen and not args.target:
        parser.error (RED + "[!] " + YELLOW + " Target unspecified for client mode" + RESET)
        retVal = False

    if args.upload and args.download:
        parser.error (RED + "[!]" + YELLOW + " '-u' and '-d' can not be clubbed together" + RESET)
        retVal = False

    if args.spawn and args.catch:
        parser.error (RED + "[!]" + YELLOW + " '-sS' and '-sC' can not be clubbed together" + RESET)
        retVal = False

    return retVal


def getArgs ():

    parser = argparse.ArgumentParser (description = RED + "Netcat Custom Tool" + RESET)

    parser.add_argument ('-l', "--listen", action = "store_true", dest = "listen", help = "Listen Mode")
    parser.add_argument ('-t', "--target", action = "store", dest = "target", help = "Target IP")
    parser.add_argument ('-u', "--upload", action = "store", dest = "upload", help = "Upload file")
    parser.add_argument ('-d', "--download", action = "store", dest = "download", help = "Download file")
    parser.add_argument ('-sS', "--spawn", action = "store_true", dest = "spawn", help = "Spawn a shell")
    parser.add_argument ('-sC', "--catch", action = "store_true", dest = "catch", help = "Catch the shell")
    parser.add_argument ("port", action = "store", help = "Port address")

    args = parser.parse_args ()

    if checkArgs (parser, args):
        return args
    else:
        print (RED + "Exiting" + RESET)
        sys.exit (1)


def main ():

    args = getArgs()

    listen = args.listen
    target = args.target
    upload = args.upload
    download = args.download
    spawn = args.spawn
    catch = args.catch
    port = int (args.port)

    if listen:
        listenMode (target, upload, download, spawn, catch, port)
    else:
        clientMode (target, upload, download, spawn, catch, port)


if __name__ == "__main__":
    main ()