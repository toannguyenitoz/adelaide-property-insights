import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re
import json
import csv
import time
import math
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_LAT = -34.9574204
BASE_LON = 138.6339638

SUBURB_COORDS = {
    'myrtle bank': (-34.9567, 138.6345),
    'glenunga': (-34.9472, 138.6394),
    'fullarton': (-34.9531, 138.6214),
    'highgate': (-34.9572, 138.6247),
    'netherby': (-34.9681, 138.6289),
    'urrbrae': (-34.9708, 138.6389),
    'glen osmond': (-34.9578, 138.6489),
    'mount osmond': (-34.9656, 138.6653),
    'st georges': (-34.9478, 138.6508),
    'frewville': (-34.9422, 138.6322),
    'eastwood': (-34.9392, 138.6217),
    'parkside': (-34.9439, 138.6142),
    'glenside': (-34.9400, 138.6417),
    'dulwich': (-34.9333, 138.6333),
    'toorak gardens': (-34.9317, 138.6417),
    'rose park': (-34.9281, 138.6283),
    'unley': (-34.9483, 138.6056),
    'malvern': (-34.9572, 138.6111),
    'kingswood': (-34.9650, 138.6147),
    'hawthorn': (-34.9650, 138.6014),
    'mitcham': (-34.9781, 138.6189),
    'lower mitcham': (-34.9772, 138.6028),
    'torrens park': (-34.9739, 138.6111),
    'linden park': (-34.9428, 138.6592),
    'burnside': (-34.9389, 138.6694),
    'hazelwood park': (-34.9350, 138.6617),
    'goodwood': (-34.9486, 138.5892),
    'wayville': (-34.9406, 138.5917),
    'cumberland park': (-34.9681, 138.5889),
    'colonel light gardens': (-34.9767, 138.5917),
    'westbourne park': (-34.9611, 138.5972),
    'clarence park': (-34.9603, 138.5806),
    'daw park': (-34.9817, 138.5889),
    'clapham': (-34.9867, 138.6056),
    'belair': (-34.9972, 138.6333),
    'blackwood': (-35.0194, 138.6167),
    'beaumont': (-34.9458, 138.6653),
}

