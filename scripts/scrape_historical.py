import pathlib
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re
import json
import csv
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

SUBURB_SLUGS = [
    'myrtle-bank-sa-5064',
    'glenunga-sa-5064',
    'fullarton-sa-5063',
    'highgate-sa-5063',
    'glenside-sa-5065',
    'frewville-sa-5063',
    'kingswood-sa-5062',
    'mitcham-sa-5062',
    'torrens-park-sa-5062',
    'unley-sa-5061',
    'malvern-sa-5061',
    'cumberland-park-sa-5041',
    'colonel-light-gardens-sa-5041',
    'glen-osmond-sa-5064'
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def crawl_sold_suburb(slug):
    url = f'https://www.homely.com.au/sold-properties/{slug}'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        urls = []
        for a in soup.find_all('a', href=re.compile(r'^/homes/[a-z0-9-]+/\d+$')):
            urls.append('https://www.homely.com.au' + a['href'])
        return list(set(urls))
    except Exception:
        return []

def parse_sold_detail(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        
        h1 = soup.find('h1')
        full_address = h1.get_text(strip=True).replace('Copy address', '').strip() if h1 else ''
        if not full_address:
            return None
            
        addr_match = re.search(r'^(.*?),\s*([A-Za-z\s]+)\s+SA\s+(\d{4})$', full_address)
        if addr_match:
            street = addr_match.group(1).strip()
            suburb = addr_match.group(2).strip()
            postcode = addr_match.group(3).strip()
        else:
            street = full_address
            suburb = ''
            postcode = ''

        if postcode == '5000' or suburb.lower() == 'adelaide':
            return None

        h2s = [h.get_text(strip=True) for h in soup.find_all('h2')]
        price_text = h2s[0] if h2s else 'Undisclosed'
        
        h3s = [h.get_text(strip=True) for h in soup.find_all('h3')]
        beds = None
        baths = None
        cars = None
        sold_date = ''
        for h in h3s:
            m = re.search(r'(\d+)\s*Bed.*?(\d+)\s*Bath.*?(\d+)\s*Car', h, re.I)
            if m:
                beds = int(m.group(1))
                baths = int(m.group(2))
                cars = int(m.group(3))
            m_date = re.search(r'Sold on\s*([A-Za-z0-9,\s]+)', h, re.I)
            if m_date:
                sold_date = m_date.group(1).strip()

        if beds != 3:
            return None

        nums = re.findall(r'[\$]?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)', price_text)
        sold_price_num = None
        if nums:
            raw_n = nums[0].replace(',', '')
            try:
                sold_price_num = float(raw_n)
            except:
                pass

        land_size = 'N/A'
        for txt in soup.stripped_strings:
            if any(k in txt for k in ['m²', 'sqm', 'Square Metres', 'Built Area']):
                m_land = re.search(r'(\d+[\d,.]*)\s*(?:m²|sqm)', txt)
                if m_land:
                    land_size = m_land.group(1) + ' m²'
                    break

        return {
            'address': full_address,
            'suburb': suburb,
            'postcode': postcode,
            'sold_price_text': price_text,
            'sold_price_num': sold_price_num,
            'sold_date': sold_date,
            'bedrooms': beds,
            'bathrooms': baths,
            'car_spaces': cars,
            'land_size': land_size,
            'url': url
        }
    except Exception:
        return None

def main():
    print("Collecting sold listing URLs across suburbs...", flush=True)
    all_urls = set()
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(crawl_sold_suburb, slug): slug for slug in SUBURB_SLUGS}
        for f in as_completed(futures):
            slug = futures[f]
            try:
                urls = f.result()
                all_urls.update(urls)
                print(f"  {slug}: {len(urls)} sold listings", flush=True)
            except Exception as e:
                print(f"  {slug}: error {e}", flush=True)

    print(f"\nTotal sold URLs found: {len(all_urls)}", flush=True)
    print("Parsing sold details...", flush=True)

    sold_data = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(parse_sold_detail, u): u for u in all_urls}
        done = 0
        for f in as_completed(futures):
            done += 1
            if done % 15 == 0 or done == len(all_urls):
                print(f"  Progress: {done}/{len(all_urls)} processed...", flush=True)
            res = f.result()
            if res:
                sold_data.append(res)

    print(f"\nTotal 3-bedroom sold properties parsed: {len(sold_data)}", flush=True)
    
    json_path = str(BASE_DIR / 'data/historical_sales_analysis.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(sold_data, f, ensure_ascii=False, indent=2)

    csv_path = str(BASE_DIR / 'data/historical_sales_analysis.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['address', 'suburb', 'postcode', 'sold_price_text', 'sold_price_num', 'sold_date', 'bedrooms', 'bathrooms', 'car_spaces', 'land_size', 'url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in sold_data:
            writer.writerow(s)

    print("Historical sold sales saved successfully to JSON and CSV!", flush=True)

if __name__ == '__main__':
    main()
