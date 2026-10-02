import pathlib
import urllib.request
import re
import json
import csv
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import math

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
OUTPUT_JSON = BASE_DIR / 'data/recently_sold_properties.json'
OUTPUT_CSV = BASE_DIR / 'data/recently_sold_properties.csv'
AUCTION_JSON = BASE_DIR / 'data/domain_weekly_auction_results.json'

BASE_LAT = -34.9574204
BASE_LON = 138.6339638

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

# Suburb Coordinates Map for exact distance calculation
SUBURB_COORDS = {
    # Burnside
    'myrtle bank': (-34.9567, 138.6345), 'glenunga': (-34.9472, 138.6394),
    'toorak gardens': (-34.9333, 138.6333), 'dulwich': (-34.9350, 138.6250),
    'rose park': (-34.9280, 138.6250), 'tusmore': (-34.9333, 138.6500),
    'hazelwood park': (-34.9350, 138.6617), 'burnside': (-34.9389, 138.6694),
    'erindale': (-34.9310, 138.6670), 'leabrook': (-34.9280, 138.6600),
    'linden park': (-34.9450, 138.6550), 'st georges': (-34.9520, 138.6500),
    'beaumont': (-34.9500, 138.6670), 'stonyfell': (-34.9350, 138.6800),
    'wattle park': (-34.9280, 138.6750), 'glenside': (-34.9400, 138.6417),
    'frewville': (-34.9422, 138.6322), 'kensington gardens': (-34.9220, 138.6670),
    'kensington park': (-34.9264, 138.6583), 'rosslyn park': (-34.9200, 138.6750),
    'beulah park': (-34.9190, 138.6450), 'auldana': (-34.9180, 138.6900),
    'mount osmond': (-34.9650, 138.6600), 'glen osmond': (-34.9578, 138.6489),
    # Unley
    'unley': (-34.9483, 138.6056), 'unley park': (-34.9600, 138.6000),
    'malvern': (-34.9550, 138.6100), 'hyde park': (-34.9500, 138.6000),
    'millswood': (-34.9580, 138.5900), 'kings park': (-34.9620, 138.5950),
    'goodwood': (-34.9480, 138.5900), 'wayville': (-34.9400, 138.5900),
    'parkside': (-34.9420, 138.6150), 'fullarton': (-34.9531, 138.6214),
    'highgate': (-34.9572, 138.6247), 'black forest': (-34.9600, 138.5750),
    'clarence park': (-34.9650, 138.5850), 'everard park': (-34.9550, 138.5800),
    'forestville': (-34.9480, 138.5800),
    # Mitcham
    'mitcham': (-34.9781, 138.6189), 'lower mitcham': (-34.9772, 138.6028),
    'kingswood': (-34.9650, 138.6147), 'torrens park': (-34.9739, 138.6111),
    'netherby': (-34.9681, 138.6289), 'urrbrae': (-34.9708, 138.6389),
    'hawthorn': (-34.9700, 138.6050), 'westbourne park': (-34.9700, 138.5950),
    'colonel light gardens': (-34.9767, 138.5917), 'cumberland park': (-34.9681, 138.5889),
    'clapham': (-34.9850, 138.6050), 'belair': (-34.9972, 138.6333),
    'blackwood': (-35.0194, 138.6167), 'eden hills': (-35.0139, 138.5972),
    'hawthorndene': (-35.0150, 138.6350), 'coromandel valley': (-35.0389, 138.6194),
    'bellevue heights': (-35.0200, 138.5750), 'glenalta': (-35.0100, 138.6250),
    'panorama': (-34.9900, 138.5950), 'pasadena': (-34.9950, 138.5850),
    'st marys': (-34.9950, 138.5750), 'daw park': (-34.9850, 138.5850),
    # Norwood / East / North-East Core
    'norwood': (-34.9214, 138.6339), 'kensington': (-34.9250, 138.6450),
    'st peters': (-34.9120, 138.6250), 'college park': (-34.9150, 138.6200),
    'hackney': (-34.9150, 138.6150), 'stepney': (-34.9150, 138.6300),
    'maylands': (-34.9180, 138.6350), 'trinity gardens': (-34.9150, 138.6450),
    'st morris': (-34.9180, 138.6550), 'heathpool': (-34.9250, 138.6500),
    'marryatville': (-34.9280, 138.6450), 'firle': (-34.9080, 138.6500),
    'payneham': (-34.9000, 138.6400), 'payneham south': (-34.9050, 138.6400),
    'felixstow': (-34.8950, 138.6400), 'marden': (-34.9000, 138.6300),
    'royston park': (-34.8980, 138.6250), 'joslin': (-34.8950, 138.6250),
    'evandale': (-34.9080, 138.6350), 'glynde': (-34.9000, 138.6550),
    'campbelltown': (-34.8889, 138.6611), 'newton': (-34.8806, 138.6833),
    'magill': (-34.9125, 138.6764), 'rostrevor': (-34.8986, 138.6853),
    'tranmere': (-34.9100, 138.6600), 'athelstone': (-34.8778, 138.7028),
    'paradise': (-34.8750, 138.6650), 'hectorville': (-34.9000, 138.6650),
    # Western Coastal
    'henley beach': (-34.9211, 138.5083), 'henley beach south': (-34.9350, 138.5100),
    'grange': (-34.9042, 138.4958), 'west beach': (-34.9489, 138.5069),
    'tennyson': (-34.8850, 138.4850), 'west lakes': (-34.8850, 138.5000),
    'west lakes shore': (-34.8750, 138.4900), 'semaphore park': (-34.8550, 138.4850),
    'lockleys': (-34.9278, 138.5444), 'fulham': (-34.9278, 138.5250),
    'fulham gardens': (-34.9150, 138.5250), 'kidman park': (-34.9139, 138.5417),
    'flinders park': (-34.9150, 138.5550), 'underdale': (-34.9250, 138.5600),
    'torrensville': (-34.9250, 138.5750), 'glenelg': (-34.9814, 138.5167),
    'glenelg south': (-34.9900, 138.5150), 'glenelg east': (-34.9850, 138.5250),
    'glenelg north': (-34.9700, 138.5150), 'somerton park': (-34.9944, 138.5250),
    'brighton': (-35.0189, 138.5208), 'north brighton': (-35.0100, 138.5200),
    'south brighton': (-35.0300, 138.5250), 'hove': (-35.0250, 138.5250),
    'kingston park': (-35.0400, 138.5200), 'seacliff': (-35.0389, 138.5222),
    'marino': (-35.0486, 138.5139),
    # Hills & Tea Tree Gully
    'crafers': (-34.9944, 138.7056), 'stirling': (-35.0083, 138.7194),
    'aldgate': (-35.0139, 138.7361), 'bridgewater': (-35.0056, 138.7667),
    'heathfield': (-35.0150, 138.7150), 'mylor': (-35.0450, 138.7550),
    'uraidla': (-34.9750, 138.7450), 'summertown': (-34.9650, 138.7350),
    'greenhill': (-34.9550, 138.6850), 'woodforde': (-34.9100, 138.7050),
    'golden grove': (-34.7833, 138.7167), 'greenwith': (-34.7722, 138.7306),
    'wynn vale': (-34.8050, 138.7150), 'redwood park': (-34.8150, 138.7050),
    'surrey downs': (-34.8050, 138.7350), 'ridgehaven': (-34.8250, 138.7150),
    'st agnes': (-34.8350, 138.7250), 'tea tree gully': (-34.8250, 138.7250),
    'highbury': (-34.8528, 138.6944), 'dernancourt': (-34.8600, 138.6750),
    'banksia park': (-34.8150, 138.7350)
}

