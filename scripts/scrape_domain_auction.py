import pathlib
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

OUTPUT_JSON = BASE_DIR / 'data/domain_weekly_auction_results.json'

async def scrape_domain_auction():
    print("=== STARTING DOMAIN ADELAIDE WEEKLY AUCTION SCRAPER ===", flush=True)
    url = "https://www.domain.com.au/auction-results/adelaide/"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        
        print(f"Navigating to {url}...", flush=True)
        try:
            resp = await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            if resp and resp.status != 200:
                print(f"Warning: Response status {resp.status}", file=sys.stderr)
        except Exception as e:
            print(f"Error loading page: {e}", file=sys.stderr)
            await browser.close()
            return False

        # Extract __NEXT_DATA__
        next_data = await page.evaluate('''() => {
            const el = document.getElementById('__NEXT_DATA__');
            return el ? JSON.parse(el.innerText) : null;
        }''')
        
        await browser.close()

    if not next_data:
        print("Failed to locate __NEXT_DATA__ from Domain page!", file=sys.stderr)
        return False

    props = next_data.get('props', {}).get('pageProps', {}).get('componentProps', {})
    
    auction_date = props.get('auctionDate', '')
    published_date = props.get('publishedDate', '')
    city_summary = props.get('citySummaryData', {})
    sales_listings_raw = props.get('salesListings', [])
    historical_dates = props.get('historicalAuctionDates', [])

    # Flatten individual property results
    flattened_listings = []
    result_labels = {
        'AUSD': 'Sold at Auction (Đã bán tại đấu giá)',
        'AUSP': 'Sold Prior to Auction (Đã bán trước đấu giá)',
        'AUPI': 'Passed In (Không đạt giá kỳ vọng / Không bán được)',
        'AUW': 'Withdrawn (Rút khỏi đấu giá)',
        'AUSA': 'Sold After Auction (Đã bán sau đấu giá)',
        'SN': 'Sold Price Not Disclosed'
    }

    for group in sales_listings_raw:
        suburb = group.get('suburb', '')
        for item in group.get('listings', []):
            code = item.get('result', '')
            street_num = item.get('streetNumber', '')
            unit_num = item.get('unitNumber', '')
            street_name = item.get('streetName', '')
            street_type = item.get('streetType', '')
            
            full_street = f"{unit_num}/{street_num}" if unit_num else street_num
            address_str = f"{full_street} {street_name} {street_type}".strip() + f", {suburb} SA {item.get('postcode', '')}"

            flattened_listings.append({
                'address': address_str,
                'suburb': suburb,
                'postcode': item.get('postcode', ''),
                'property_type': item.get('propertyType', 'House'),
                'bedrooms': item.get('bedrooms'),
                'bathrooms': item.get('bathrooms'),
                'carspaces': item.get('carspaces'),
                'price': item.get('price'),
                'result_code': code,
                'result_label': result_labels.get(code, code),
                'agency': item.get('agencyName', ''),
                'domain_url': item.get('domainPropertyDetailsUrl') or (f"https://www.domain.com.au/{item.get('domainId')}" if item.get('domainId') else '')
            })

    output_data = {
        'city': 'Adelaide',
        'auction_date': auction_date,
        'published_date': published_date,
        'summary': city_summary,
        'historical_dates': historical_dates,
        'total_properties_recorded': len(flattened_listings),
        'listings': flattened_listings
    }

    os.makedirs(OUTPUT_JSON.parent, exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Auction results saved successfully to {OUTPUT_JSON}!")
    print(f"Summary: Clearance Rate = {city_summary.get('adjClearanceRate', 0)*100:.1f}%, Median = ${city_summary.get('median', 0):,}, Total Sales = ${city_summary.get('totalSales', 0):,}, Listed = {city_summary.get('numberListedForAuction')}, Sold = {city_summary.get('numberSold')}")
    return True

def main():
    success = asyncio.run(scrape_domain_auction())
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
