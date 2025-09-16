import requests
from datetime import datetime
import sys
import json

def get_shein_search_results(search_term, max_results=50, page=1):
    products = []
    page_size = 20  # Puedes ajustar este valor (máximo 120)
    while len(products) < max_results:
        url = (
            f"https://www.shein.com/search-api/product/search?"
            f"keyword={search_term}&page={page}&page_size={page_size}"
        )
        print(f"Searching URL: {url}", file=sys.stderr)
        response = requests.get(url)
        data = response.json()
        items = data.get("goods_list", [])
        if not items:
            break
        for item in items:
            if len(products) >= max_results:
                break
            products.append({
                "Code": item.get("goods_id", "N/A"),
                "Title": item.get("goods_name", "N/A"),
                "Price": item.get("retailPrice", "N/A"),
                "Image URL": "https:" + item.get("goods_img", ""),
                "Product URL": f"https://www.shein.com/{item.get('goods_url', '')}",
                "Scrape Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        page += 1
    return products

if __name__ == "__main__":
    search_term = "adidas"
    max_results = 50
    products = get_shein_search_results(search_term, max_results)
    print(json.dumps(products, ensure_ascii=False, indent=4))