REGIONS_CONFIG = {
    'City of Burnside & Core East': [
        'myrtle-bank-sa-5064', 'glenunga-sa-5064', 'toorak-gardens-sa-5065', 'dulwich-sa-5065',
        'rose-park-sa-5067', 'tusmore-sa-5065', 'hazelwood-park-sa-5066', 'burnside-sa-5066',
        'erindale-sa-5066', 'leabrook-sa-5068', 'linden-park-sa-5065', 'st-georges-sa-5064',
        'beaumont-sa-5066', 'stonyfell-sa-5066', 'wattle-park-sa-5066', 'glenside-sa-5065',
        'frewville-sa-5063', 'kensington-gardens-sa-5068', 'kensington-park-sa-5068', 'rosslyn-park-sa-5072',
        'beulah-park-sa-5067', 'auldana-sa-5072', 'mount-osmond-sa-5064', 'glen-osmond-sa-5064'
    ],
    'City of Unley & Prestige South': [
        'unley-sa-5061', 'unley-park-sa-5061', 'malvern-sa-5061', 'hyde-park-sa-5061',
        'millswood-sa-5034', 'kings-park-sa-5034', 'goodwood-sa-5034', 'wayville-sa-5034',
        'parkside-sa-5063', 'fullarton-sa-5063', 'highgate-sa-5063', 'black-forest-sa-5035',
        'clarence-park-sa-5034', 'everard-park-sa-5035', 'forestville-sa-5035'
    ],
    'City of Mitcham & Foothills': [
        'mitcham-sa-5062', 'lower-mitcham-sa-5062', 'kingswood-sa-5062', 'torrens-park-sa-5062',
        'netherby-sa-5062', 'urrbrae-sa-5064', 'hawthorn-sa-5062', 'westbourne-park-sa-5062',
        'colonel-light-gardens-sa-5041', 'cumberland-park-sa-5041', 'clapham-sa-5062',
        'belair-sa-5052', 'blackwood-sa-5051', 'eden-hills-sa-5050', 'hawthorndene-sa-5051',
        'coromandel-valley-sa-5051', 'bellevue-heights-sa-5050', 'glenalta-sa-5052',
        'panorama-sa-5041', 'pasadena-sa-5042', 'st-marys-sa-5042', 'daw-park-sa-5041'
    ],
    'Norwood, Campbelltown & North-East Core': [
        'norwood-sa-5067', 'kensington-sa-5068', 'st-peters-sa-5069', 'college-park-sa-5069',
        'hackney-sa-5069', 'stepney-sa-5069', 'maylands-sa-5069', 'trinity-gardens-sa-5068',
        'st-morris-sa-5068', 'heathpool-sa-5068', 'marryatville-sa-5068', 'firle-sa-5070',
        'payneham-sa-5070', 'payneham-south-sa-5070', 'felixstow-sa-5070', 'marden-sa-5070',
        'royston-park-sa-5070', 'joslin-sa-5070', 'evandale-sa-5069', 'glynde-sa-5070',
        'campbelltown-sa-5074', 'newton-sa-5074', 'magill-sa-5072', 'rostrevor-sa-5073',
        'tranmere-sa-5073', 'athelstone-sa-5076', 'paradise-sa-5075', 'hectorville-sa-5073'
    ],
    'Western Coastal Corridors': [
        'henley-beach-sa-5022', 'henley-beach-south-sa-5022', 'grange-sa-5022', 'west-beach-sa-5024',
        'tennyson-sa-5022', 'west-lakes-sa-5021', 'west-lakes-shore-sa-5020', 'semaphore-park-sa-5019',
        'lockleys-sa-5032', 'fulham-sa-5024', 'fulham-gardens-sa-5024', 'kidman-park-sa-5025',
        'flinders-park-sa-5025', 'underdale-sa-5032', 'torrensville-sa-5031', 'glenelg-sa-5045',
        'glenelg-south-sa-5045', 'glenelg-east-sa-5045', 'glenelg-north-sa-5045', 'somerton-park-sa-5044',
        'brighton-sa-5048', 'north-brighton-sa-5048', 'south-brighton-sa-5048', 'hove-sa-5048',
        'kingston-park-sa-5049', 'seacliff-sa-5049', 'marino-sa-5049'
    ],
    'Adelaide Hills & Tea Tree Gully Safe Enclaves': [
        'crafers-sa-5152', 'stirling-sa-5152', 'aldgate-sa-5154', 'bridgewater-sa-5155',
        'heathfield-sa-5153', 'mylor-sa-5153', 'uraidla-sa-5142', 'summertown-sa-5141',
        'greenhill-sa-5140', 'woodforde-sa-5072',
        'golden-grove-sa-5125', 'greenwith-sa-5125', 'wynn-vale-sa-5127', 'redwood-park-sa-5097',
        'surrey-downs-sa-5126', 'ridgehaven-sa-5097', 'st-agnes-sa-5097', 'tea-tree-gully-sa-5091',
        'highbury-sa-5089', 'dernancourt-sa-5075', 'banksia-park-sa-5091'
    ]
}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)

