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


def load_ignored_words(words_file):
    ignored_words = set()
    # Read ignored words from file
    if words_file is not None:
        with open(words_file, 'r') as ignore_file:
            lines = ignore_file.readlines()
            lines = [line.strip() for line in lines]
            ignored_words = [w for line in lines for w in line.split(' ')]
        ignored_words = set(ignored_words)
        print('[*] Ignoring the following words')
        print(ignored_words)

    return ignored_words


def create_word_list(elements, ignored_words):
    word_list = []
    for element in elements:
        element_text = element.get_text().strip()
        element_words = element_text.split(' ')
        word_list += element_words
    return remove_punctuation(word_list, ignored_words)


def remove_punctuation(word_list, ignored_words):
    # Remove punctuation
    removed_punctuation = [''.join(c for c in word if c not in string.punctuation) for word in word_list]
    # Make lowercase
    lower_list = [w.lower() for w in removed_punctuation]
    # Remove ignored words and words of length 1 
    final_list = [w for w in lower_list if len(w) > 1 and w not in ignored_words]

    return final_list


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
    parser.add_argument('-i', '--ignore', help='Path to ignored words list')
    args = parser.parse_args()

    if not re.match('^https?://*', args.url):
        args.url = 'http://' + args.url

    ignored_words = load_ignored_words(args.ignore)

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
    
    word_list = create_word_list(elements, ignored_words)
    frequencies = count_frequencies(word_list)

    print('[*] Most Frequent Words')

    for i, w in enumerate(sorted(frequencies, key=frequencies.get, reverse=True)):
        if i > 10:
            break
        print(' {0:_<20}: {1: 5}'.format(w, frequencies[w]))


if __name__ == '__main__':
    main()
