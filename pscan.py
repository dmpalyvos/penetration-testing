#!/usr/bin/python3
'''
Port Scanner
'''

import argparse


def main():
    parser = argparse.ArgumentParser(description='Port Scanner')
    parser.add_argument('host', help='Destination Host')
    parser.add_argument('-p', '--port', help='Destination Port(s)', nargs='+',
                        required=True)
    args = parser.parse_args()
    host = args.host
    port = args.port
    print('Host: {0}'.format(host))
    print('Port: {0}'.format(port))


if __name__ == '__main__':
    main()
