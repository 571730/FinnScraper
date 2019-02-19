from requests import get
from bs4 import BeautifulSoup
import re
from pathlib import Path
import sys

url_part = 'https://www.finn.no'

def iterate_pages(pages):
    text = ''
    counter = 0
    for page in pages:
        counter += 1
        print("Getting text from page", counter)
        for link in page:
            url = url_part + link['href']
            soup = soup_from_page(url)
            text += text_from_soup(soup)
    return text

def text_from_soup(soup):
    # u-word-break
    div = soup.find('div', class_='u-word-break')
    return div.get_text().lower()


def soup_from_page(link):
    response = get(link)
    return BeautifulSoup(response.text, 'html.parser')


def find_links_page(soup):
    # ads__unit__link
    all_links = soup.find_all('a', class_='ads__unit__link')

    return all_links


def count_words_in_text(text, wordlist):
    # Replace all symbols and studd with whitespace
    text = re.sub(r'[^\w]', ' ', text)
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

def check_if_good_word(goodwords, word):
    good_word = False
    for w in goodwords:
        if w == word:
            good_word = True
            break
    return good_word

def check_if_bad_word(badwords, word):
    in_bad_words = False
    for w in badwords:
        if w == word:
            in_bad_words = True
            break

    return in_bad_words

def get_bad_words(list):
    with open(list, encoding='utf8') as f:
        bad_words = f.read().strip()

    return bad_words


def text_til_fil():
    start_url = 'https://www.finn.no/job/fulltime/search.html?occupation=0.23'
    response = get(start_url)
    main_page_soup = BeautifulSoup(response.text, 'html.parser')
    all_pages = main_page_soup.find_all('a', class_='pagination__page')
    links_all_pages = []
    for page in all_pages:
        link = url_part + page['href']
        soup = soup_from_page(link)
        links_all_pages.append(find_links_page(soup))

    print('Found', len(links_all_pages), 'pages of IT job listings!')
    text_all_ads = iterate_pages(links_all_pages)
    with open("Output.txt", "w") as text_file:
        print(f"{text_all_ads}", file=text_file)

def main():
    wordlist_to_use = sys.argv[0]
    file = Path('Output.txt')
    if not file.is_file():
        text_til_fil()

    with open('Output.txt', encoding='utf8') as f:
        text_all_ads = f.read().strip()

    counts_dict = count_words_in_text(text_all_ads, wordlist_to_use)
    sorted_by_value = sorted(counts_dict.items(), key=lambda kv: kv[1])
    sorted_by_value.reverse()
    for ord in sorted_by_value:
        print(ord)



main()
