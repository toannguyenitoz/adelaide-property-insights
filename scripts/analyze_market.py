import json
import statistics

with open('d:/Looking for a home/data/active_listings_under_1.2m.json', encoding='utf-8') as f:
    active = json.load(f)

with open('d:/Looking for a home/data/historical_sales_analysis.json', encoding='utf-8') as f:
    historical = json.load(f)

print(f"=== ACTIVE LISTINGS ANALYSIS ({len(active)} properties) ===")
suburbs_count = {}
types_count = {}
for p in active:
    sub = p['suburb'] if p['suburb'] else 'Unknown'
    suburbs_count[sub] = suburbs_count.get(sub, 0) + 1
    types_count[p['property_type']] = types_count.get(p['property_type'], 0) + 1

print("\nActive Properties By Suburb:")
for s, c in sorted(suburbs_count.items(), key=lambda x: -x[1]):
    print(f"  - {s}: {c} properties")

print("\nActive Properties By Type:")
for t, c in types_count.items():
    print(f"  - {t}: {c} properties")

print("\n--- ALL ACTIVE 3-BEDROOM PROPERTIES UNDER $1.2M ---")
for idx, p in enumerate(active, 1):
    gihs = "[GIHS ZONE]" if any("GIHS" in h for h in p['high_schools']) else ""
    unley = "[UNLEY HIGH]" if any("Unley High" in h for h in p['high_schools']) else ""
    schools = f"{gihs} {unley}".strip()
    print(f"{idx}. {p['address']}")
    print(f"   Distance: {p['distance_km_from_wilgena']} km | Type: {p['property_type']} | Land: {p['land_size']}")
    print(f"   Price: {p['price_raw']}")
    print(f"   Schools: {schools} | High: {p['high_schools']} | Primary: {p['primary_schools']}")
    print(f"   URL: {p['url']}")
    print()

print(f"\n=== HISTORICAL SALES ANALYSIS ({len(historical)} properties) ===")
suburb_prices = {}
for h in historical:
    sub = h['suburb'] if h['suburb'] else 'Unknown'
    price = h['sold_price_num']
    if price and price > 400000: # filter valid house/unit prices
        suburb_prices.setdefault(sub, []).append(price)

print("\nMedian Sold Prices (3 Bedrooms) by Suburb:")
for s, prices in sorted(suburb_prices.items(), key=lambda x: statistics.median(x[1])):
    med = statistics.median(prices)
    avg = statistics.mean(prices)
    count = len(prices)
    print(f"  - {s} ({count} sales): Median ${med:,.0f} | Range: ${min(prices):,.0f} - ${max(prices):,.0f}")
