import json
from datetime import datetime
import sys
import re
import csv
import requests
from bs4 import BeautifulSoup

def extract_asin(url):
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    return match.group(1) if match else "N/A"

def get_search_results(search_term, max_results=1000, page_soup=None, page_number=1):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Country': 'US',
    'Cookie': 'lc-main=en_US; ubid-main=133-1234567-1234567; i18n-prefs=USD;'
}
    products = []
    current_page = page_number
    while len(products) < max_results:
        if page_soup:
            soup = page_soup
        else:
            search_url = f"https://www.amazon.com/s?k={search_term.replace(' ', '+')}&page={current_page}&ref=sr_pg_{current_page}"
            print(f"Searching URL: {search_url}", file=sys.stderr)
            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.text, features="lxml")
        
        items = soup.find_all('div', {'data-component-type': 's-search-result'})
        if not items:
            break 
        for item in items:
            if len(products) >= max_results:
                break
            try:
                title_tag = item.find('h2',{'class': 'a-size-medium a-spacing-none a-color-base a-text-normal'})
                title = title_tag.get_text(strip=True) if title_tag else "N/A"
                a_tag = item.find('a', {'class': 'a-link-normal s-no-outline'}, href=True)
                url = "https://www.amazon.com" + a_tag['href'] if a_tag else "N/A"
                asin = extract_asin(url)
                image_tag = item.find('img', {'class': 's-image'})
                image = image_tag['src'] if image_tag else "N/A"
                price = "N/A"
                price_blocks = item.find_all('span', {'class': 'a-price'})
                for pb in price_blocks:
                    price_tag = pb.find('span', {'class': 'a-offscreen'})
                    if price_tag:
                        txt = price_tag.get_text(strip=True)
                        if re.match(r'^\$\d', txt) or re.match(r'^\d', txt):
                            # Eliminar comas (separadores de miles) y luego reemplazar el símbolo de moneda
                            price = txt.replace(',', '').replace('$', '').replace('€', '')
                            break
                if price == "N/A":
                    price_whole = item.find('span', {'class': 'a-price-whole'})
                    price_fraction = item.find('span', {'class': 'a-price-fraction'})
                    if price_whole and price_fraction:
                        # Eliminar comas de la parte entera y luego concatenar con la parte decimal
                        price = f"{price_whole.text.replace(',', '')}.{price_fraction.text}"
                    else:
                        price = "N/A"
                rating_tag = item.find('span', {'class': 'a-icon-alt'})
                rating = rating_tag.text if rating_tag else "N/A"
               
            
                shipping_spans = item.find_all('span', class_='a-text-bold')
                shipping_dates = [span.get_text(strip=True) for span in shipping_spans if span.get_text(strip=True)]
                shipping = " | ".join(shipping_dates) if shipping_dates else "N/A"
                products.append({
                    "ASIN": asin,
                    "Title": title,
                    "Price": price,
                    "Image URL": image,
                    "Rating": rating,
                    "Shipping": shipping,
                    "Product URL": url,
                    "Scrape Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Shop": "amazon"
                })
            except Exception:
                continue
        current_page += 1
        if page_soup: 
            break
    return products, soup

# def save_products_to_csv(products, search_term):
#     now = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"amazon_{search_term}_{now}.csv"
#     if products:
#         keys = products[0].keys()
#         with open(filename, "w", newline='', encoding="utf-8") as f:
#             writer = csv.DictWriter(f, fieldnames=keys)
#             writer.writeheader()
#             writer.writerows(products)
#     return filename

if __name__ == "__main__":
    if len(sys.argv) > 3:
        search_term = sys.argv[1]
        max_results = int(sys.argv[2])
        page = int(sys.argv[3])
    else:
        print("Uso: python amazon.search.products.py <search_term> <max_results> <page>", file=sys.stderr)
        sys.exit(1)

    products, _ = get_search_results(search_term, max_results, page_number=page)
    print(json.dumps(products, ensure_ascii=False, indent=4))
    # csv_file = save_products_to_csv(products, search_term)
    # print(f"CSV file created: {csv_file}", file=sys.stderr)
