import json

with open('d:/Looking for a home/data/expanded_safe_listings_under_1.2m.json', encoding='utf-8') as f:
    props = json.load(f)

regions = {}
for p in props:
    r = p['region']
    regions.setdefault(r, []).append(p)

for reg, p_list in regions.items():
    print(f"=== {reg} ({len(p_list)} properties) ===")
    sorted_p = sorted(p_list, key=lambda x: (x['price_min'] if x['price_min'] else 9999999))
    for p in sorted_p[:4]:
        addr = p['address']
        price = p['price_raw']
        ptype = p['property_type']
        land = p['land_size']
        zone = p['school_zone']
        url = p['url']
        print(f"  * {addr}")
        print(f"    Price: {price} | Type: {ptype} | Land: {land} | Zone: {zone}")
        print(f"    URL: {url}")
    print()
