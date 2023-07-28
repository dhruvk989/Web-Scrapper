import feedparser
import openpyxl
import os
from datetime import datetime
from dateutil.parser import parse as parse_date
import pytz
import pandas as pd
from newspaper import Config, Article
import urllib.request
import re
import os
import requests
import xml.etree.ElementTree as ET
import time

def articles_TimesNowNews():
    xml_link = "https://www.timesnownews.com/google-news-sitemap-en.xml"

    # Fetch the XML content from the link
    response = requests.get(xml_link)
    xml_content = response.content

    # Parse the XML content
    root = ET.fromstring(xml_content)
    # Define the XML namespace used in the document
    namespace = {
        "sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "news": "http://www.google.com/schemas/sitemap-news/0.9",
    }

    # Extract the title, link, and date
    articles = []
    for item in root.findall("sitemap:url", namespace):
        article = {}

        loc = item.find("sitemap:loc", namespace)
        if loc is not None and loc.text:
            article['link'] = loc.text

        title = item.find("news:news/news:title", namespace)
        if title is not None and title.text:
            article['title'] = title.text

        publication_date = item.find(
            "news:news/news:publication_date", namespace)
        if publication_date is not None and publication_date.text:
            article['date'] = publication_date.text

        articles.append(article)

    TN_data = []
    # Print the extracted data
    for article in articles:
        TN_data.append({
            'Source': "TimesNow News",
            'Title': article.get('title', 'N/A'),
            'Link': article.get('link', 'N/A'),
            'Published': article.get('date', 'N/A')
        })
    return TN_data

# Function to fetch articles from an RSS feed
def fetch_articles(rss_url, num_pages):
    # Create an empty list to store the extracted data
    data = []

    # Iterate over the specified number of pages
    for page in range(1, num_pages + 1):
        # Append page number to the RSS feed URL
        page_url = f"{rss_url}?page={page}"

        # Parse the RSS feed
        feed = feedparser.parse(page_url)

        # Extract relevant information from each entry in the feed
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            published = entry.published

            # Convert the publication date to a datetime object
            if rss_url == 'https://www.republicworld.com/rss/world-news.xml':
                pub_date_utc = datetime.strptime(
                    published, "%a, %d %b %Y %H:%M:%S %Z")
                utc_tz = pytz.timezone('GMT')
                ist_tz = pytz.timezone('Asia/Kolkata')
                pub_date_utc = utc_tz.localize(pub_date_utc)
                pub_date_ist = pub_date_utc.astimezone(ist_tz)
                published = pub_date_ist.strftime("%Y-%m-%d %H:%M:%S")
            else:
                pub_date = parse_date(published)
                published = pub_date.strftime("%Y-%m-%d %H:%M:%S")

            # Add the extracted data to the list
            data.append({
                'Source': rss_url,
                'Title': title,
                'Link': link,
                'Published': published
            })

    return data

# Function to scrape the Hindustan Times feed
def scrape_hindustan_times_feed(num_articles):
    # Replace with the actual XML URL
    xml_url = "https://www.hindustantimes.com/sitemap/news.xml"

    # Fetch the XML data from the URL
    with urllib.request.urlopen(xml_url) as response:
        xml_data = response.read().decode('utf-8')

    # Now you can use the xml_data variable to work with the XML content
    # print(xml_data)

    feed_data = []

    # xml_link="https://www.hindustantimes.com/sitemap/news.xml"

    # Extract HTML links and publishing times using regular expressions
    pattern = r"<loc>(https:\/\/www\.hindustantimes\.com\/.+?\.html)<\/loc>[\s\S]*?<news:publication_date>(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2})"
    matches = re.findall(pattern, xml_data)

    # Output the extracted links and publishing times
    for match in matches:
        link = match[0]
        time = match[1]
        pattern2 = "(https:\/(.)+\/)((.)+)(-(\d)+).html"
        matches2 = re.findall(pattern2, match[0])
        for matchh in matches2:
            title = matchh[2]
        feed_data.append({"Source": "Hindustan Times",
                         "Link": link, "Title": title, "Published": time})

    return feed_data

