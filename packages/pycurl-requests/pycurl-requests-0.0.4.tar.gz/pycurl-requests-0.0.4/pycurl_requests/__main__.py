"""Shim for running existing Requests-based script using PycURL-Requests."""
import argparse
import runpy
import sys

import pycurl_requests


def main():
    parser = argparse.ArgumentParser(description='a Requests-compatible interface for PycURL')
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('-m', dest='module', help='Python module to run')
    source_group.add_argument('script', help='Python script to run', nargs='?')
    parser.add_argument('arg', nargs='*', help='script arguments')
    args = parser.parse_args()

    # Override requests
    pycurl_requests.patch_requests()

    # Run script
    sys.argv[1:] = args.arg
    if args.module:
        runpy.run_module(args.module, run_name='__main__')
    else:
        runpy.run_path(args.script, run_name='__main__')
    sys.exit()


if __name__ == '__main__':
    main()
