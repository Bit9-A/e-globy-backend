import json
from datetime import datetime
from bs4 import BeautifulSoup
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from amazon_product_info import get_product_inf

def get_today_deals_selenium(url, max_results=10):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    print(f"Loading page: {url}", file=sys.stderr)
    driver.get(url)

    try:
      
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='product-card']"))
        )
    except Exception:
        print("No se encontraron productos después de esperar.", file=sys.stderr)
        driver.quit()
        return []

    soup = BeautifulSoup(driver.page_source, "lxml")
    items = soup.find_all('div', {'data-testid': 'product-card'})
    products = []

    for item in items:
        if len(products) >= max_results:
            break
        try:
            asin = item.get('data-asin', 'N/A')
            a_tag = item.find('a', {'data-testid': 'product-card-link'}, href=True)
            if a_tag and a_tag['href']:
                href = a_tag['href']
                if href.startswith('http'):
                    product_url = href
                else:
                    product_url = "https://www.amazon.com" + href
            else:
                product_url = "N/A"
            title_span = item.find('span', class_='a-truncate-full')
            title = title_span.get_text(strip=True) if title_span else "N/A"
            img_tag = item.find('img', class_='a-amazon-image')
            image_url = img_tag['src'] if img_tag else "N/A"
            
        
            _, price_current, price_original, _, _, _ = get_product_inf(product_url)

         
            discount_span = item.find('div', class_='style_filledRoundedBadgeLabel__Vo-4g')
            discount = discount_span.get_text(strip=True) if discount_span else "N/A"
            
            products.append({
                "ASIN": asin,
                "Title": title,
                "Price Current": price_current,
                "Price Original": price_original,
                "Discount": discount,
                "Image URL": image_url,
                "Product URL": product_url,
                "Shop": "amazon",
                "Scrape Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        except Exception as e:
            print(f"Error al procesar el producto {product_url}: {e}", file=sys.stderr)
            continue

    driver.quit()
    return products

if __name__ == "__main__":
    deals_url = "https://www.amazon.com/deals"
    print(f"Scraping deals from: {deals_url}", file=sys.stderr)
    deals = get_today_deals_selenium(deals_url, max_results=2)
    if deals:
        print(json.dumps(deals, ensure_ascii=False, indent=4))
    else:
        print("No se encontraron ofertas.", file=sys.stderr)