# Function to extract the summary from an article URL
def extract_summary(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.summary

# Function to combine articles from multiple sources
def combine_articles(rss_urls, num_pages, num_hindustan_times_articles):
    # Fetch articles from each source
    articles_data = []
    for source, rss_url in rss_urls.items():
        articles = fetch_articles(rss_url, num_pages)
        articles_data.extend(articles)

    # Create a DataFrame from the fetched data
    articles_df = pd.DataFrame(articles_data)

    # Scrape the Hindustan Times feed
    hindustan_times_feed = scrape_hindustan_times_feed(num_hindustan_times_articles)
    TN_news = articles_TimesNowNews()

    # Convert the list of dictionaries to a pandas DataFrame
    hindustan_times_df = pd.DataFrame(hindustan_times_feed)
    Timesnewsnow_df = pd.DataFrame(TN_news)

    # Combine the dataframes
    combined_df = pd.concat([articles_df, hindustan_times_df, Timesnewsnow_df], ignore_index=True)

    # Drop duplicate articles based on title and source
    combined_df.drop_duplicates(subset=['Title', 'Source'], inplace=True)

    # Add the summary field
    combined_df['Summary'] = combined_df['Link'].apply(extract_summary)

    # Specify the filename for the Excel file
    filename = 'combined_articles.xlsx'

    # Save the combined DataFrame to an Excel file
    save_to_excel(combined_df, filename)

    return combined_df

# Function to save DataFrame to Excel
def save_to_excel(df, filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{filename}_{timestamp}.xlsx"

    # Create a Pandas Excel writer using openpyxl engine
    writer = pd.ExcelWriter(filename, engine='openpyxl')

    # Write the DataFrame to the Excel file
    df.to_excel(writer, index=False)

    # Save the Excel file
    writer.save()
    writer.close()

    print(f"Data saved to {filename}.")

def auto_update(rss_urls, num_pages, num_hindustan_times_articles, update_interval_minutes):
    while True:
        # Run the code to fetch and combine articles
        combined_df = combine_articles(rss_urls, num_pages, num_hindustan_times_articles)

        # Print the combined DataFrame
        print(combined_df)

        # Wait for the specified interval before updating again
        time.sleep(update_interval_minutes * 60)

# RSS feed URLs and number of pages to retrieve
rss_urls = {
    # 'Republic World': 'https://www.republicworld.com/rss/world-news.xml',
    # 'Republic World: India News': 'https://www.republicworld.com/rss/india-news.xml',
    # 'Republic World: Sports News': 'https://www.republicworld.com/rss/sports-news.xml',
    # 'Republic World: Entertainment News': 'https://www.republicworld.com/rss/entertainment-news.xml',
    # 'Republic World: Technology News': 'https://www.republicworld.com/rss/technology-news.xml',
    # 'Republic World: Business News': 'https://www.republicworld.com/rss/business-news.xml',
    # 'NDTV': 'https://feeds.feedburner.com/ndtvnews-world-news',
    # 'NDTV News': 'https://feeds.feedburner.com/ndtvnews-india-news',
    # 'NDTV News': 'https://feeds.feedburner.com/ndtvnews-top-stories',
    # 'NDTV News': 'https://feeds.feedburner.com/ndtvnews-trending-news',
    # 'NDTV News': 'https://feeds.feedburner.com/ndtvmovies-latest',
    # 'NDTV News': 'https://feeds.feedburner.com/ndtvprofit-latest',
    # 'NDTV News': 'https://feeds.feedburner.com/ndtvnews-latest',
    # 'NDTV News': 'https://feeds.feedburner.com/ndtvsports-latest',
    # 'NDTV News': 'https://feeds.feedburner.com/gadgets360-latest',
    # 'NDTV News': 'https://feeds.feedburner.com/carandbike-latest',
    # 'NDTV News': 'https://feeds.feedburner.com/ndtvsports-latest',
    # 'NDTV News': 'https://feeds.feedburner.com/ndtvsports-cricket',
    # 'NDTV News': 'https://feeds.feedburner.com/ndtvnews-cities-news',
    # 'NDTV News': 'https://feeds.feedburner.com/ndtvnews-south',
    # 'NDTV News': 'https://feeds.feedburner.com/ndtvnews-indians-abroad',
    # 'NDTV News': 'https://feeds.feedburner.com/ndtvcooks-latest',
    # 'NDTV News': 'https://feeds.feedburner.com/ndtvnews-offbeat-news',
    # 'NDTV News': 'https://feeds.feedburner.com/ndtvnews-people',
    # 'NDTV News': 'https://feeds.feedburner.com/ndtv/latest-videos',
    # 'India Today': 'https://www.indiatoday.in/rss/home',
    # 'India Today': 'https://www.indiatoday.in/rss/1206514',
    # 'India Today': 'https://www.indiatoday.in/rss/1206614',
    # 'India Today': 'https://www.indiatoday.in/rss/1206494',
    # 'India Today': 'https://www.indiatoday.in/rss/1206577',
    # 'India Today': 'https://www.indiatoday.in/rss/1206500',
    # 'India Today': 'https://www.indiatoday.in/rss/1206550',
    # 'Times Now': 'https://www.timesnownews.com/google-news-sitemap-en.xml'
}

num_pages = 2
num_hindustan_times_articles = 5

# Specify the interval in minutes for updating the data
update_interval_minutes = 5

# Call the auto_update function with the specified parameters
auto_update(rss_urls, num_pages, num_hindustan_times_articles, update_interval_minutes)
