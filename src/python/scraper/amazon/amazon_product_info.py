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
    
    price = "N/A"
    price_original = "N/A"

    try:
       
        price_full_span = soup.find('span', {'class': 'a-offscreen'})
        if price_full_span:
            price = price_full_span.get_text(strip=True).replace('$', '').replace('€', '').replace(',', '')
        else:
            priceInt = soup.find('span', {'class': 'a-price-whole'}).get_text(strip=True).replace(',', '')
            priceDec = soup.find('span', {'class': 'a-price-fraction'}).get_text(strip=True)
            price = f"{priceInt}.{priceDec}" if priceInt and priceDec else "N/A"
    except AttributeError:
        price = "N/A"

    try:
      
        original_price_span = soup.find('span', {'class': 'a-text-price'})
        if original_price_span:
            price_original = original_price_span.find('span', {'class': 'a-offscreen'}).get_text(strip=True).replace('$', '').replace('€', '').replace(',', '')
    except AttributeError:
        price_original = "N/A"

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
        
    return title, price, price_original, image_url, details_table, rating
