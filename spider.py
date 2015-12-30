#!/usr/bin/python3
"""

"""
import argparse
import requests
from bs4 import BeautifulSoup
import re
import itertools
import string
from collections import defaultdict


def create_word_list(elements):
    word_list = []
    for element in elements:
        element_text = element.get_text().strip()
        element_words = element_text.split(' ')
        word_list += element_words
    return word_list 


def remove_punctuation(word_list):
    for word in word_list:
        word = ''.join(c for c in word if c not in string.punctuation)

    return word_list

def count_frequencies(word_list):
    frequencies = defaultdict(int)    
    for word in word_list:
        frequencies[word] += 1
    return frequencies


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
#    for element in elements:
#        element_text = element.get_text().strip()
#        print('[*] {0}'.format(element_text))

    word_list = create_word_list(elements)
    world_list = remove_punctuation(word_list)
    frequencies = count_frequencies(word_list)

    print('[*] Most Frequent Words')

    for w in sorted(frequencies, key=frequencies.get, reverse=True):
        if frequencies[w] > 3:
            print('{0}: {1}'.format(w, frequencies[w]))

if __name__ == '__main__':
    main()
