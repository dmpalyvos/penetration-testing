#!/usr/bin/python3
"""
Analyze the word frequencies on the main articles of a website
"""
import argparse
import requests
from bs4 import BeautifulSoup
import re
import itertools
import string
from collections import defaultdict
import time
import json
import os


def load_ignored_words(words_file):
    '''Load a list of words to ignore from a text file
    '''

    ignored_words = set()
    # Read ignored words from file
    if words_file is not None:
        with open(words_file, 'r') as ignore_file:
            lines = ignore_file.readlines()
            lines = [line.strip() for line in lines]
            ignored_words = [w for line in lines for w in line.split(' ')]
        # Keep unique words
        ignored_words = set(ignored_words)
        print('[*] Ignoring the following words')
        print(ignored_words)

    return ignored_words


def retrieve_page(url):
    '''Rertrieve the text contents from a URL
    '''
    if url is None:
        return ''

    try:
        print('[+] Retrieving {0}'.format(url))
        content = requests.get(url).text
    except Exception as e:
        print('[-] Error retrieving page content')
        print('[-] {0}'.format(e))
        return ''

    time.sleep(0.2)
    return content


def get_element_texts(content, element_type):
    '''Get the contents of the requested elements  
    '''
    soup = BeautifulSoup(content, 'html.parser')
    elements = soup.find_all(element_type)
    text = [element.get_text().strip() for element in elements]
    return text


def get_element_links(content, element_type):
    '''Get the links inside the requested elements
    '''
    soup = BeautifulSoup(content, 'html.parser')
    elements = soup.select('{0} a'.format(element_type))
    links = [element.get('href') for element in elements]
    return links


def create_word_list(elements, ignored_words=set()):
    '''Create a list of words given a list of html elements 

    This function splits the sentenctes into words and merges them into one
    single list. Moreover, it removes punctuation and turns all words to
    lowercase in order to make frequency analysis easier.
    If provided with a list of ignored words, it removes those words from
    the final words list.

    Args:
        elements: List of HTML elements that the function gets the text from
        
        ignored_words: Set of words remove from the final list

    Returns:
        A list of all the words contained in the given elements

    '''

    word_list = []
    for element in elements:
        element_words = element.split(' ')
        if element_words is not None:
            word_list += element_words
    # Remove punctuation
    removed_punctuation = [''.join(c for c in word if c not in string.punctuation)
                           for word in word_list]
    # Make lowercase
    lower_list = [w.lower() for w in removed_punctuation]
    # Remove ignored words and words of length 1 
    final_list = [w for w in lower_list if len(w) > 1 and w not in ignored_words]

    return final_list


def count_frequencies(word_list):
    '''Create a dictionary of frequencies for each unique word
    '''
    frequencies = defaultdict(int)    
    for word in word_list:
        frequencies[word] += 1
    return frequencies


def get_domain(url):
    m = re.match(r'https?://(www\.)?(.+)\..+', url)
    return m.group(2)


def follow_links(url, element_type):

    cache_fname = '{domain}_{element}.json'.format(domain=get_domain(url),element=element_type)

    if os.path.isfile(cache_fname):
        print('[*] Loading from cache file {0}'.format(cache_fname))
        with open(cache_fname, 'r') as cache_file:
            pages = json.load(cache_file)
            return pages

    content = retrieve_page(url)
    links = get_element_links(content, element_type)
    pages = [retrieve_page(link) for link in links]

    print('[*] Saving cache file {0}'.format(cache_fname))
    with open(cache_fname, 'w') as cache_file:
        json.dump(pages, cache_file)

    return pages 


def mine_url(url, element_type, ignored_words):

    pages = follow_links(url, element_type)
    paragraph_list = [get_element_texts(page, 'p') for page in pages]
    word_lists = [create_word_list(paragraphs, ignored_words) for paragraphs in paragraph_list]
    return word_lists


def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Retrieve specified HTML'
                                     ' Elements from a URL')
    parser.add_argument('url', help='The html page you want to retrieve all'
                        ' the elements from')
    parser.add_argument('element', help='The type of html element, e.g. h1')
    parser.add_argument('-i', '--ignore', help='Path to ignored words list')
    args = parser.parse_args()

    # Add http if not already present in the url
    if not re.match('^https?://*', args.url):
        args.url = 'http://' + args.url

    # Load ignored words
    ignored_words = load_ignored_words(args.ignore)

    # Parse content
    word_lists = mine_url(args.url, args.element, ignored_words)
    all_words = itertools.chain(*word_lists)
    frequencies = count_frequencies(all_words)
    print('[*] Most Frequent Words')

    for i, w in enumerate(sorted(frequencies, key=frequencies.get, reverse=True)):
        if i > 10:
            break
        print(' {0:_<20}: {1: 5}'.format(w, frequencies[w]))


if __name__ == '__main__':
    main()
