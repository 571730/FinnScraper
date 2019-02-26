# FinnScraper
### Scraping the website Finn.no looking for buzzwords

#### Usage
To count all words found in goodwords.txt

`python main.py good`

or you can count all words not excluded using badwordlist.txt

`python main.py bad`

To scrape through all the pages and find new job listings, 
add the keyword `fresh`. If this is not added, the program will use
a saved list of text to avoid the slow task of scraping all the links again.

To count words and get a new updated list

`python main.py good fresh`