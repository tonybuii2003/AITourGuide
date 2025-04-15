from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin

service = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=service)

# We know from the pagination that there are 5 pages total
num_pages = 5

all_data = []

# Iterate through each page
for page_num in range(1, num_pages+1):
    # Construct the page URL (notice the pattern /page/X)
    page_url = f"https://scgp.stonybrook.edu/art/exhibitions/art-exhibitions-and-demonstrations/page/{page_num}"
    driver.get(page_url)
    time.sleep(3)  # Let the page load
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all article elements
    exhibitions = soup.find_all('article')
    for article in exhibitions:
        # Title
        title_tag = article.find(['h1','h2','h3'], class_='entry-title')
        title = title_tag.get_text(strip=True) if title_tag else ""
        
        # Summary
        summary_tag = article.find('div', class_='entry-summary')
        summary = summary_tag.get_text(strip=True) if summary_tag else ""
        
        # Image
        img = article.find('img')
        img_url = img.get('src') if img else ""
        if img_url and not img_url.startswith('http'):
            img_url = urljoin(page_url, img_url)
        
        all_data.append({
            'title': title,
            'summary': summary,
            'image': img_url
        })

driver.quit()

# Convert to DataFrame and export
df = pd.DataFrame(all_data)
df.to_csv('exhibitions_all_pages.csv', index=False)
print(f"Scraped {len(df)} items across {num_pages} pages.")
