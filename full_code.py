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
    hindustan_times_feed = scrape_hindustan_times_feed(
        num_hindustan_times_articles)
    TN_news = articles_TimesNowNews()

    # Convert the list of dictionaries to a pandas DataFrame
    hindustan_times_df = pd.DataFrame(hindustan_times_feed)
    Timesnewsnow_df = pd.DataFrame(TN_news)
    # Combine the dataframes
    combined_df = pd.concat(
        [articles_df, hindustan_times_df, Timesnewsnow_df], ignore_index=True)

    # Drop duplicate articles based on title and source
    combined_df.drop_duplicates(subset=['Title', 'Source'], inplace=True)

    # Specify the filename for the Excel file
    filename = 'combined_articles.xlsx'

    # Save the combined DataFrame to an Excel file
    save_to_excel(combined_df, filename)

    return combined_df


# Function to save DataFrame to Excel file
def save_to_excel(df, filename):
    # Create a Pandas Excel writer using openpyxl engine
    writer = pd.ExcelWriter(filename, engine='openpyxl')

    # Write the DataFrame to the Excel file
    df.to_excel(writer, index=False)

    # Save the Excel file
    writer.close()

    print(f"Data saved to {filename}.")


# RSS feed URLs and number of pages to retrieve
rss_urls = {
    'ETTop Stories Today': 'https://cfo.economictimes.indiatimes.com/rss/topstories',
    'ET Recent Stories': 'https://cfo.economictimes.indiatimes.com/rss/recentstories',
    'ET Tax, Legal & Accounting': 'https://cfo.economictimes.indiatimes.com/rss/tax-legal-accounting',
    'ET Corporate Finance': 'https://cfo.economictimes.indiatimes.com/rss/corporate-finance',
    'ET ESG': 'https://cfo.economictimes.indiatimes.com/rss/esg',
    'ET CFO Tech': 'https://cfo.economictimes.indiatimes.com/rss/cfo-tech',
    'ET Strategy & Operations': 'https://cfo.economictimes.indiatimes.com/rss/strategy-operations',
    'ET Policy': 'https://cfo.economictimes.indiatimes.com/rss/policy',
    'ET Leadership': 'https://cfo.economictimes.indiatimes.com/rss/leadership',
    'ET Governance Risk & Compliance': 'https://cfo.economictimes.indiatimes.com/rss/governance-risk-compliance',
    'ET Interviews': 'https://cfo.economictimes.indiatimes.com/rss/Interviews',
    'ET Economy': 'https://cfo.economictimes.indiatimes.com/rss/economy',
    'ET Features': 'https://cfo.economictimes.indiatimes.com/rss/Features',
    'ET Not Just Finance': 'https://cfo.economictimes.indiatimes.com/rss/not-just-finance',
    'Mint Companies': 'https://www.livemint.com/rss/companiesRSS',
    'Mint Opinion': 'https://www.livemint.com/rss/opinionRSS',
    'Mint Money': 'https://www.livemint.com/rss/moneyRSS',
    'Mint  Politics': 'https://www.livemint.com/rss/politicsRSS',
    'Mint  Science': 'https://www.livemint.com/rss/scienceRSS',
    'Mint Industry': 'https://www.livemint.com/rss/industryRSS',
    'Mint Lounge': 'https://www.livemint.com/rss/loungeRSS',
    'Mint Education': 'https://www.livemint.com/rss/educationRSS',
    'Mint Sports': 'https://www.livemint.com/rss/sportsRSS',
    'Mint Technology': 'https://www.livemint.com/rss/technologyRSS',
    'Mint News': 'https://www.livemint.com/rss/newsRSS',
    'Mint Mutual Funds': 'https://www.livemint.com/rss/Mutual%20FundsRSS',
    'Mint Markets': 'https://www.livemint.com/rss/marketsRSS',
    'Mint AI': 'https://www.livemint.com/rss/AIRSS',
    'Mint Insurance': 'https://www.livemint.com/rss/insuranceRSS',
    'Mint Budget': 'https://www.livemint.com/rss/budgetRSS',
    'Mint Elections': 'https://www.livemint.com/rss/electionsRSS',
    'Mint Videos': 'https://www.livemint.com/rss/videos',
    'Financial Express Economy': 'https://www.financialexpress.com/economy/feed/',
    'Financial Express General News': 'https://www.financialexpress.com/feed/',
    'Financial Express Industry': 'https://www.financialexpress.com/industry/feed/',
    'Financial Express Banking and Finance': 'https://www.financialexpress.com/industry/banking-finance/feed/',
    'Financial Express Companies': 'https://www.financialexpress.com/industry/companies/feed/',
    'Financial Express Insurance': 'https://www.financialexpress.com/industry/insurance/feed/',
    'Financial Express Jobs': 'https://www.financialexpress.com/industry/jobs/feed/',
    'Financial Express World Markets': 'https://www.financialexpress.com/market/world-markets/feed/',
    'Financial Express Indian Markets': 'https://www.financialexpress.com/market/indian-markets/feed/',
    'Financial Express Market': 'https://www.financialexpress.com/market/feed/',
    'Financial Express Science': 'https://www.financialexpress.com/lifestyle/science/feed/',
    'Business Standard Top Stories': 'https://www.business-standard.com/rss/home_page_top_stories.rss',
    'Business Standard Latest News': 'https://www.business-standard.com/rss/latest.rss',
    'Business Standard Markets': 'https://www.business-standard.com/rss/markets-106.rss',
    'Business Standard Most Viewed': 'https://www.business-standard.com/rss/most-viewed.rss',
    'Business Standard India News': 'https://www.business-standard.com/rss/india-news-216.rss',
    'Business Standard Industry': 'https://www.business-standard.com/rss/industry-217.rss',
    'Business Standard Cricket': 'https://www.business-standard.com/rss/cricket-218.rss',
    'Business Standard Podcast': 'https://www.business-standard.com/rss/podcast-219.rss',
    'Business Standard World News': 'https://www.business-standard.com/rss/world-news-221.rss',
    'Business Standard Companies': 'https://www.business-standard.com/rss/companies-101.rss',
    'Business Standard Economy': 'https://www.business-standard.com/rss/economy-102.rss',

    'Republic World': 'https://www.republicworld.com/rss/world-news.xml',
    'Republic World: India News': 'https://www.republicworld.com/rss/india-news.xml',
    'Republic World: Sports News': 'https://www.republicworld.com/rss/sports-news.xml',
    'Republic World: Entertainment News': 'https://www.republicworld.com/rss/entertainment-news.xml',
    'Republic World: Technology News': 'https://www.republicworld.com/rss/technology-news.xml',
    'Republic World: Business News': 'https://www.republicworld.com/rss/business-news.xml',
    'NDTV': 'https://feeds.feedburner.com/ndtvnews-world-news',
    'NDTV News': 'https://feeds.feedburner.com/ndtvnews-india-news',
    'NDTV News': 'https://feeds.feedburner.com/ndtvnews-top-stories',
    'NDTV News': 'https://feeds.feedburner.com/ndtvnews-trending-news',
    'NDTV News': 'https://feeds.feedburner.com/ndtvmovies-latest',
    'NDTV News': 'https://feeds.feedburner.com/ndtvprofit-latest',
    'NDTV News': 'https://feeds.feedburner.com/ndtvnews-latest',
    'NDTV News': 'https://feeds.feedburner.com/ndtvsports-latest',
    'NDTV News': 'https://feeds.feedburner.com/gadgets360-latest',
    'NDTV News': 'https://feeds.feedburner.com/carandbike-latest',
    'NDTV News': 'https://feeds.feedburner.com/ndtvsports-latest',
    'NDTV News': 'https://feeds.feedburner.com/ndtvsports-cricket',
    'NDTV News': 'https://feeds.feedburner.com/ndtvnews-cities-news',
    'NDTV News': 'https://feeds.feedburner.com/ndtvnews-south',
    'NDTV News': 'https://feeds.feedburner.com/ndtvnews-indians-abroad',
    'NDTV News': 'https://feeds.feedburner.com/ndtvcooks-latest',
    'NDTV News': 'https://feeds.feedburner.com/ndtvnews-offbeat-news',
    'NDTV News': 'https://feeds.feedburner.com/ndtvnews-people',
    'NDTV News': 'https://feeds.feedburner.com/ndtv/latest-videos',
    'India Today': 'https://www.indiatoday.in/rss/home',
    'India Today': 'https://www.indiatoday.in/rss/1206514',
    'India Today': 'https://www.indiatoday.in/rss/1206614',
    'India Today': 'https://www.indiatoday.in/rss/1206494',
    'India Today': 'https://www.indiatoday.in/rss/1206577',
    'India Today': 'https://www.indiatoday.in/rss/1206500',
    'India Today': 'https://www.indiatoday.in/rss/1206550',
    'Times Now': 'https://www.timesnownews.com/google-news-sitemap-en.xml'
}

num_pages = 20
num_hindustan_times_articles = 1000

# Combine articles from multiple sources
combined_df = combine_articles(
    rss_urls, num_pages, num_hindustan_times_articles)

# Print the combined DataFrame
print(combined_df)
