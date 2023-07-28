import datetime
import newspaper
from openpyxl import Workbook

# Initialize the Excel workbook and sheet
workbook = Workbook()
sheet = workbook.active

# Set the headers for the columns
headers = ["URL", "Published Date", "Heading"]
sheet.append(headers)

# Base URL for Hindustan Times website
base_url = "https://web.archive.org/web/2018"

# Define the date range
start_date = datetime.date(2018, 1, 1)
# Specify the end date for limited data extraction
end_date = datetime.date(2022, 1, 12)
delta = datetime.timedelta(days=1)

current_date = start_date
while current_date <= end_date:
    # Create the URL for the current date
    formatted_date = current_date.strftime("%Y%m%d")
    url = f"{base_url}{formatted_date}/www.hindustantimes.com"

    try:
        # Extract data using Newspaper3k
        article = newspaper.Article(url)
        article.download()
        article.parse()
        sheet.append([url, article.publish_date, article.title])

    except newspaper.article.ArticleException as e:
        print(f"Failed to extract data for URL: {url}")
        print(f"Error: {e}")

    # Move to the next day
    current_date += delta

# Save the Excel file
workbook.save("extracted_data.xlsx")
