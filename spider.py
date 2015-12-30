"""

"""
import argparse
import requests
from bs4 import BeautifulSoup
import re


def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Retrieve specified HTML'
                                     ' Elements from a URL')
    parser.add_argument('url', help='The html page you want to retrieve all'
                        ' the elements from')
    parser.add_argument('element', help='The type of html element, e.g. h1')
    args = parser.parse_args()

    if not re.match('^https?://*', args.url):
        args.url = 'http://' + args.url

    # Retrieve page
    try:
        print('[+] Retrieving {0}'.format(args.url))
        content = requests.get(args.url).text
        print('[+] OK')
    except Exception as e:
        print('[-] Error retrieving page content')
        print('[-] {0}'.format(e))
        exit(1)

    # Parse content
    soup = BeautifulSoup(content, 'html.parser')

    elements = soup.find_all(args.element)
    for element in elements:
        element_text = element.get_text().strip()
        print('[*] {0}'.format(element_text))


if __name__ == '__main__':
    main()
