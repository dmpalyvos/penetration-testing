#!/usr/bin/python3
'''
Port Scanner
'''

import argparse
import re
from socket import *


def parse_port(port_args):
    '''Parse port argument

    Args:
        port_args(list): If this list contains multiple elements, we assume
        that these correspond to unique ports and just return them as integers.
        If it contains only one element with the format X-Y then we return the
        range(X, Y).

    Retruns:
        A list of ports or a port range.

    '''
    if len(port_args) > 1:
        ports = [int(port) for port in port_args]
        return ports
    else:
        # If the argument is a range
        if port_args[0].find('-') > -1:
            port_range = re.split('-', port_args[0])
            ports = range(int(port_range[0]), int(port_range[1]))
            return ports
        else:
            return int(port_args[0])


def is_ip(host):
    '''Check if a given string is a valid IP address
    '''
    return re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', host) is not None


def main():

    # Parse Arguments
    parser = argparse.ArgumentParser(description='Port Scanner')
    parser.add_argument('host', help='Destination Host/IP Address')
    parser.add_argument('-ip', help='Destination IP')
    parser.add_argument('-p', '--port', help='Destination Port(s) seperated'
                        'by spaces or a port range (start-end)', nargs='+',
                        required=True)
    args = parser.parse_args()

    # Determine whether we were given an IP or a hostname
    # If given a hostname determine the IP and vice versa
    if is_ip(args.host):
        ip = args.host
        host = gethostbyaddr(ip)
    else:
        host = args.host
        ip = gethostbyname(host)

    # Parse ports argument
    ports = parse_port(args.port)

    print('[*] Host: {0} ({1})'.format(host, ip))
    print('[*] Ports: {0}'.format(ports))
    print('[*] Begining port scan...')


if __name__ == '__main__':
    main()
