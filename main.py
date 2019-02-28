from requests import get
from bs4 import BeautifulSoup
import re
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import os
import threading

url_part = 'https://www.finn.no'

'''
    Thread-class used to scrape pages faster.
    It will be given the url to a page, then it go through all the links
    saving the text from all ads in class variables.
'''


class MyThread(threading.Thread):
    def __init__(self, threadID, page):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.page = page
        self.text = ''
        self.links = []

    def run(self):
        print("Starting thread", self.threadID)
        for link in self.page:
            url = url_part + link['href']
            self.links.append(url)
            soup = soup_from_page(url)
            self.text += text_from_soup(soup)
        print("Thread", self.threadID, "is done!")


'''
    Goes through all the found pages on finn
'''


def iterate_pages(pages):
    text = ''
    counter = 0
    links = []
    threads = []
    for page in pages:
        counter += 1
        thread = MyThread(counter, page)
        threads.append(thread)
        thread.start()
        # print("Getting text from page", counter)
        # for link in page:
        #     url = url_part + link['href']
        #     links.append(url)
        #     soup = soup_from_page(url)
        #     text += text_from_soup(soup)
    # Waiting for all threads to finish
    for t in threads:
        t.join()
    # Collecting the data from all threads
    for t in threads:
        links.extend(t.links)
        text += t.text
    links_to_file(links)
    return text


'''
    Gets all the text from each add
'''


def text_from_soup(soup):
    # u-word-break
    div = soup.find('div', class_='u-word-break')
    return div.get_text().lower()


'''
    Takes a url, returns the soup
'''


def soup_from_page(link):
    response = get(link)
    return BeautifulSoup(response.text, 'html.parser')


'''
    Finds all links on a page, on finn.no
'''


def find_links_page(soup):
    # ads__unit__link
    all_links = soup.find_all('a', class_='ads__unit__link')

    return all_links


'''
    Goes through all the text, counts the occurance of each word.
    Will also get rid of unwanted words.
    :return a dictionary
'''


def count_words_in_text(text, wordlist):
    # Replace all symbols and studd with whitespace
    # text = re.sub(r'[^\w]', ' ', text)
    text = re.sub(r'[,.]', ' ', text)
    counts = dict()
    words = text.split(' ')
    listen = 'goodwords.txt'
    use_good = True
    if wordlist == 'bad':
        listen = 'badwords.txt'
        use_good = False
    bad_words = get_bad_words(listen).split()

    for word in words:
        if not use_good:
            if check_if_bad_word(bad_words, word):
                continue
            elif word in counts:
                counts[word] += 1
            else:
                counts[word] = 1
        else:
            if check_if_good_word(bad_words, word):
                if word in counts:
                    counts[word] += 1
                else:
                    counts[word] = 1

    return counts


'''
    Checks if a word is on the good-word-list
'''


def check_if_good_word(goodwords, word):
    good_word = False
    for w in goodwords:
        if w == word:
            good_word = True
            break
    return good_word


'''
    Checks if a word is on the bad-word-list
'''


def check_if_bad_word(badwords, word):
    in_bad_words = False
    for w in badwords:
        if w == word:
            in_bad_words = True
            break

    return in_bad_words


'''
    Gets a word list
'''


def get_bad_words(list):
    with open(list, encoding='utf8') as f:
        bad_words = f.read().strip()

    return bad_words


'''
    Saves all the scraped text to a file, this is done so that you will not have to scrape all
    the pages each time you want to run the program. It can take some time.
'''


def text_til_fil():
    links_all_pages = get_all_links_finn()
    # links_to_file(links_all_pages)
    print('Found', len(links_all_pages), 'pages of IT job listings!')
    text_all_ads = iterate_pages(links_all_pages)
    with open("Output.txt", "w") as text_file:
        print(f"{text_all_ads}", file=text_file)


def links_to_file(links):
    with open("Links.txt", "w") as text_file:
        for item in links:
            text_file.write("%s\n" % item)


def get_all_links_finn():
    start_url = 'https://www.finn.no/job/fulltime/search.html?occupation=0.23'
    response = get(start_url)
    main_page_soup = BeautifulSoup(response.text, 'html.parser')
    all_pages = main_page_soup.find_all('a', class_='pagination__page')
    links_all_pages = []
    for page in all_pages:
        link = url_part + page['href']
        soup = soup_from_page(link)
        links_all_pages.append(find_links_page(soup))

    return links_all_pages


def main():
    wordlist_to_use = sys.argv[1]
    fresh_search = 'no delete'
    if len(sys.argv) == 3:
        fresh_search = sys.argv[2]
    if fresh_search == 'fresh':
        try:
            os.remove('Output.txt')
        except FileNotFoundError:
            print('Output file not there')
    print(wordlist_to_use)
    file = Path('Output.txt')
    if not file.is_file():
        text_til_fil()

    with open('Output.txt', encoding='ISO-8859-1') as f:
        text_all_ads = f.read().strip()

    counts_dict = count_words_in_text(text_all_ads, wordlist_to_use)
    sorted_by_value = sorted(counts_dict.items(), key=lambda kv: kv[1])
    # sorted_by_value.reverse()
    for ord in sorted_by_value:
        print(ord)

    if not wordlist_to_use == 'bad':
        plt.bar(range(len(counts_dict)), counts_dict.values(), align='center', color=['black', 'red', 'green', 'blue',
                                                                                      'cyan'])
        plt.xticks(range(len(counts_dict)), list(counts_dict.keys()), rotation='vertical')
        plt.show()


if __name__ == '__main__':
    main()
