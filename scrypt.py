import csv
import requests
from bs4 import BeautifulSoup
import sqlite3
import datetime

# Create a connection to the SQLite database
conn = sqlite3.connect('verge.db')
c = conn.cursor()

# Create the table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS articles
             (id INTEGER PRIMARY KEY, url TEXT, headline TEXT, author TEXT, date TEXT)''')


# Set the URL to scrape from
url = 'https://www.theverge.com/'

# Getting HTML content of page
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')


# Find all articles elements on the page
articles = soup.find_all('div', class_='flex grow flex-row border-gray-31 py-16 md:flex-row-reverse md:justify-between md:border-b')


#Getting Date to use as CSV filename
date = datetime.datetime.now()
file = date.strftime('%d%m%Y_verge.csv')

# Open the CSV file for writing
fieldnames = ['id','url', 'headline', 'author','date']

with open(file,mode='w') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for i, article in enumerate(articles):

        #Heading Element
        headline_element = article.find('a',class_='group-hover:shadow-underline-franklin')
        headline = headline_element.text

        #URL
        article_url = url + headline_element['href']

        #DATE TIME
        article_page = requests.get(article_url)
        article_soup = BeautifulSoup(article_page.content,'html.parser')
        date_element = article_soup.find('time',class_='duet--article--timestamp font-polysans text-12')
        article_date = date_element.text.strip()

        #AUTHOR
        author_element = article.find('a', class_='text-gray-31 hover:shadow-underline-inherit dark:text-franklin mr-8')
        article_author = author_element.text.strip()

        # WRITING IN CSV FILE
        writer.writerow({'id':i,'url':article_url,'headline':headline,'author':article_author,'date':article_date})

        # INSERTING DATA INTO SQLITE DATABASE
        c.execute("INSERT OR IGNORE INTO articles VALUES (?, ?, ?, ?, ?)",(i,article_url,headline,article_author,article_date))

# Commit the changes to the database and close the connection
conn.commit()
conn.close()