def get_distance(suburb_clean):
    for name, coords in SUBURB_COORDS.items():
        if name in suburb_clean or suburb_clean in name:
            return haversine(BASE_LAT, BASE_LON, coords[0], coords[1])
    return 7.5

def parse_sold_date(date_str):
    m = re.search(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', date_str)
    if m:
        day, month_str, year = m.groups()
        try:
            return datetime.strptime(f"{day} {month_str} {year}", "%d %b %Y").date()
        except Exception:
            return None
    return None

def normalize_address(addr):
    s = ' ' + re.sub(r'[^a-z0-9 ]', ' ', addr.lower()).strip() + ' '
    reps = {
        ' rd ': ' road ', ' av ': ' avenue ', ' ave ': ' avenue ', ' st ': ' street ',
        ' dr ': ' drive ', ' ct ': ' court ', ' pl ': ' place ', ' pde ': ' parade ',
        ' cr ': ' crescent ', ' cres ': ' crescent ', ' tce ': ' terrace ', ' hwy ': ' highway '
    }
    for k, v in reps.items():
        s = s.replace(k, v)
    return ' '.join(s.split())

def classify_property_type(addr, land_str, beds):
    addr_l = (addr or '').lower()
    land_l = (land_str or '').lower()
    b = beds or 3
    if re.search(r'\b(apt|apartment)\b', addr_l) or re.search(r'^\d{3,}/', addr_l):
        return 'Apartment'
    if re.search(r'\b(townhouse|th)\b', addr_l):
        return 'Townhouse'
    if re.search(r'\b(unit|villa|flat)\b', addr_l):
        if b >= 3 and ('m2' in land_l or 'm²' in land_l):
            return 'Townhouse'
        return 'Unit'
    m_slash = re.search(r'^(\d+)[a-z]?/(\d+)', addr_l)
    if m_slash:
        unit_num = int(m_slash.group(1))
        if unit_num >= 100:
            return 'Apartment'
        if b <= 2:
            return 'Unit'
        elif b == 3:
            return 'Townhouse'
        else:
            return 'House'
    m_letter = re.search(r'^\d+[a-f]\b', addr_l)
    if m_letter and b <= 3:
        if 'm²' in land_l or 'm2' in land_l:
            m_a = re.search(r'(\d+)', land_l.replace(',', ''))
            if m_a and int(m_a.group(1)) < 300:
                return 'Townhouse'
    if 'm²' in land_l or 'm2' in land_l:
        m_a = re.search(r'(\d+)', land_l.replace(',', ''))
        if m_a:
            area = int(m_a.group(1))
            if area < 180 and b <= 2:
                return 'Unit'
            elif area < 320 and b <= 3:
                return 'Townhouse'
            else:
                return 'House'
    if b == 1:
        return 'Unit'
    return 'House'

def load_known_auctions():
    known_auctions = set()
    if AUCTION_JSON.exists():
        try:
            with open(AUCTION_JSON, 'r', encoding='utf-8') as f:
                d = json.load(f)
                for l in d.get('listings', []):
                    clean = normalize_address(l.get('address', ''))
                    if clean:
                        known_auctions.add(clean)
        except Exception as e:
            print(f"Warning reading auction json: {e}")
    return known_auctions

def scrape_suburb_sold(slug, region_name):
    listings = []
    seen_urls = set()
    for page in [1, 2, 3]:
        p_str = '' if page == 1 else f'/page-{page}'
        url = f'https://www.homely.com.au/sold-properties/{slug}{p_str}?sort=newest'
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            html = urllib.request.urlopen(req, timeout=9).read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
        except Exception:
            break
            
        cards_found = 0
        for a in soup.find_all('a', href=re.compile(r'^/homes/')):
            try:
                href = a['href']
                if href in seen_urls: continue
                seen_urls.add(href)
                cards_found += 1
                
                card = a
                for _ in range(5):
                    if card.parent and len(card.parent.find_all('a', href=re.compile(r'^/homes/'))) == 1:
                        card = card.parent
                    else:
                        break
                
                chunks = list(card.stripped_strings)
                
                sold_chunk_idx = -1
                for i, c in enumerate(chunks):
                    if 'sold on' in c.lower():
                        sold_chunk_idx = i
                        break
                
                if sold_chunk_idx == -1:
                    continue
                    
                sold_date_str = chunks[sold_chunk_idx]
                sold_date_obj = parse_sold_date(sold_date_str)
                if not sold_date_obj or sold_date_obj.year < 2024:
                    continue
                
                # Price
                price_str = 'Price Undisclosed'
                price_val = None
                price_status = 'Undisclosed'
                for c in chunks[sold_chunk_idx:sold_chunk_idx+5]:
                    if '$' in c:
                        price_str = c
                        num_m = re.sub(r'[^\d]', '', c)
                        if num_m:
                            price_val = int(num_m)
                            price_status = 'Disclosed'
                        break
                    elif 'undisclosed' in c.lower() or 'contact agent' in c.lower():
                        price_str = 'Price Undisclosed'
                        price_status = 'Undisclosed'
                        break
                
                # Address & Suburb
                addr_chunks = [c for c in chunks if 'SA 50' in c or 'SA 51' in c or 'SA 52' in c]
                full_addr = addr_chunks[0] if addr_chunks else ''
                if full_addr:
                    idx = chunks.index(full_addr)
                    if idx > 0 and not any(k in chunks[idx-1].lower() for k in ['sold', '$', 'undisclosed', 'rated', 'contact']):
                        full_addr = f"{chunks[idx-1]} {full_addr}"
                
                if not full_addr:
                    continue
                    
                suburb_raw = slug.split('-sa-')[0].replace('-', ' ').title()
                
                # Specs: beds, baths, cars, land
                beds, baths, cars, land = None, None, None, ''
                spec_candidates = []
                for c in chunks:
                    if re.match(r'^\d+$', c) and len(c) <= 2:
                        spec_candidates.append(int(c))
                    elif 'm²' in c or 'm\xb2' in c or 'm2' in c:
                        land = c
                
                if len(spec_candidates) >= 1: beds = spec_candidates[0]
                if len(spec_candidates) >= 2: baths = spec_candidates[1]
                if len(spec_candidates) >= 3: cars = spec_candidates[2]
                
                dist = get_distance(suburb_raw.lower())
                ptype = classify_property_type(full_addr, land or '', beds or 3)
                
                listings.append({
                    'id': href.split('/')[-1],
                    'address': full_addr,
                    'suburb': suburb_raw,
                    'region': region_name,
                    'property_type': ptype,
                    'sold_date': str(sold_date_obj),
                    'sold_date_formatted': sold_date_obj.strftime("%d/%m/%Y"),
                    'price_val': price_val,
                    'price_str': price_str,
                    'price_status': price_status,
                    'sale_type': 'Private Treaty',  # Will cross-reference with auctions
                    'bedrooms': beds or 3,
                    'bathrooms': baths or 1,
                    'carspaces': cars or 1,
                    'land_size': land or 'N/A',
                    'distance_km_from_wilgena': dist,
                    'homely_url': f'https://www.homely.com.au{href}'
                })
            except Exception:
                continue
                
        if cards_found == 0:
            break
            
    return listings

def main():
    print("=== STARTING ADELAIDE RECENTLY SOLD PROPERTIES SCRAPER (PRIVATE TREATY + AUCTION) ===")
    known_auctions = load_known_auctions()
    print(f"Loaded {len(known_auctions)} known auction properties for cross-referencing.")
    
    suburb_region_pairs = []
    for reg, slugs in REGIONS_CONFIG.items():
        for s in slugs:
            suburb_region_pairs.append((s, reg))
            
    print(f"Crawling recently sold listings across {len(suburb_region_pairs)} safe suburbs in Greater Adelaide...")
    
    all_sold_listings = []
    seen_addresses = set()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scrape_suburb_sold, s, reg): (s, reg) for s, reg in suburb_region_pairs}
        for future in as_completed(futures):
            results = future.result()
            for item in results:
                addr_clean = normalize_address(item['address'])
                if addr_clean in seen_addresses:
                    continue
                seen_addresses.add(addr_clean)
                
                # Cross-reference with known auctions
                is_auction = False
                for a_addr in known_auctions:
                    if a_addr in addr_clean or addr_clean in a_addr or (a_addr.split()[:3] == addr_clean.split()[:3] and len(a_addr.split()) >= 3):
                        is_auction = True
                        break
                        
                if is_auction:
                    item['sale_type'] = 'Auction (Đấu giá)'
                else:
                    item['sale_type'] = 'Private Treaty (Bán thỏa thuận)'
                    
                all_sold_listings.append(item)
                
    # Sort by sold date descending
    all_sold_listings.sort(key=lambda x: (x['sold_date'], x.get('price_val') or 0), reverse=True)
    
    # Calculate statistics
    now_date = date.today()
    date_7d = str(now_date - timedelta(days=7))
    date_14d = str(now_date - timedelta(days=14))
    date_30d = str(now_date - timedelta(days=30))
    
    sold_7d = [x for x in all_sold_listings if x['sold_date'] >= date_7d]
    sold_14d = [x for x in all_sold_listings if x['sold_date'] >= date_14d]
    sold_30d = [x for x in all_sold_listings if x['sold_date'] >= date_30d]
    
    disclosed_prices = [x['price_val'] for x in all_sold_listings if x['price_val']]
    median_price = int(sorted(disclosed_prices)[len(disclosed_prices)//2]) if disclosed_prices else 0
    
    private_treaty_count = sum(1 for x in all_sold_listings if 'Private Treaty' in x['sale_type'])
    auction_count = sum(1 for x in all_sold_listings if 'Auction' in x['sale_type'])
    disclosed_count = len(disclosed_prices)
    undisclosed_count = len(all_sold_listings) - disclosed_count
    
    summary = {
        'last_updated': datetime.now().isoformat(),
        'total_sold_all_2026': len(all_sold_listings),
        'total_sold_last_7_days': len(sold_7d),
        'total_sold_last_14_days': len(sold_14d),
        'total_sold_last_30_days': len(sold_30d),
        'private_treaty_count': private_treaty_count,
        'auction_count': auction_count,
        'disclosed_price_count': disclosed_count,
        'undisclosed_price_count': undisclosed_count,
        'median_sold_price': median_price,
        'min_sold_price': min(disclosed_prices) if disclosed_prices else 0,
        'max_sold_price': max(disclosed_prices) if disclosed_prices else 0
    }
    
    data_to_save = {
        'summary': summary,
        'listings': all_sold_listings
    }
    
    # Save JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        
    # Save CSV
    fieldnames = [
        'id', 'sold_date', 'sold_date_formatted', 'address', 'suburb', 'region',
        'property_type', 'sale_type', 'price_status', 'price_val', 'price_str',
        'bedrooms', 'bathrooms', 'carspaces', 'land_size',
        'distance_km_from_wilgena', 'homely_url'
    ]
    with open(OUTPUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in all_sold_listings:
            writer.writerow(item)
            
    print(f"\n=== RESULTS ===")
    print(f"Total sold properties tracked: {len(all_sold_listings)}")
    print(f"- Sold in last 7 days: {len(sold_7d)}")
    print(f"- Sold in last 14 days: {len(sold_14d)}")
    print(f"- Sold in last 30 days: {len(sold_30d)}")
    print(f"- Private Treaty sales: {private_treaty_count} ({round(private_treaty_count/max(len(all_sold_listings),1)*100, 1)}%)")
    print(f"- Auction sales: {auction_count} ({round(auction_count/max(len(all_sold_listings),1)*100, 1)}%)")
    print(f"- Disclosed prices: {disclosed_count} (Median: ${median_price:,} AUD)")
    print(f"JSON saved to: {OUTPUT_JSON}")
    print(f"CSV saved to: {OUTPUT_CSV}")

if __name__ == '__main__':
    main()
