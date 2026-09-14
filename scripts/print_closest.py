import json

with open('d:/Looking for a home/data/active_listings_under_1.2m.json', encoding='utf-8') as f:
    active = json.load(f)

for idx, p in enumerate(active[:27], 1):
    schools = '; '.join(p['high_schools'])
    dist = p['distance_km_from_wilgena']
    addr = p['address']
    price = p['price_raw']
    ptype = p['property_type']
    land = p['land_size']
    url = p['url']
    print(f"{idx}. [{dist} km] {addr}")
    print(f"   Price: {price} | Type: {ptype} | Land: {land}")
    print(f"   Schools: {schools}")
    print(f"   URL: {url}")
