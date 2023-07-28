import pandas as pd
import feedparser
from tqdm import tqdm
from datetime import datetime

# Define the news sources and their RSS feed URLs
news_sources = {
    'Times of India Top Stories': 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
    'Times of India Most Recent': 'https://timesofindia.indiatimes.com/rssfeedmostrecent.cms',
    'Times of India Sports': 'https://timesofindia.indiatimes.com/rssfeeds/296589292.cms',
    'Times of India Business': 'https://timesofindia.indiatimes.com/rssfeeds/1898055.cms',
    'Times of India Entertainment': 'https://timesofindia.indiatimes.com/rssfeeds/1898184.cms',
    'Times of India World': 'https://timesofindia.indiatimes.com/rssfeeds/1898274.cms',
    'Times of India Technology': 'https://timesofindia.indiatimes.com/rssfeeds/66949542.cms',
    'Times of India Education': 'https://timesofindia.indiatimes.com/rssfeeds/913168846.cms',
    'Times of India Health': 'https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms',
    'Times of India Science': 'https://timesofindia.indiatimes.com/rssfeeds/2886704.cms',
}

# Function to fetch news data from a source


def fetch_news_data(url, num_pages):
    news_data = []

    for page in range(1, num_pages + 1):
        try:
            feed = feedparser.parse(f"{url}?page={page}")

            for entry in feed.entries:
                title = entry.title
                author = entry.author if 'author' in entry else None
                published = entry.published_parsed if 'published_parsed' in entry else None
                summary = entry.summary
                link = entry.link

                # Convert published time to a readable format
                if published:
                    published = datetime.fromtimestamp(
                        datetime(*published[:6]).timestamp()
                    ).strftime("%Y-%m-%d %H:%M:%S")

                news_item = {
                    'Title': title,
                    'Author': author,
                    'Published': published,
                    'Summary': summary,
                    'Link': link
                }

                news_data.append(news_item)
        except Exception as e:
            print(f"Error occurred while fetching data from {url}: {str(e)}")

    return news_data


# Set the number of pages to fetch
num_pages = 14

# Create an empty list to store the news data
all_news_data = []

# Retrieve news data from each source
for source, url in tqdm(news_sources.items(), desc='Fetching News'):
    news_data = fetch_news_data(url, num_pages)
    for item in news_data:
        item['Source'] = source
    all_news_data.extend(news_data)

# Create a DataFrame from the news data
df = pd.DataFrame(all_news_data)

# Save the DataFrame to an Excel file
df.to_excel('timesa.xlsx', index=False)

print('News data saved to times_of_india_news_data.xlsx file.')
