#!/usr/bin/python3
'''
Port Scanner
'''

import argparse
import re
import socket
from threading import Thread, Lock
from queue import Queue

OUTPUT_LOCK = Lock()
NUM_THREADS = 100


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
        return port_args
    else:
        # If the argument is a range
        if port_args[0].find('-') > -1:
            port_range = re.split('-', port_args[0])
            ports = range(int(port_range[0]), int(port_range[1])+1)
            return ports
        else:
            return port_args


def parse_host(host_arg):
    '''Resolve the hostname and the IP from the given hostname/IP

    This function determines whether the user has given us a hostname or an
    IP address and takes the necessary actions to determine the other one.
    If the hostname cannot be determined from the IP, it simply returns an
    'Unknown' host. If the IP cannot be resolved, the program fails.

    Args:
        host_arg (string): Either a hostname or an IP address

    Returns:
        ip, hostname (strings)

    '''

    # Determine whether we were given an IP or a hostname
    # If given a hostname determine the IP and vice versa
    if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', host_arg) is not None:
        ip = host_arg
        try:
            host = socket.gethostbyaddr(ip)
        except:
            print('Could not resolve hostname')
            host = 'Unknown'
    else:
        host = host_arg
        try:
            ip = socket.gethostbyname(host)
        except:
            # If we can't find the IP the program must be terminated
            print('Could not find IP address')
            exit(1)

    return ip, host


def try_tcp(ip, port):
    '''Try to establish a TCP connection to the specified IP/Port
    '''

    port = int(port)
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((ip, port))
        # Send a dummy string to help us determine the application running
        conn.send(b'Test String, please ignore\r\n')
        result = conn.recv(128).decode().strip()
        # If no exception is thrown, we managed to connect
        with OUTPUT_LOCK:
            print('[+] {0}/tcp OPEN'.format(port))
            print('[+] Service: {0}'.format(result))
    except:
        pass
        # print('[-] {0}/tcp closed'.format(port))
    finally:
        conn.close()


def worker(q):
    while True:
        args = q.get()
        try_tcp(args[0], args[1])
        q.task_done()


def scan_host(ip, ports):
    '''Perform a port scan for the given host and ports list
    '''
    print('[*] Started port scan...')
    socket.setdefaulttimeout(2.0)
    q = Queue()

    for port in ports:
        q.put((ip, port))

    for i in range(NUM_THREADS):
        t = Thread(target=worker, args=(q, ))
        t.daemon = True
        t.start()
    q.join()


def main():

    # Parse Arguments
    parser = argparse.ArgumentParser(description='Port Scanner')
    parser.add_argument('host', help='Destination Host/IP Address')
    parser.add_argument('-ip', help='Destination IP')
    parser.add_argument('-p', '--port', help='Destination Port(s) seperated'
                        'by spaces or a port range (start-end)', nargs='+',
                        required=True)
    args = parser.parse_args()

    ip, host = parse_host(args.host)
    ports = parse_port(args.port)

    print('[*] Host: {0} ({1})'.format(host, ip))
    print('[*] Ports: {0}'.format(ports))

    scan_host(ip, ports)


if __name__ == '__main__':
    main()
