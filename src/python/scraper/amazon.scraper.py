import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def get_product_inf(url):
    headers ={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Language': 'en-ES,es;q=0.9',
    }
    
    response = requests.get(url, headers=headers)   
    soup = BeautifulSoup(response.text, features="lxml")
    
    try:
        title = soup.find(id="productTitle").get_text(strip=True)
    except AttributeError:
        title = "N/A"
        
    try:
        image_url = soup.find(id="landingImage")['src']
    except (AttributeError, TypeError):
        image_url = "N/A"
    
    try:
        priceInt = soup.find('span', {'class': 'a-price-whole'}).get_text(strip=True)
        priceDec = soup.find('span', {'class': 'a-price-fraction'}).get_text(strip=True)
        price = f"{priceInt}.{priceDec}" if priceInt and priceDec else "N/A"
    except AttributeError:
        price = "N/A"
    try:
        details_table = soup.find('table', {'class': 'a-normal a-spacing-micro'})
        details_dict = {}
        for row in details_table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) == 2:
                key = cols[0].get_text(strip=True)
                value = cols[1].get_text(strip=True)
                details_dict[key] = value
        details_table = details_dict
        
    except AttributeError:
        details_table = None
        
    try:
        rating = soup.find('span', {'id': 'acrPopover'})['title']
    except AttributeError:
        rating = "N/A"
        
    return title, price, image_url, details_table, rating

def get_search_results(search_term, max_results=10):
    headers ={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Language': 'en-ES,es;q=0.9',
    }
    
    search_url = f"https://www.amazon.com/s?k={search_term.replace(' ', '+')}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, features="lxml")
    
    product_links = []
    for a_tag in soup.find_all('a', {'class': 'a-link-normal s-no-outline'}, href=True):
        if len(product_links) >= max_results:
            break
        product_links.append("https://www.amazon.com" + a_tag['href'])
        
    return product_links  

import sys

if __name__ == "__main__":
    if len(sys.argv) > 2:
        search_term = sys.argv[1]
        max_results = int(sys.argv[2])
    else:
        print("Uso: python app.py <search_term> <max_results>", file=sys.stderr)
        sys.exit(1)

    if search_term:
        product_links = get_search_results(search_term, max_results)
        print(f"Found {len(product_links)} products. Scraping details...", file=sys.stderr)
        
        all_product_data = []
        for url in product_links:
            title, price, image_url, details_table, rating = get_product_inf(url)
            product_data = {
                "Title": title,
                "Price": price,
                "Image URL": image_url,
                "Details": details_table,
                "Rating": rating,
                "Product URL": url,
                "Scrape Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            all_product_data.append(product_data)
            print(f"Scraped: {title}", file=sys.stderr)
        
        if all_product_data:
            print(json.dumps(all_product_data, ensure_ascii=False, indent=4))
    else:
        print("Please enter a search term.", file=sys.stderr)
