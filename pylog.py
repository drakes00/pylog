#!/usr/bin/env python

import sys
import getopt


DEFAULT_OUT_PATH = "/tmp/pylog.log"


def record():
    # TODO


def main():
    outPath = ""

    try:
        optlist,args = getopt.getopt(sys.argv(1:], "ho:", ["help"])
    except getopt.GetoptError ad err:
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
            assert False, "Unhandled option."

    if outPath = "":
        outPath = DEFAULT_OUT_PATH


    # Setup logging thread
    # TODO

    # Start recording
    record()


if __name__ == "__main__":
    main()