SUBURB_SLUGS = [
    'myrtle-bank-sa-5064',
    'glenunga-sa-5064',
    'fullarton-sa-5063',
    'highgate-sa-5063',
    'urrbrae-sa-5064',
    'netherby-sa-5062',
    'glen-osmond-sa-5064',
    'frewville-sa-5063',
    'glenside-sa-5065',
    'eastwood-sa-5063',
    'parkside-sa-5063',
    'unley-sa-5061',
    'malvern-sa-5061',
    'kingswood-sa-5062',
    'hawthorn-sa-5062',
    'mitcham-sa-5062',
    'lower-mitcham-sa-5062',
    'torrens-park-sa-5062',
    'st-georges-sa-5064',
    'linden-park-sa-5065',
    'burnside-sa-5066',
    'hazelwood-park-sa-5066',
    'dulwich-sa-5065',
    'cumberland-park-sa-5041',
    'colonel-light-gardens-sa-5041',
    'westbourne-park-sa-5041',
    'clarence-park-sa-5034',
    'daw-park-sa-5041',
    'clapham-sa-5062',
    'mount-osmond-sa-5064'
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def get_suburb_distance(suburb_name):
    clean = suburb_name.lower().strip()
    for name, coords in SUBURB_COORDS.items():
        if name in clean or clean in name:
            return haversine_distance(BASE_LAT, BASE_LON, coords[0], coords[1])
    return 3.5

def determine_school_zones(address, suburb):
    sub = suburb.lower().strip()
    primary_schools = []
    high_schools = []
    
    gihs_suburbs = ['myrtle bank', 'glenunga', 'frewville', 'eastwood', 'glenside', 'glen osmond', 'st georges', 'linden park', 'dulwich']
    if any(s in sub for s in gihs_suburbs):
        high_schools.append('Glenunga International High School (GIHS) [Tier 1 Zone]')
    elif 'fullarton' in sub:
        high_schools.append('Glenunga International High (GIHS) / Unley High (Dual Zone depending on street)')
    elif 'parkside' in sub:
        high_schools.append('Glenunga International High / Adelaide High / Adelaide Botanic High (Border Zone)')
    
    unley_high_suburbs = ['highgate', 'malvern', 'unley', 'kingswood', 'hawthorn', 'netherby', 'urrbrae', 'mitcham', 'lower mitcham', 'torrens park', 'cumberland park', 'westbourne park']
    if any(s in sub for s in unley_high_suburbs):
        high_schools.append('Unley High School [Prestigious Zone]')
        
    girls_suburbs = ['daw park', 'colonel light gardens', 'clapham', 'mitcham', 'kingswood', 'highgate', 'netherby', 'torrens park', 'lower mitcham', 'hawthorn']
    if any(s in sub for s in girls_suburbs) or True:
        high_schools.append('Mitcham Girls High School (State-wide Zone for girls)')

    if 'myrtle bank' in sub:
        primary_schools.append('Highgate School (Zoned) / Glen Osmond Primary (Zoned)')
    elif 'glenunga' in sub:
        primary_schools.append('Glenunga International Primary / Linden Park Primary')
    elif 'fullarton' in sub:
        primary_schools.append('Highgate School / Parkside Primary')
    elif 'highgate' in sub:
        primary_schools.append('Highgate School (Top Ranked Primary)')
    elif 'glenside' in sub or 'frewville' in sub:
        primary_schools.append('Linden Park Primary / Parkside Primary')
    elif 'glen osmond' in sub or 'mount osmond' in sub:
        primary_schools.append('Glen Osmond Primary School')
    elif 'linden park' in sub or 'st georges' in sub:
        primary_schools.append('Linden Park Primary School')
    elif 'kingswood' in sub or 'mitcham' in sub or 'torrens park' in sub:
        primary_schools.append('Mitcham Primary School / Clapham Primary')
    elif 'unley' in sub or 'malvern' in sub:
        primary_schools.append('Unley Primary School')
    elif 'cumberland park' in sub or 'westbourne park' in sub or 'colonel light gardens' in sub:
        primary_schools.append('Westbourne Park Primary / Colonel Light Gardens Primary')
    else:
        primary_schools.append('Local Zoned Public Primary')

    return {
        'high_schools': high_schools,
        'primary_schools': primary_schools
    }

def parse_price(price_str):
    if not price_str:
        return None, None, "No Price"
    s = price_str.replace(',', '').replace('$', '').strip()
    
    m_range = re.findall(r'(\d+(?:\.\d+)?)\s*[mM]', s)
    if m_range:
        vals = [float(v) * 1_000_000 for v in m_range]
        return min(vals), max(vals), price_str
        
    k_range = re.findall(r'(\d+(?:\.\d+)?)\s*[kK]', s)
    if k_range:
        vals = [float(v) * 1_000 for v in k_range]
        return min(vals), max(vals), price_str
        
    nums = re.findall(r'(\d{6,8})', s)
    if nums:
        vals = [float(v) for v in nums]
        return min(vals), max(vals), price_str
        
    return None, None, price_str

def crawl_suburb(slug):
    urls = []
    for page in [1, 2]:
        p_str = '' if page == 1 else f'/page-{page}'
        url = f'https://www.homely.com.au/buy/{slug}{p_str}'
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a', href=re.compile(r'^/homes/[a-z0-9-]+/\d+$')):
                urls.append('https://www.homely.com.au' + a['href'])
        except Exception:
            break
    return list(set(urls))

def parse_listing_detail(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        
        if 'Page Not Found' in (soup.title.string or ''):
            return None
            
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
            sub_m = re.search(r'([A-Za-z\s]+)\s+SA\s+(\d{4})', full_address)
            if sub_m:
                suburb = sub_m.group(1).strip()
                postcode = sub_m.group(2).strip()

        if postcode == '5000' or suburb.lower() == 'adelaide':
            return None
            
        h2s = [h.get_text(strip=True) for h in soup.find_all('h2')]
        price_text = h2s[0] if h2s else 'Contact Agent'
        
        h3s = [h.get_text(strip=True) for h in soup.find_all('h3')]
        beds = None
        baths = None
        cars = None
        for h in h3s:
            m = re.search(r'(\d+)\s*Bed.*?(\d+)\s*Bath.*?(\d+)\s*Car', h, re.I)
            if m:
                beds = int(m.group(1))
                baths = int(m.group(2))
                cars = int(m.group(3))
                break
        if beds is None:
            b_m = re.search(r'(\d+)\s*Bed', html[:4000], re.I)
            if b_m:
                beds = int(b_m.group(1))
            ba_m = re.search(r'(\d+)\s*Bath', html[:4000], re.I)
            if ba_m:
                baths = int(ba_m.group(1))
            c_m = re.search(r'(\d+)\s*Car', html[:4000], re.I)
            if c_m:
                cars = int(c_m.group(1))

        if beds != 3:
            return None

        land_size = 'N/A'
        for txt in soup.stripped_strings:
            if any(k in txt for k in ['m²', 'sqm', 'Square Metres', 'Built Area']):
                m_land = re.search(r'(\d+[\d,.]*)\s*(?:m²|sqm)', txt)
                if m_land:
                    land_size = m_land.group(1) + ' m²'
                    break

        title_str = (soup.title.string or '').lower()
        prop_type = 'House'
        if 'townhouse' in title_str or 'townhouse' in html[:4000].lower():
            prop_type = 'Townhouse'
        elif 'unit' in title_str or 'unit' in html[:4000].lower():
            prop_type = 'Unit / Villa'
        elif 'apartment' in title_str:
            prop_type = 'Apartment'
        elif 'courtyard' in html[:4000].lower():
            prop_type = 'Courtyard Home'

        min_p, max_p, raw_p = parse_price(price_text)
        
        # If price is explicitly stated and min is above $1.25M AUD, skip
        if min_p is not None and min_p > 1_250_000:
            return None

        distance_km = get_suburb_distance(suburb)
        school_info = determine_school_zones(full_address, suburb)

        desc = ''
        desc_div = soup.find('div', class_=lambda c: c and 'description' in c.lower())
        if desc_div:
            desc = desc_div.get_text(strip=True)[:400]
        else:
            ps = [p.get_text(strip=True) for p in soup.find_all('p') if len(p.get_text(strip=True)) > 40]
            desc = ' '.join(ps[:2])[:400]

        return {
            'address': full_address,
            'street': street,
            'suburb': suburb,
            'postcode': postcode,
            'price_raw': price_text,
            'price_min': min_p,
            'price_max': max_p,
            'bedrooms': beds,
            'bathrooms': baths,
            'car_spaces': cars,
            'land_size': land_size,
            'property_type': prop_type,
            'distance_km_from_wilgena': distance_km,
            'high_schools': school_info['high_schools'],
            'primary_schools': school_info['primary_schools'],
            'description_snippet': desc,
            'url': url
        }
    except Exception:
        return None

def main():
    print("Collecting listing links across 30 suburbs...", flush=True)
    all_urls = set()
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(crawl_suburb, slug): slug for slug in SUBURB_SLUGS}
        for f in as_completed(futures):
            slug = futures[f]
            try:
                urls = f.result()
                all_urls.update(urls)
                print(f"  {slug}: {len(urls)} listings", flush=True)
            except Exception as e:
                print(f"  {slug}: error {e}", flush=True)

    print(f"\nTotal unique listing URLs: {len(all_urls)}", flush=True)
    print("Parsing listings in parallel (ThreadPoolExecutor)...", flush=True)

    matched = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(parse_listing_detail, u): u for u in all_urls}
        done = 0
        for f in as_completed(futures):
            done += 1
            if done % 20 == 0 or done == len(all_urls):
                print(f"  Progress: {done}/{len(all_urls)} checked, {len(matched)} matched criteria...", flush=True)
            res = f.result()
            if res:
                matched.append(res)

    matched.sort(key=lambda x: (x['distance_km_from_wilgena'], x['price_min'] if x['price_min'] else 9999999))
    print(f"\nCompleted! Total matching 3-bedroom properties under $1.2M: {len(matched)}", flush=True)

    json_path = 'd:/Looking for a home/data/active_listings_under_1.2m.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(matched, f, ensure_ascii=False, indent=2)

    csv_path = 'd:/Looking for a home/data/active_listings_under_1.2m.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = [
            'address', 'suburb', 'postcode', 'price_raw', 'property_type',
            'bedrooms', 'bathrooms', 'car_spaces', 'land_size',
            'distance_km_from_wilgena', 'high_schools', 'primary_schools', 'url'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for p in matched:
            row = dict(p)
            row['high_schools'] = '; '.join(p['high_schools'])
            row['primary_schools'] = '; '.join(p['primary_schools'])
            writer.writerow(row)

    print("Data saved successfully to JSON and CSV!", flush=True)

if __name__ == '__main__':
    main()
