#!/usr/bin/env python3

import socket
import logging
logging.basicConfig()

import argparse


def main():

    ap = argparse.ArgumentParser()
    ap.add_argument("response")
    args = ap.parse_args()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 44444))

    while True:

        try:
            data, addr = s.recvfrom(1024)
            print(repr(data), repr(addr))
            s.sendto(args.response.encode("utf-8"), addr)
        except Exception:
            logging.exception("packet handling")


if __name__ == "__main__":
    main()
