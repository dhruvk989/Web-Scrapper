import feedparser
import pandas as pd

# Define the news sources and their RSS feed URLs
news_sources = {
    'live hindustan': 'https://feed.livehindustan.com/rss/3116',
    'live hindustan': 'https://feed.livehindustan.com/rss/3127',
    'live hindustan पटना खबरें': 'https://feed-smart.livehindustan.com/rss/patna/news',
    'live hindustan आगरा खबरें': 'https://feed-smart.livehindustan.com/rss/agra/news',
    'live hindustan पटना ट्रेंडिंग': 'https://feed-smart.livehindustan.com/rss/patna/trending',
    'live hindustan आगरा ट्रेंडिंग': 'https://feed-smart.livehindustan.com/rss/agra/trending',
    'live hindustan पटना फोटो': 'https://feed-smart.livehindustan.com/rss/patna/photos',
    'live hindustan आगरा फोटो': 'https://feed-smart.livehindustan.com/rss/agra/photos',
    'live hindustan जयपुर खबरें': 'https://feed-smart.livehindustan.com/rss/jaipur/news',
    'live hindustan इंदौर खबरें': 'https://feed-smart.livehindustan.com/rss/indore/news',
    'live hindustan जयपुर ट्रेंडिंग': 'https://feed-smart.livehindustan.com/rss/jaipur/trending',
    'live hindustan इंदौर ट्रेंडिंग': 'https://feed-smart.livehindustan.com/rss/indore/trending',
    'live hindustan जयपुर फोटो': 'https://feed-smart.livehindustan.com/rss/jaipur/photos',
    'live hindustan इंदौर फोटो': 'https://feed-smart.livehindustan.com/rss/indore/photos',
    'live hindustan लखनऊ खबरें': 'https://feed-smart.livehindustan.com/rss/lucknow/news',
    'live hindustan कानपुर खबरें': 'https://feed-smart.livehindustan.com/rss/kanpur/news',
    'live hindustan लखनऊ ट्रेंडिंग': 'https://feed-smart.livehindustan.com/rss/lucknow/trending',
    'live hindustan कानपुर ट्रेंडिंग': 'https://feed-smart.livehindustan.com/rss/kanpur/trending',
    'live hindustan लखनऊ फोटो': 'https://feed-smart.livehindustan.com/rss/lucknow/photos',
    'live hindustan कानपुर फोटो': 'https://feed-smart.livehindustan.com/rss/kanpur/photos',
    'live hindustan मेरठ खबरें': 'https://feed-smart.livehindustan.com/rss/meerut/news',
    'live hindustan मुजफ्फरपुर खबरें': 'https://feed-smart.livehindustan.com/rss/muzaffarpur/news',
    'live hindustan मेरठ ट्रेंडिंग': 'https://feed-smart.livehindustan.com/rss/meerut/trending',
    'live hindustan मुजफ्फरपुर ट्रेंडिंग': 'https://feed-smart.livehindustan.com/rss/muzaffarpur/trending',
    'live hindustan मेरठ फोटो': 'https://feed-smart.livehindustan.com/rss/meerut/photos',
    'live hindustan मुजफ्फरपुर फोटो': 'https://feed-smart.livehindustan.com/rss/muzaffarpur/photos',
    'live hindustan वाराणसी खबरें': 'https://feed-smart.livehindustan.com/rss/varanasi/news',
    'live hindustan वाराणसी ट्रेंडिंग': 'https://feed-smart.livehindustan.com/rss/varanasi/trending',
    'live hindustan वाराणसी फोटो': 'https://feed-smart.livehindustan.com/rss/varanasi/photos',
    'live hindustan मनोरंजन': 'https://feed-smart.livehindustan.com/rss/entertainment',
    ' ABP Home Page': 'https://www.abplive.com/home/feed',
    'ABPIndia News': 'https://www.abplive.com/news/india/feed',
    'ABPWorld News': 'https://www.abplive.com/news/world/feed',
    'ABP States': 'https://www.abplive.com/states/feed',
    'ABP Sports': 'https://www.abplive.com/sports/feed',
    'ABP Bollywood': 'https://www.abplive.com/entertainment/bollywood/feed',
    'ABP Television': 'https://www.abplive.com/entertainment/television/feed',
    'ABP Tamil Cinema': 'https://www.abplive.com/entertainment/tamil-cinema/feed',
    'ABP Bhojpuri Cinema': 'https://www.abplive.com/entertainment/bhojpuri-cinema/feed',
    'ABP Astro': 'https://www.abplive.com/astro/feed',
    'ABP Religion': 'https://www.abplive.com/lifestyle/religion/feed',
    'ABP Business': 'https://www.abplive.com/business/feed',
    'ABP Gadgets': 'https://www.abplive.com/technology/gadgets/feed',
    'ABP Life Style': 'https://www.abplive.com/lifestyle/feed',
    'ABP Health': 'https://www.abplive.com/lifestyle/health/feed',
    'ABP Technology': 'https://www.abplive.com/technology/feed',
    'ABP Education': 'https://www.abplive.com/education/feed',
    'ABP Jobs': 'https://www.abplive.com/education/jobs/feed',
    'ABP Coronavirus': 'https://www.abplive.com/latest-news/coronavirus/feed',
    'ABP Agricultures': 'https://www.abplive.com/agriculture/feed',
    'ABP GK': 'https://www.abplive.com/gk/feed',
    'ABP Utility News': 'https://www.abplive.com/utility-news/feed',
    'ABP Live': 'https://www.abplive.com/home/feed',
    'ABP News Top Stories': 'https://newsapi.abplive.com/news/india/feed',
    'ABP News India': 'https://newsapi.abplive.com/news/india/national/feed',
    'ABP News World': 'https://newsapi.abplive.com/news/world/feed',
    'ABP News Business': 'https://newsapi.abplive.com/news/business/feed',
    'ABP News Sports': 'https://newsapi.abplive.com/news/sports/feed',
    'ABP News Entertainment': 'https://newsapi.abplive.com/news/entertainment/feed',
    'zee': 'https: // zeenews.india.com/hindi/tags/rss.html',
    'zee': 'https: // zeenews.india.com/hindi',
    'Zee News India': 'https://zeenews.india.com/rss/india-national-news.xml',
    'Zee News World': 'https://zeenews.india.com/rss/world-news.xml',
    'Zee News States': 'https://zeenews.india.com/rss/india-news.xml',
    'Zee News Asia': 'https://zeenews.india.com/rss/asia-news.xml',
    'Zee News Business': 'https://zeenews.india.com/rss/business.xml',
    'Zee News Sports': 'https://zeenews.india.com/rss/sports-news.xml',
    'Zee News Science & Environment': 'https://zeenews.india.com/rss/science-environment-news.xml',
    'Zee News Entertainment': 'https://zeenews.india.com/rss/entertainment-news.xml',
    'Zee News Health': 'https://zeenews.india.com/rss/health-news.xml',
    'Zee News Blogs': 'https://zeenews.india.com/rss/blog-news.xml',
    'Zee News Technology': 'https://zeenews.india.com/rss/technology-news.xml',
    'Zee News': 'https://zeenews.india.com/hindi/tags/rss.html',
    'Zee News India': 'https://zeenews.india.com/rss/india-national-news.xml',
    'Zee News World': 'https://zeenews.india.com/rss/world-news.xml',
    'Zee News Business': 'https://zeenews.india.com/rss/business-news.xml',
    'Zee News Sports': 'https://zeenews.india.com/rss/sports-news.xml',
    'Zee News Entertainment': 'https://zeenews.india.com/rss/entertainment-news.xml',
    'Zee News Technology': 'https://zeenews.india.com/rss/technology-news.xml',
    'Zee News Automobile': 'https://zeenews.india.com/rss/automobile-news.xml',

    'eNavabharat': 'https://navbharattimes.indiatimes.com/rssfeedsdefault.cms',
    'eNavabharat Top Stories': 'https://navbharattimes.indiatimes.com/rssfeeds/-2128936835.cms',
    'eNavabharat India News': 'https://navbharattimes.indiatimes.com/rssfeeds/1057854.cms',
    'eNavabharat World News': 'https://navbharattimes.indiatimes.com/rssfeeds/1057856.cms',
    'eNavabharat Business News': 'https://navbharattimes.indiatimes.com/rssfeeds/2098152.cms',
    'eNavabarat Sports News': 'https://navbharattimes.indiatimes.com/rssfeeds/4719148.cms',
    'eNavabharat Entertainment News': 'https://navbharattimes.indiatimes.com/rssfeeds/4719149.cms',
    'eNavabharat Sports': 'https://www.enavabharat.com/feeds/sports.xml',
    'eNavabharat Business': 'https://www.enavabharat.com/feeds/business.xml',
    'eNavabharat Markets': 'https://www.enavabharat.com/feeds/markets.xml',
    'eNavabharat Economy': 'https://www.enavabharat.com/feeds/economy.xml',
    'eNavabharat Entertainment': 'https://www.enavabharat.com/feeds/entertainment.xml',
    'eNavabharat Lifestyle': 'https://www.enavabharat.com/feeds/lifestyle.xml',
    'eNavabharat Education': 'https://www.enavabharat.com/feeds/education.xml',
    'eNavabharat Health': 'https://www.enavabharat.com/feeds/health.xml',
    'eNavabharat Auto': 'https://www.enavabharat.com/feeds/auto.xml',
    'eNavabharat Tech': 'https://www.enavabharat.com/feeds/tech.xml',
    'eNavabharat Astro': 'https://www.enavabharat.com/feeds/astro.xml',
    'eNavabharat Astrology': 'https://www.enavabharat.com/feeds/astrology.xml',
    'eNavabharat Astrology': 'https://www.enavabharat.com/feeds/astrology.xml',
    'eNavabharat ': 'https://www.enavabharat.com/feeds/north-india.xml',
    'aajtak': "https://www.aajtak.in",
    'aajtak': "https://www.aajtak.in/world",
    'aajtak': "https://www.aajtak.in/sports",
    'aajtak': "https://www.aajtak.in/entertainment",
    'aajtak': "https://www.aajtak.in/business",
    'aajtak': "https://www.aajtak.in/auto",
    'aajtak': "https://www.aajtak.in/technology",
    'aajtak': "https://www.aajtak.in/crime",
    'aajtak': "https://www.aajtak.in/religion",
    'aajtak': "https://www.aajtak.in/lifestyle",
    'aajtak': "https://www.aajtak.in/literature",
    'aajtak': "https://www.aajtak.in/education",
    'aajtak': "https://www.aajtak.in/fact-check",
    'aajtak': "https://www.aajtak.in/events",
    'aajtak': "https://www.aajtak.in/tez",
    'aajtak': "https://www.aajtak.in/india-today-hindi",
    'aajtak': "https://www.aajtak.in/elections",
    'aajtak': "https://www.aajtak.in/trending",
    'aajtak': "https://www.aajtak.in/anchors"
}

# Set the number of articles to extract
num_articles = 100

# Create an empty list to store the news data
news_data = []

# Retrieve news data from each source
for source, url in news_sources.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:num_articles]:
        news_item = {
            'Source': source,
            'Title': entry.title,
            'Link': entry.link,
            'Published': entry.published
        }

        news_data.append(news_item)

# Create a DataFrame from the news data
df = pd.DataFrame(news_data)

# Save the DataFrame to an Excel file
df.to_excel('news_data.xlsx', index=False)

print('News data saved to news_data.xlsx file.')

# Add further processing code for each entry in feed.entries
for entry in feed.entries:
    source_title = entry.title
    link = entry.link
    published_datetime = entry.published

    # Do further processing with the extracted information
    # Print or store the extracted data as needed
    print("Source Title:", source_title)
    print("Link:", link)
    print("Published Datetime:", published_datetime)
    print("\n")
