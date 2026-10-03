import pathlib
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
import json
import os
import datetime
import re
from markdown_it import MarkdownIt

DATA_JSON = str(BASE_DIR / 'data/expanded_safe_listings_under_1.2m.json')
AUCTION_JSON = str(BASE_DIR / 'data/domain_weekly_auction_results.json')
RECENTLY_SOLD_JSON = str(BASE_DIR / 'data/recently_sold_properties.json')
MD_REPORT = str(BASE_DIR / 'reports/real_estate_market_report.md')
OUTPUT_INDEX = str(BASE_DIR / 'index.html')

def get_rendered_report_html():
    if not os.path.exists(MD_REPORT):
        return "<p>Báo cáo chưa sẵn sàng.</p>"

    with open(MD_REPORT, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Replace relative chart links to point to reports/charts/ with cache buster
    ts = int(datetime.datetime.now().timestamp())
    md_text = re.sub(r'\(charts/([a-zA-Z0-9_]+)\.png\)', rf'(reports/charts/\1.png?v={ts})', md_text)
    md_text = md_text.replace('(charts/', '(reports/charts/')

    md = MarkdownIt('gfm-like', {'html': True, 'linkify': False})
    rendered_html = md.render(md_text)

    # Slugs for each chapter
    slug_map = {
        '1': 'chuong-1-tong-quan',
        '2': 'chuong-2-suburb-thuong-luu',
        '3': 'chuong-3-bo-loc-an-ninh-sapol',
        '4': 'chuong-4-he-thong-8-bieu-do',
        '5': 'chuong-5-phan-bien-kinh-te-do-thi',
        '6': 'chuong-6-phan-tich-6-hanh-lang',
        '7': 'chuong-7-so-sanh-chi-phi-house-townhouse-unit',
        '8': 'chuong-8-huong-dan-thuc-chien-phap-ly-solar',
        '9': 'chuong-9-danh-gia-chien-luoc-mua-hay-doi',
        '10': 'chuong-10-top-bat-dong-san-form-1'
    }

    # Add id and styling to H2 elements
    def replace_h2(match):
        num = match.group(1)
        title = match.group(2)
        slug = slug_map.get(num, f'chuong-{num}')
        return f'<h2 id="{slug}" class="report-h2"><span class="report-chap-badge">Chương {num}</span> {title}</h2>'

    rendered_html = re.sub(r'<h2>(\d+)\.\s*(.*?)</h2>', replace_h2, rendered_html)

    # Wrap tables in responsive wrapper
    rendered_html = re.sub(
        r'(<table>[\s\S]*?</table>)',
        r'<div class="report-table-wrapper">\1</div>',
        rendered_html
    )

    # Enhance math formula presentation
    rendered_html = re.sub(
        r'\$\$([\s\S]*?)\$\$',
        r'<div class="report-math-box"><code>\1</code></div>',
        rendered_html
    )

    return rendered_html

def build():
    with open(DATA_JSON, 'r', encoding='utf-8') as f:
        properties = json.load(f)

    # Sort by distance
    properties.sort(key=lambda x: (x.get('distance_km_from_wilgena', 99), x.get('price_min') or 9999999))

    total_listings = len(properties)
    prices = [p['price_min'] for p in properties if p.get('price_min')]
    median_price = int(sorted(prices)[len(prices)//2]) if prices else 890000

    now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    # Load Domain Auction Data
    auction_data = {}
    if os.path.exists(AUCTION_JSON):
        try:
            with open(AUCTION_JSON, 'r', encoding='utf-8') as f_auc:
                auction_data = json.load(f_auc)
        except Exception:
            pass

    auc_summary = auction_data.get('summary', {})
    auc_listings = auction_data.get('listings', [])
    auc_clearance = auc_summary.get('adjClearanceRate', 0.392) * 100
    auc_last_year = auc_summary.get('lastYearClearanceRate', 0.477) * 100
    auc_median = auc_summary.get('median', 917750)
    auc_total_sales = auc_summary.get('totalSales', 21721500)
    auc_listed = auc_summary.get('numberListedForAuction', 103)
    auc_sold = auc_summary.get('numberSold', 31)
    auc_passed_in = auc_summary.get('numberPassedIn', 40)
    auc_withdrawn = auc_summary.get('numberWithdrawn', 8)
    auc_date_raw = auction_data.get('auction_date', '2026-09-26')
    try:
        auc_date_str = datetime.datetime.fromisoformat(auc_date_raw.replace('Z', '')).strftime('%d/%m/%Y')
    except Exception:
        auc_date_str = '26/09/2026'

    # Load Recently Sold Data (Private Treaty + Auction)
    sold_data = {}
    if os.path.exists(RECENTLY_SOLD_JSON):
        try:
            with open(RECENTLY_SOLD_JSON, 'r', encoding='utf-8') as f_sold:
                sold_data = json.load(f_sold)
        except Exception:
            pass

    sold_summary = sold_data.get('summary', {})
    sold_listings = sold_data.get('listings', [])
    sold_total_30d = sold_summary.get('total_sold_last_30_days', 257)
    sold_total_7d = sold_summary.get('total_sold_last_7_days', 32)
    sold_total_14d = sold_summary.get('total_sold_last_14_days', 103)
    sold_median = sold_summary.get('median_sold_price', 1150000)
    sold_pt_count = sold_summary.get('private_treaty_count', 2237)
    sold_auc_count = sold_summary.get('auction_count', 10)
    sold_disclosed_count = sold_summary.get('disclosed_price_count', 1234)
    sold_total_all = sold_summary.get('total_sold_all_2026', len(sold_listings))

    properties_json_str = json.dumps(properties, ensure_ascii=False)
    auction_listings_json_str = json.dumps(auc_listings, ensure_ascii=False)
    sold_listings_json_str = json.dumps(sold_listings, ensure_ascii=False)
    report_html = get_rendered_report_html()

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Toan Nguyen IT OZ | Cổng Thông Tin Bất Động Sản Greater Adelaide</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #1e3a8a;
      --primary-dark: #0f172a;
      --accent: #2563eb;
      --cyan: #0284c7;
      --emerald: #059669;
      --amber: #d97706;
      --rose: #e11d48;
      --slate-50: #f8fafc;
      --slate-100: #f1f5f9;
      --slate-200: #e2e8f0;
      --slate-600: #475569;
      --slate-700: #334155;
      --slate-900: #0f172a;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      background-color: #f8fafc;
      color: var(--slate-700);
      line-height: 1.55;
    }}
    a {{ color: var(--accent); text-decoration: none; }}
    
    /* Navbar */
    .navbar {{
      background: rgba(15, 23, 42, 0.95);
      backdrop-filter: blur(10px);
      color: white;
      padding: 14px 24px;
      position: sticky;
      top: 0;
      z-index: 100;
      border-bottom: 1px solid rgba(255,255,255,0.1);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .nav-brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .brand-title {{
      font-size: 19px;
      font-weight: 800;
      letter-spacing: 0.5px;
      color: #38bdf8;
    }}
    .brand-sub {{
      font-size: 11px;
      color: #94a3b8;
      display: block;
    }}
    .nav-actions {{
      display: flex;
      gap: 12px;
      align-items: center;
    }}
    .btn-pdf {{
      background: linear-gradient(135deg, #2563eb, #1d4ed8);
      color: white;
      padding: 8px 16px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: none;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(37,99,235,0.3);
      transition: all 0.2s;
    }}
    .btn-pdf:hover {{
      background: #1e40af;
      transform: translateY(-1px);
    }}
    
    /* Hero Banner */
    .hero {{
      background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 60%, #1d4ed8 100%);
      color: white;
      padding: 48px 24px;
      text-align: center;
      position: relative;
    }}
    .hero-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(255,255,255,0.12);
      padding: 5px 14px;
      border-radius: 20px;
      font-size: 11.5px;
      font-weight: 600;
      margin-bottom: 16px;
      border: 1px solid rgba(255,255,255,0.2);
    }}
    .hero h1 {{
      font-size: 30px;
      font-weight: 800;
      max-width: 850px;
      margin: 0 auto 12px auto;
      line-height: 1.25;
    }}
    .hero p {{
      font-size: 14.5px;
      color: #cbd5e1;
      max-width: 700px;
      margin: 0 auto 24px auto;
    }}
    
    /* Stats Bar */
    .stats-container {{
      max-width: 1200px;
      margin: -24px auto 32px auto;
      padding: 0 16px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      position: relative;
      z-index: 10;
    }}
    .stat-card {{
      background: white;
      padding: 18px 20px;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.06);
      border: 1px solid var(--slate-200);
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .stat-icon {{
      width: 44px;
      height: 44px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
    }}
    .stat-val {{
      font-size: 20px;
      font-weight: 800;
      color: var(--slate-900);
    }}
    .stat-lbl {{
      font-size: 11.5px;
      color: var(--slate-600);
      font-weight: 600;
    }}
    
    /* Main Layout */
    .main-wrapper {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 0 16px 60px 16px;
    }}
    
    /* Filter Bar */
    .filter-card {{
      background: white;
      padding: 20px;
      border-radius: 12px;
      border: 1px solid var(--slate-200);
      box-shadow: 0 2px 10px rgba(0,0,0,0.03);
      margin-bottom: 24px;
    }}
    .filter-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      margin-bottom: 14px;
    }}
    .region-pills {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .pill-btn {{
      padding: 6px 14px;
      border-radius: 20px;
      border: 1px solid var(--slate-200);
      background: var(--slate-50);
      color: var(--slate-700);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .pill-btn:hover, .pill-btn.active {{
      background: var(--primary);
      color: white;
      border-color: var(--primary);
    }}
    .filter-inputs {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      width: 100%;
    }}
    .search-input, .select-input {{
      padding: 8px 12px;
      border-radius: 8px;
      border: 1px solid var(--slate-200);
      font-size: 12.5px;
      font-family: inherit;
      outline: none;
    }}
    .search-input {{ flex: 1; min-width: 200px; }}
    .select-input {{ min-width: 160px; }}
    
    /* Property Grid */
    .grid-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }}
    .grid-title {{
      font-size: 18px;
      font-weight: 800;
      color: var(--slate-900);
    }}
    .property-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 20px;
    }}
    .property-card {{
      background: white;
      border-radius: 12px;
      border: 1px solid var(--slate-200);
      overflow: hidden;
      box-shadow: 0 2px 10px rgba(0,0,0,0.03);
      display: flex;
      flex-direction: column;
      transition: all 0.2s;
    }}
    .property-card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.08);
      border-color: #93c5fd;
    }}
    .card-head {{
      padding: 14px 16px;
      border-bottom: 1px solid var(--slate-100);
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 8px;
    }}
    .card-region {{
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--cyan);
      margin-bottom: 2px;
    }}
    .card-address {{
      font-size: 14.5px;
      font-weight: 800;
      color: var(--slate-900);
      line-height: 1.3;
    }}
    .card-badge-safe {{
      background: #ecfdf5;
      color: var(--emerald);
      border: 1px solid #a7f3d0;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 10px;
      font-weight: 700;
      white-space: nowrap;
    }}
    .card-body {{
      padding: 14px 16px;
      flex: 1;
    }}
    .card-price {{
      font-size: 18px;
      font-weight: 800;
      color: var(--rose);
      margin-bottom: 10px;
    }}
    .card-features {{
      display: flex;
      gap: 12px;
      font-size: 12px;
      color: var(--slate-600);
      margin-bottom: 12px;
      padding-bottom: 10px;
      border-bottom: 1px solid var(--slate-100);
    }}
    .feat-item {{
      display: flex;
      align-items: center;
      gap: 4px;
      font-weight: 600;
    }}
    .card-tags {{
      display: flex;
      flex-direction: column;
      gap: 6px;
      font-size: 11.5px;
    }}
    .tag-row {{
      display: flex;
      align-items: flex-start;
      gap: 6px;
    }}
    .tag-label {{
      font-weight: 700;
      color: var(--slate-700);
      min-width: 75px;
    }}
    .card-foot {{
      padding: 12px 16px;
      background: var(--slate-50);
      border-top: 1px solid var(--slate-100);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .card-dist {{
      font-size: 11.5px;
      font-weight: 700;
      color: var(--primary);
    }}
    .btn-group-foot {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .btn-homely {{
      background: #0ea5e9;
      color: white;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: all 0.15s;
    }}
    .btn-homely:hover {{
      background: #0284c7;
      color: white;
      box-shadow: 0 2px 6px rgba(14,165,233,0.35);
    }}
    .btn-domain {{
      background: #f8fafc;
      color: #00875a;
      border: 1px solid #86efac;
      padding: 5px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 3px;
      transition: all 0.15s;
    }}
    .btn-domain:hover {{
      background: #ecfdf5;
      color: #006644;
      border-color: #00875a;
    }}
    
    .btn-calc {{
      background: #7c3aed;
      color: white;
      border: none;
      padding: 6px 11px;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      cursor: pointer;
      transition: all 0.15s;
      text-decoration: none;
    }}
    .btn-calc:hover {{
      background: #6d28d9;
      color: white;
      box-shadow: 0 2px 6px rgba(124,58,237,0.35);
    }}
    .floating-calc-btn {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
      color: white;
      font-weight: 800;
      font-size: 13px;
      padding: 12px 18px;
      border-radius: 30px;
      border: 2px solid white;
      box-shadow: 0 8px 24px rgba(124, 58, 237, 0.45);
      cursor: pointer;
      z-index: 999;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
    }}
    .floating-calc-btn:hover {{
      transform: translateY(-3px) scale(1.03);
      box-shadow: 0 12px 30px rgba(124, 58, 237, 0.6);
    }}
    /* Mortgage Modal Styling */
    .modal-overlay {{
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(15, 23, 42, 0.75);
      backdrop-filter: blur(6px);
      z-index: 10000;
      justify-content: center;
      align-items: center;
      padding: 16px;
      overflow-y: auto;
    }}
    .modal-overlay.active {{
      display: flex;
    }}
    .modal-card {{
      background: white;
      border-radius: 16px;
      max-width: 980px;
      width: 100%;
      max-height: 92vh;
      overflow-y: auto;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
      border: 1px solid #e2e8f0;
      display: flex;
      flex-direction: column;
      animation: modalFadeIn 0.2s ease-out;
    }}
    @keyframes modalFadeIn {{
      from {{ opacity: 0; transform: scale(0.96); }}
      to {{ opacity: 1; transform: scale(1); }}
    }}
    .modal-header {{
      padding: 20px 24px;
      background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
      color: white;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-top-left-radius: 16px;
      border-top-right-radius: 16px;
    }}
    .modal-header h3 {{
      font-size: 18px;
      font-weight: 800;
      margin: 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .modal-close-btn {{
      background: rgba(255, 255, 255, 0.15);
      border: none;
      color: white;
      font-size: 22px;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s;
    }}
    .modal-close-btn:hover {{
      background: rgba(255, 255, 255, 0.3);
    }}
    .modal-body {{
      padding: 18px 20px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
      background: #f8fafc;
    }}
    @media (max-width: 820px) {{
      .modal-body {{
        grid-template-columns: 1fr;
      }}
    }}
    .calc-panel {{
      background: white;
      border-radius: 12px;
      padding: 16px 18px;
      border: 1px solid #e2e8f0;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .calc-group {{
      margin-bottom: 12px;
    }}
    .calc-label {{
      font-size: 12.5px;
      font-weight: 700;
      color: #334155;
      margin-bottom: 6px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .calc-input-wrapper {{
      position: relative;
      display: flex;
      align-items: center;
    }}
    .calc-input-prefix {{
      position: absolute;
      left: 12px;
      font-weight: 700;
      color: #64748b;
      font-size: 14px;
    }}
    .calc-input-suffix {{
      position: absolute;
      right: 12px;
      font-weight: 700;
      color: #64748b;
      font-size: 12px;
    }}
    .calc-input {{
      width: 100%;
      padding: 10px 48px 10px 28px;
      border: 1.5px solid #cbd5e1;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 700;
      color: #0f172a;
      outline: none;
      transition: border-color 0.15s;
    }}
    .calc-input:focus {{
      border-color: #0284c7;
      box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
    }}
    .calc-quick-btns {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      margin-top: 6px;
    }}
    .calc-pill {{
      background: #f1f5f9;
      border: 1px solid #cbd5e1;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      color: #475569;
      cursor: pointer;
      transition: all 0.15s;
    }}
    .calc-pill:hover, .calc-pill.active {{
      background: #e0f2fe;
      color: #0284c7;
      border-color: #0284c7;
    }}

    /* Analytics & Charts Section */
    .section-box {{
      background: white;
      border-radius: 12px;
      border: 1px solid var(--slate-200);
      padding: 28px;
      margin-top: 40px;
    }}
    .section-head {{
      margin-bottom: 20px;
    }}
    .section-head h2 {{
      font-size: 20px;
      font-weight: 800;
      color: var(--slate-900);
      margin-bottom: 4px;
    }}
    .chart-tabs {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 20px;
      border-bottom: 1px solid var(--slate-200);
      padding-bottom: 10px;
    }}
    .chart-tab-btn {{
      padding: 8px 16px;
      border-radius: 8px;
      border: 1px solid transparent;
      background: var(--slate-100);
      font-size: 12px;
      font-weight: 700;
      color: var(--slate-700);
      cursor: pointer;
      transition: all 0.2s;
    }}
    .chart-tab-btn.active {{
      background: var(--primary);
      color: white;
    }}
    .chart-display {{
      text-align: center;
    }}
    .chart-img {{
      max-width: 100%;
      height: auto;
      border-radius: 10px;
      border: 1px solid var(--slate-200);
      box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }}
    
    /* Content Articles */
    .article-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 20px;
      margin-top: 24px;
    }}
    .article-card {{
      background: var(--slate-50);
      padding: 20px;
      border-radius: 10px;
      border: 1px solid var(--slate-200);
    }}
    .article-card h3 {{
      font-size: 15px;
      font-weight: 800;
      color: var(--primary);
      margin-bottom: 10px;
    }}
    .article-card p, .article-card li {{
      font-size: 12px;
      color: var(--slate-700);
      margin-bottom: 8px;
    }}
    
    /* Full Report Styling (10 Chapters) */
    .full-report-container {{
      background: white;
      border-radius: 16px;
      border: 1px solid var(--slate-200);
      box-shadow: 0 10px 30px rgba(0,0,0,0.04);
      margin-top: 40px;
      margin-bottom: 30px;
      overflow: hidden;
    }}
    .report-hero-head {{
      background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 70%, #1d4ed8 100%);
      color: white;
      padding: 36px 32px;
      position: relative;
    }}
    .report-badge-top {{
      display: inline-block;
      background: rgba(56, 189, 248, 0.2);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.4);
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 12px;
    }}
    .report-hero-head h2 {{
      font-size: 24px;
      font-weight: 800;
      line-height: 1.3;
      margin-bottom: 8px;
      color: #ffffff;
    }}
    .report-hero-head p {{
      font-size: 13.5px;
      color: #cbd5e1;
      max-width: 850px;
      margin-bottom: 18px;
    }}
    .report-meta-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      align-items: center;
      font-size: 12px;
      color: #94a3b8;
      border-top: 1px solid rgba(255,255,255,0.15);
      padding-top: 14px;
    }}
    .report-meta-item strong {{
      color: white;
    }}
    .report-head-btns {{
      margin-left: auto;
      display: flex;
      gap: 10px;
    }}
    .report-action-btn {{
      padding: 7px 14px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: none;
      transition: all 0.2s;
    }}
    .report-btn-pdf {{
      background: #059669;
      color: white;
    }}
    .report-btn-pdf:hover {{
      background: #047857;
      color: white;
    }}
    .report-btn-print {{
      background: rgba(255,255,255,0.15);
      color: white;
      border: 1px solid rgba(255,255,255,0.3);
    }}
    .report-btn-print:hover {{
      background: rgba(255,255,255,0.25);
    }}

    /* Weekly Auction Section Styles */
    .auction-kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin-bottom: 22px;
    }}
    .auction-kpi-card {{
      background: white;
      border: 1px solid var(--slate-200);
      border-radius: 10px;
      padding: 16px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.03);
      position: relative;
      overflow: hidden;
    }}
    .auction-kpi-val {{
      font-size: 22px;
      font-weight: 800;
      color: var(--primary);
      margin-bottom: 2px;
    }}
    .auction-kpi-lbl {{
      font-size: 11.5px;
      font-weight: 600;
      color: var(--slate-600);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .auction-kpi-sub {{
      font-size: 11px;
      color: #64748b;
      margin-top: 4px;
    }}
    .badge-ausd {{
      background: #ecfdf5;
      color: #047857;
      border: 1px solid #a7f3d0;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      display: inline-block;
    }}
    .badge-ausp {{
      background: #eff6ff;
      color: #1d4ed8;
      border: 1px solid #bfdbfe;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      display: inline-block;
    }}
    .badge-aupi {{
      background: #fffbeb;
      color: #b45309;
      border: 1px solid #fde68a;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      display: inline-block;
    }}
    .badge-auw {{
      background: #fef2f2;
      color: #b91c1c;
      border: 1px solid #fecaca;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      display: inline-block;
    }}
    .badge-private-type {{
      background: #ecfdf5;
      color: #047857;
      border: 1px solid #a7f3d0;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      display: inline-block;
    }}
    .badge-auction-type {{
      background: #f5f3ff;
      color: #6d28d9;
      border: 1px solid #ddd6fe;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      display: inline-block;
    }}
    .auction-table-scroll {{
      max-height: 520px;
      overflow-y: auto;
      border: 1px solid var(--slate-200);
      border-radius: 10px;
      background: white;
    }}
    .auction-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12.5px;
      text-align: left;
    }}
    .auction-table th {{
      position: sticky;
      top: 0;
      background: #0f172a;
      color: white;
      padding: 10px 12px;
      font-weight: 700;
      z-index: 10;
      font-size: 11.5px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .auction-table td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--slate-100);
    }}
    .auction-table tr:hover {{
      background: #f8fafc;
    }}

    .chapter-nav-bar {{
      background: #f1f5f9;
      border-bottom: 1px solid var(--slate-200);
      padding: 10px 20px;
      display: flex;
      gap: 8px;
      overflow-x: auto;
      white-space: nowrap;
      position: sticky;
      top: 60px;
      z-index: 90;
    }}
    .chap-nav-pill {{
      padding: 6px 12px;
      background: white;
      border: 1px solid var(--slate-200);
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 700;
      color: var(--slate-700);
      text-decoration: none;
      transition: all 0.15s;
    }}
    .chap-nav-pill:hover {{
      background: var(--primary);
      color: white;
      border-color: var(--primary);
    }}
    .report-article-body {{
      padding: 36px 32px;
      font-size: 14.5px;
      line-height: 1.8;
      color: var(--slate-700);
    }}
    .report-article-body p {{
      margin-bottom: 14px;
    }}
    .report-article-body ul, .report-article-body ol {{
      margin-bottom: 16px;
      padding-left: 24px;
    }}
    .report-article-body li {{
      margin-bottom: 6px;
    }}
    .report-h2 {{
      font-size: 20px;
      font-weight: 800;
      color: var(--slate-900);
      border-bottom: 2px solid var(--slate-200);
      padding-bottom: 8px;
      margin-top: 40px;
      margin-bottom: 16px;
      scroll-margin-top: 120px;
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .report-chap-badge {{
      background: var(--primary);
      color: white;
      font-size: 11.5px;
      font-weight: 800;
      padding: 3px 9px;
      border-radius: 6px;
      letter-spacing: 0.5px;
    }}
    .report-article-body h3 {{
      font-size: 16px;
      font-weight: 800;
      color: var(--primary);
      margin-top: 24px;
      margin-bottom: 10px;
      scroll-margin-top: 120px;
    }}
    .report-article-body h4 {{
      font-size: 14.5px;
      font-weight: 700;
      color: var(--cyan);
      margin-top: 18px;
      margin-bottom: 6px;
    }}
    .report-article-body hr {{
      border: none;
      border-top: 1px dashed var(--slate-200);
      margin: 36px 0;
    }}
    .report-article-body strong {{
      color: var(--slate-900);
      font-weight: 700;
    }}
    .report-article-body code {{
      background: #eff6ff;
      color: #1d4ed8;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: Consolas, Monaco, monospace;
      font-size: 13px;
      font-weight: 600;
    }}
    .report-math-box {{
      background: #f8fafc;
      border-left: 4px solid var(--accent);
      padding: 14px 18px;
      border-radius: 0 8px 8px 0;
      margin: 18px 0;
    }}
    .report-math-box code {{
      background: transparent;
      padding: 0;
      font-size: 15px;
      font-weight: 700;
      color: var(--primary);
    }}
    .report-table-wrapper {{
      width: 100%;
      overflow-x: auto;
      margin: 20px 0;
      border-radius: 8px;
      border: 1px solid var(--slate-200);
    }}
    .report-article-body table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      text-align: left;
    }}
    .report-article-body th {{
      background: var(--primary);
      color: white;
      padding: 10px 12px;
      font-weight: 700;
      white-space: nowrap;
    }}
    .report-article-body td {{
      padding: 9px 12px;
      border-bottom: 1px solid var(--slate-100);
    }}
    .report-article-body tr:nth-child(even) {{
      background: var(--slate-50);
    }}
    .report-article-body tr:hover {{
      background: #eff6ff;
    }}
    .report-article-body img {{
      max-width: 100%;
      height: auto;
      border-radius: 10px;
      border: 1px solid var(--slate-200);
      margin: 16px 0;
      box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }}
    .nav-links {{
      display: flex;
      gap: 6px;
      align-items: center;
    }}
    .nav-link {{
      color: #cbd5e1;
      font-size: 12px;
      font-weight: 600;
      padding: 6px 12px;
      border-radius: 6px;
      transition: all 0.2s;
    }}
    .nav-link:hover {{
      color: white;
      background: rgba(255,255,255,0.1);
    }}
    .nav-link-highlight {{
      color: #38bdf8;
      background: rgba(56, 189, 248, 0.12);
      border: 1px solid rgba(56, 189, 248, 0.25);
    }}
    .hero-buttons {{
      display: flex;
      justify-content: center;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 16px;
    }}
    .hero-btn {{
      padding: 9px 20px;
      border-radius: 8px;
      font-size: 12.5px;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }}
    .hero-btn-primary {{
      background: #38bdf8;
      color: #0f172a;
    }}
    .hero-btn-primary:hover {{
      background: #7dd3fc;
      transform: translateY(-2px);
      color: #0f172a;
    }}
    .hero-btn-secondary {{
      background: rgba(255,255,255,0.15);
      color: white;
      border: 1px solid rgba(255,255,255,0.3);
    }}
    .hero-btn-secondary:hover {{
      background: rgba(255,255,255,0.25);
      transform: translateY(-2px);
      color: white;
    }}
    
    /* Footer */
    footer {{
      background: var(--slate-900);
      color: #94a3b8;
      padding: 40px 20px;
      text-align: center;
      font-size: 12px;
      margin-top: 60px;
      border-top: 1px solid rgba(255,255,255,0.1);
    }}
    footer strong {{ color: white; }}

    @media (max-width: 768px) {{
      .nav-links {{ display: none; }}
      .report-hero-head h2 {{ font-size: 20px; }}
      .report-article-body {{ padding: 20px 14px; }}
      .report-head-btns {{ width: 100%; margin-top: 10px; }}
      .hero h1 {{ font-size: 24px; }}
    }}
  </style>
</head>
<body>

  <!-- Navbar -->
  <nav class="navbar">
    <a href="#" class="nav-brand" style="text-decoration:none;">
      <div>
        <span class="brand-title">TOAN NGUYEN IT OZ</span>
        <span class="brand-sub">Adelaide Real Estate Intelligence &bull; Daily Automated Updates @ 6:00 AM ACST</span>
      </div>
    </a>
    <div class="nav-links">
      <a href="#propertySection" class="nav-link">🏡 Tìm Nhà ({total_listings})</a>
      <a href="#soldSection" class="nav-link" style="color:#10b981; font-weight:700;">🤝 Nhà Vừa Bán ({sold_total_30d})</a>
      <a href="#auctionSection" class="nav-link" style="color:#38bdf8;">🔨 Đấu Giá Tuần ({len(auc_listings)})</a>
      <a href="#analyticsSection" class="nav-link">📊 12 Biểu Đồ</a>
      <a href="javascript:void(0)" onclick="openMortgageModal('Mẫu Dự Toán Tài Chính', 1100000)" class="nav-link" style="color:#c084fc; font-weight:800; display:inline-flex; align-items:center; gap:4px;">🧮 Tính Vay Mua Nhà</a>
      <a href="#economicsSection" class="nav-link">🏛️ Kinh Tế Đô Thị</a>
      <a href="#fullReportSection" class="nav-link nav-link-highlight">📖 Toàn Văn Báo Cáo (10 Chương)</a>
    </div>
    <div class="nav-actions">
      <a href="reports/Bao_Cao_Bat_Dong_San_Greater_Adelaide_Toan_Nguyen_IT_OZ_v2.pdf" download class="btn-pdf">
        📥 Tải Báo Cáo PDF (18 Trang)
      </a>
    </div>
  </nav>

  <!-- Hero -->
  <header class="hero">
    <div class="hero-badge">
      🛡️ Dữ Liệu Thực Tế Tuyển Chọn &bull; Loại Trừ Vùng Tội Phạm &bull; Cập nhật lúc {now_str}
    </div>
    <h1>CỔNG PHÂN TÍCH BẤT ĐỘNG SẢN AN TOÀN GREATER ADELAIDE</h1>
    <p>Hệ thống tự động quét và thẩm định {total_listings} nhà 3 phòng ngủ có giá dưới $1.2M AUD, đối soát ranh giới trường công lập danh tiếng và chỉ số an ninh cảnh sát SAPOL.</p>
    <div class="hero-buttons">
      <a href="#propertySection" class="hero-btn hero-btn-primary">
        🔍 Khảo Sát {total_listings} Nhà Đang Bán
      </a>
      <a href="javascript:void(0)" onclick="openMortgageModal('Mẫu Dự Toán Tài Chính Toàn Vùng', 1100000)" class="hero-btn" style="background:#7c3aed; color:white;">
        🧮 Bảng Tính Vay &amp; Chi Phí Mua Nhà MỚI
      </a>
      <a href="#soldSection" class="hero-btn" style="background:#10b981; color:white;">
        🤝 Xem {sold_total_30d} Nhà Vừa Bán (Private Treaty + Đấu Giá)
      </a>
      <a href="#fullReportSection" class="hero-btn hero-btn-secondary">
        📖 Đọc Toàn Văn Báo Cáo (10 Chương)
      </a>
    </div>
  </header>

  <!-- Stats -->
  <div class="stats-container">
    <div class="stat-card">
      <div class="stat-icon" style="background:#eff6ff; color:#2563eb;">🏡</div>
      <div>
        <div class="stat-val">{total_listings} Căn</div>
        <div class="stat-lbl">Nhà An Toàn Đang Chào Bán</div>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-icon" style="background:#ecfdf5; color:#059669;">🤝</div>
      <div>
        <div class="stat-val">{sold_total_7d} Căn (7 Ngày)</div>
        <div class="stat-lbl">Vừa Bán ({sold_total_30d} căn/30 ngày &bull; Median ${sold_median/1000:,.0f}k)</div>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-icon" style="background:#f0fdf4; color:#059669;">🛡️</div>
      <div>
        <div class="stat-val">100% Lọc SAPOL</div>
        <div class="stat-lbl">Loại Trừ Elizabeth, Salisbury, Morphett Vale</div>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-icon" style="background:#fef3c7; color:#d97706;">💰</div>
      <div>
        <div class="stat-val">${median_price/1000:,.0f}k AUD</div>
        <div class="stat-lbl">Giá Đang Rao Bán Trung Vị</div>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-icon" style="background:#fdf2f8; color:#db2777;">🏫</div>
      <div>
        <div class="stat-val">5 Trường Top</div>
        <div class="stat-lbl">GIHS, Norwood Int, Henley, Brighton, Unley</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <main class="main-wrapper">

    <!-- Property Section -->
    <section id="propertySection">
      <!-- Filters -->
      <div class="filter-card">
        <div class="filter-row">
          <span style="font-size:12px; font-weight:700; color:var(--slate-900);">Hành Lang Đô Thị:</span>
          <div class="region-pills" id="regionPills">
            <button class="pill-btn active" onclick="setRegion('all', this)">Tất cả ({total_listings})</button>
            <button class="pill-btn" onclick="setRegion('City of Burnside & Core East', this)">Burnside & Toorak Gdns</button>
            <button class="pill-btn" onclick="setRegion('City of Unley & Prestige South', this)">Unley & Unley Park</button>
            <button class="pill-btn" onclick="setRegion('City of Mitcham & Foothills', this)">Mitcham & Foothills</button>
            <button class="pill-btn" onclick="setRegion('Norwood, Campbelltown & North-East Core', this)">Norwood & Campbelltown</button>
            <button class="pill-btn" onclick="setRegion('Western Coastal & Beachside', this)">Ven Biển Henley/Brighton</button>
            <button class="pill-btn" onclick="setRegion('Adelaide Hills & North-East Enclaves', this)">Adelaide Hills & Golden Grove</button>
          </div>
        </div>
        <div class="filter-inputs">
          <input type="text" id="searchInput" class="search-input" placeholder="🔍 Tìm kiếm địa chỉ, vùng ngoại ô (suburb), trường học..." oninput="renderProperties()">
          <select id="typeFilter" class="select-input" onchange="renderProperties()">
            <option value="all">Mọi loại hình</option>
            <option value="House">Freestanding House</option>
            <option value="Townhouse">Townhouse</option>
            <option value="Unit">Unit / Villa Trệt</option>
          </select>
          <select id="sortFilter" class="select-input" onchange="renderProperties()">
            <option value="dist">Gần 1B Wilgena Ave nhất</option>
            <option value="price_asc">Giá: Thấp đến Cao</option>
            <option value="price_desc">Giá: Cao đến Thấp</option>
          </select>
        </div>
      </div>

      <!-- Properties Grid -->
      <div class="grid-header">
        <div class="grid-title">Danh Sách Bất Động Sản An Toàn (<span id="matchCount">{total_listings}</span> căn phù hợp)</div>
        <div style="font-size:12px; color:var(--slate-600);">Tâm điểm: 1B Wilgena Ave, Myrtle Bank SA 5064</div>
      </div>
      <div class="property-grid" id="propertyGrid"></div>
    <!-- Recently Sold Properties Section (Private Treaty + Auction) -->
    <section id="soldSection" class="section-box" style="border: 2px solid #059669; background: #ffffff;">
      <div class="section-head" style="border-bottom: 2px solid #d1fae5; padding-bottom: 14px; margin-bottom: 18px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
          <div>
            <div style="display:inline-block; background:#059669; color:white; font-size:11px; font-weight:800; padding:4px 10px; border-radius:6px; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.5px;">
              Giao Dịch Thực Tế Toàn Vùng An Toàn &bull; Bán Thỏa Thuận (Private Treaty) &amp; Đấu Giá
            </div>
            <h2 style="color:#0f172a; font-size:22px; margin-top:2px;">🤝 Báo Cáo Nhà Vừa Bán &amp; Giá Bán Chốt Thực Tế</h2>
            <p style="font-size:13px; color:#475569;">
              Theo dõi sát sao các bất động sản vừa giao dịch thành công trên 137 vùng an toàn tại Adelaide. Đầy đủ cả hình thức đàm phán thông thường và đấu giá.
            </p>
          </div>
          <div>
            <span style="background:#ecfdf5; border:1px solid #a7f3d0; color:#047857; font-size:12px; font-weight:700; padding:8px 16px; border-radius:6px; display:inline-flex; align-items:center; gap:6px;">
              🛡️ Đã Quét 137 Suburb An Toàn
            </span>
          </div>
        </div>
      </div>

      <!-- Sold KPI Grid -->
      <div class="auction-kpi-grid">
        <div class="auction-kpi-card" style="border-left:4px solid #059669;">
          <div class="auction-kpi-val" style="color:#059669;">{sold_total_7d} Căn (7 Ngày)</div>
          <div class="auction-kpi-lbl">Nhà Vừa Bán Tuần Qua</div>
          <div class="auction-kpi-sub">14 ngày: {sold_total_14d} căn &bull; 30 ngày: {sold_total_30d} căn</div>
        </div>
        <div class="auction-kpi-card" style="border-left:4px solid #0284c7;">
          <div class="auction-kpi-val" style="color:#0284c7;">${sold_median/1000:,.0f}k AUD</div>
          <div class="auction-kpi-lbl">Giá Bán Trung Vị (Công Khai)</div>
          <div class="auction-kpi-sub">Đã công bố giá: {sold_disclosed_count:,} căn ({sold_disclosed_count/max(sold_total_all,1)*100:.1f}%)</div>
        </div>
        <div class="auction-kpi-card" style="border-left:4px solid #10b981;">
          <div class="auction-kpi-val" style="color:#10b981;">{sold_pt_count/max(sold_total_all,1)*100:.1f}%</div>
          <div class="auction-kpi-lbl">Bán Thỏa Thuận (Private Treaty)</div>
          <div class="auction-kpi-sub">{sold_pt_count:,} căn bán đàm phán trực tiếp</div>
        </div>
        <div class="auction-kpi-card" style="border-left:4px solid #8b5cf6;">
          <div class="auction-kpi-val" style="color:#8b5cf6;">{sold_auc_count} Căn Đấu Giá</div>
          <div class="auction-kpi-lbl">Bán Qua Sàn Đấu Giá</div>
          <div class="auction-kpi-sub">Chiếm {sold_auc_count/max(sold_total_all,1)*100:.1f}% tổng giao dịch khu an toàn</div>
        </div>
      </div>

      <!-- Callout to Charts 9, 10 & 11 (Sold Analytics) -->
      <div style="background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%); border: 1.5px solid #a7f3d0; border-radius: 8px; padding: 14px 18px; margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div style="display:flex; align-items:center; gap:12px;">
          <span style="font-size:28px;">📊</span>
          <div>
            <div style="font-weight:800; color:#065f46; font-size:14px;">Báo Cáo Chuyên Sâu Nhà Đã Bán &amp; Giá Bán Thực Tế (8,121 Giao Dịch Toàn Greater Adelaide)</div>
            <div style="font-size:12px; color:#047857; margin-top:2px;">Xem chi tiết theo: Chu kỳ 2 năm (BĐ 9), Phân loại nhà &amp; Số PN (BĐ 10), 6 Vùng an toàn (BĐ 11), và Chu kỳ tuần theo Loại nhà &amp; PN (BĐ 12).</div>
          </div>
        </div>
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
          <a href="#analyticsSection" onclick="switchChart(9, document.querySelectorAll('.chart-tab-btn')[8])" style="background:#059669; color:white; font-size:11.5px; font-weight:700; padding:6px 12px; border-radius:6px; text-decoration:none; display:inline-flex; align-items:center; gap:4px; box-shadow:0 2px 4px rgba(5,150,105,0.2);">
            📈 BĐ 9: Chu Kỳ 2 Năm &rarr;
          </a>
          <a href="#analyticsSection" onclick="switchChart(10, document.querySelectorAll('.chart-tab-btn')[9])" style="background:#0284c7; color:white; font-size:11.5px; font-weight:700; padding:6px 12px; border-radius:6px; text-decoration:none; display:inline-flex; align-items:center; gap:4px; box-shadow:0 2px 4px rgba(2,132,199,0.2);">
            🏡 BĐ 10: Loại Nhà &amp; PN &rarr;
          </a>
          <a href="#analyticsSection" onclick="switchChart(11, document.querySelectorAll('.chart-tab-btn')[10])" style="background:#0d9488; color:white; font-size:11.5px; font-weight:700; padding:6px 12px; border-radius:6px; text-decoration:none; display:inline-flex; align-items:center; gap:4px; box-shadow:0 2px 4px rgba(13,148,136,0.2);">
            🛡️ BĐ 11: 6 Vùng An Toàn &rarr;
          </a>
          <a href="#analyticsSection" onclick="switchChart(12, document.querySelectorAll('.chart-tab-btn')[11])" style="background:#7c3aed; color:white; font-size:11.5px; font-weight:700; padding:6px 12px; border-radius:6px; text-decoration:none; display:inline-flex; align-items:center; gap:4px; box-shadow:0 2px 4px rgba(124,58,237,0.2);">
            📆 BĐ 12: Tuần Loại Nhà &amp; PN &rarr;
          </a>
        </div>
      </div>

      <!-- Sold Filters & Search -->
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:12px;">
        <div style="font-size:13.5px; font-weight:800; color:#0f172a;">
          Danh Sách Bất Động Sản Vừa Bán (<span id="soldMatchCount" style="color:#059669;">{len(sold_listings)}</span> căn):
        </div>
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
          <input type="text" id="soldSearch" class="search-input" style="padding:6px 12px; font-size:12px; width:180px;" placeholder="Tìm suburb, đường..." oninput="filterSoldTable()">
          <select id="soldFilterPropType" class="select-input" style="padding:6px 10px; font-size:12px;" onchange="filterSoldTable()">
            <option value="all">Mọi loại nhà (All Types)</option>
            <option value="House">🏡 House (Nhà riêng)</option>
            <option value="Townhouse">🏘️ Townhouse (Nhà liên kế)</option>
            <option value="Unit">🏢 Unit / Villa (Căn hộ thấp tầng)</option>
            <option value="Apartment">🏙️ Apartment (Chung cư)</option>
          </select>
          <select id="soldFilterBedrooms" class="select-input" style="padding:6px 10px; font-size:12px;" onchange="filterSoldTable()">
            <option value="all">Mọi phòng ngủ</option>
            <option value="1">1 Phòng ngủ</option>
            <option value="2">2 Phòng ngủ</option>
            <option value="3">3 Phòng ngủ</option>
            <option value="4">4 Phòng ngủ</option>
            <option value="5+">5+ Phòng ngủ</option>
          </select>
          <select id="soldFilterRegion" class="select-input" style="padding:6px 10px; font-size:12px; max-width:180px;" onchange="filterSoldTable()">
            <option value="all">Mọi khu vực (All Regions)</option>
            <option value="Western Coastal Corridors">Western Coastal</option>
            <option value="Norwood, Campbelltown & North-East Core">Norwood &amp; Campbelltown</option>
            <option value="City of Mitcham & Foothills">Mitcham &amp; Foothills</option>
            <option value="Adelaide Hills & Tea Tree Gully Safe Enclaves">Hills &amp; Tea Tree Gully</option>
            <option value="City of Burnside & Core East">Burnside &amp; Core East</option>
            <option value="City of Unley & Prestige South">Unley &amp; Prestige South</option>
          </select>
          <select id="soldFilterTime" class="select-input" style="padding:6px 10px; font-size:12px;" onchange="filterSoldTable()">
            <option value="30d">Trong 30 ngày qua ({sold_total_30d} căn)</option>
            <option value="14d">Trong 14 ngày qua ({sold_total_14d} căn)</option>
            <option value="7d">Trong 7 ngày qua ({sold_total_7d} căn)</option>
            <option value="all">Tất cả ({sold_total_all} căn)</option>
          </select>
          <select id="soldFilterType" class="select-input" style="padding:6px 10px; font-size:12px;" onchange="filterSoldTable()">
            <option value="all">Mọi hình thức</option>
            <option value="Private Treaty">Bán thỏa thuận (Private Treaty)</option>
            <option value="Auction">Bán đấu giá (Auction)</option>
          </select>
          <select id="soldFilterPrice" class="select-input" style="padding:6px 10px; font-size:12px;" onchange="filterSoldTable()">
            <option value="all">Mọi trạng thái giá</option>
            <option value="Disclosed">Đã công bố giá</option>
            <option value="Undisclosed">Chờ công bố (Bảo mật)</option>
          </select>
          <select id="soldSort" class="select-input" style="padding:6px 10px; font-size:12px;" onchange="filterSoldTable()">
            <option value="date_desc">Ngày bán mới nhất</option>
            <option value="price_asc">Giá: Thấp &rarr; Cao</option>
            <option value="price_desc">Giá: Cao &rarr; Thấp</option>
            <option value="dist">Gần 1B Wilgena Ave nhất</option>
          </select>
        </div>
      </div>

      <!-- Scrollable Sold Table -->
      <div class="auction-table-scroll" style="max-height: 560px;">
        <table class="auction-table">
          <thead>
            <tr>
              <th>Ngày bán &amp; Địa chỉ / Suburb</th>
              <th>Loại hình / Phòng</th>
              <th>Hình thức bán</th>
              <th>Mức giá chốt</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody id="soldTableBody">
            <!-- Populated via JavaScript -->
          </tbody>
        </table>
      </div>
      <div style="font-size:11.5px; color:#64748b; margin-top:8px; text-align:right;">
        * Dữ liệu bán từ các đại lý BĐS Nam Úc &amp; Homely. Cập nhật ngày {now_str}.
      </div>
    </section>

    <!-- Domain Weekly Auction Intelligence Section -->
    <section id="auctionSection" class="section-box" style="border: 2px solid #0284c7; background: #ffffff;">
      <div class="section-head" style="border-bottom: 2px solid #e0f2fe; padding-bottom: 14px; margin-bottom: 18px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
          <div>
            <div style="display:inline-block; background:#0284c7; color:white; font-size:11px; font-weight:800; padding:4px 10px; border-radius:6px; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.5px;">
              Dữ Liệu Đấu Giá Chính Thức Từ Domain.com.au &bull; Adelaide
            </div>
            <h2 style="color:#0f172a; font-size:22px; margin-top:2px;">🔨 Báo Cáo Tình Hình Đấu Giá Tuần Này ({auc_date_str})</h2>
            <p style="font-size:13px; color:#475569;">
              Theo dõi sát sao áp lực thị trường qua tỷ lệ chốt thành công (Clearance Rate) và danh sách chi tiết các căn nhà bán tại sàn đấu giá.
            </p>
          </div>
          <div>
            <a href="https://www.domain.com.au/auction-results/adelaide/" target="_blank" rel="noopener noreferrer" style="background:#0284c7; color:white; font-size:12px; font-weight:700; padding:8px 16px; border-radius:6px; display:inline-flex; align-items:center; gap:6px;">
              Xem trang gốc trên Domain.com.au &rarr;
            </a>
          </div>
        </div>
      </div>

      <!-- Auction KPI Grid -->
      <div class="auction-kpi-grid">
        <div class="auction-kpi-card" style="border-left:4px solid #0284c7;">
          <div class="auction-kpi-val" style="color:#0284c7;">{auc_clearance:.1f}%</div>
          <div class="auction-kpi-lbl">Tỷ Lệ Chốt Thành Công</div>
          <div class="auction-kpi-sub">Cùng kỳ năm trước: {auc_last_year:.1f}%</div>
        </div>
        <div class="auction-kpi-card" style="border-left:4px solid #059669;">
          <div class="auction-kpi-val" style="color:#059669;">${auc_median/1000:,.0f}k AUD</div>
          <div class="auction-kpi-lbl">Giá Trung Vị Đấu Giá</div>
          <div class="auction-kpi-sub">Tổng DS: ${auc_total_sales/1000000:,.1f}M AUD</div>
        </div>
        <div class="auction-kpi-card" style="border-left:4px solid #2563eb;">
          <div class="auction-kpi-val" style="color:#2563eb;">{auc_sold} / {auc_listed}</div>
          <div class="auction-kpi-lbl">Căn Đã Bán / Đưa Ra Đấu Giá</div>
          <div class="auction-kpi-sub">Bán trước + Bán tại sàn</div>
        </div>
        <div class="auction-kpi-card" style="border-left:4px solid #d97706;">
          <div class="auction-kpi-val" style="color:#d97706;">{auc_passed_in} Căn</div>
          <div class="auction-kpi-lbl">Không Đạt Giá Kỳ Vọng (Passed In)</div>
          <div class="auction-kpi-sub">Rút lui (Withdrawn): {auc_withdrawn} căn</div>
        </div>
      </div>

      <!-- Auction Table Search & Filters -->
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:12px;">
        <div style="font-size:13.5px; font-weight:800; color:#0f172a;">
          Danh Sách {len(auc_listings)} Bất Động Sản Trong Phiên Đấu Giá Vừa Qua:
        </div>
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
          <input type="text" id="auctionSearch" class="search-input" style="padding:6px 12px; font-size:12px; width:220px;" placeholder="Tìm theo suburb, đường..." oninput="filterAuctionTable()">
          <select id="auctionFilterResult" class="select-input" style="padding:6px 10px; font-size:12px;" onchange="filterAuctionTable()">
            <option value="all">Tất cả kết quả</option>
            <option value="sold">✅ Tất cả nhà ĐÃ BÁN (31 căn)</option>
            <option value="AUSD">Đã bán tại sàn (AUSD)</option>
            <option value="AUSP">Đã bán trước (AUSP)</option>
            <option value="AUPI">Không bán được (AUPI)</option>
            <option value="AUW">Rút khỏi đấu giá (AUW)</option>
          </select>
        </div>
      </div>

      <!-- Scrollable Auction Table -->
      <div class="auction-table-scroll">
        <table class="auction-table">
          <thead>
            <tr>
              <th>Địa chỉ &amp; Suburb</th>
              <th>Loại hình / Phòng</th>
              <th>Kết quả đấu giá</th>
              <th>Mức giá chốt</th>
              <th>Đại lý (Agency)</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody id="auctionTableBody">
            <!-- Populated via JavaScript -->
          </tbody>
        </table>
      </div>
      <div style="font-size:11.5px; color:#64748b; margin-top:8px; text-align:right;">
        * Dữ liệu sơ bộ được cung cấp bởi Domain Group. Cập nhật vào ngày {auc_date_str}.
      </div>
    </section>

    <!-- Analytics Section -->
    <section id="analyticsSection" class="section-box">
      <div class="section-head">
        <h2>📊 Hệ Thống 12 Biểu Đồ Thẩm Định Thị Trường Adelaide</h2>
        <p style="font-size:12.5px; color:var(--slate-600);">Dữ liệu độc quyền phân tích rủi ro, cung cầu, phân loại hình nhà, số phòng ngủ, xu hướng giá tuần và chu kỳ bán 2 năm bởi Toan Nguyen IT OZ.</p>
      </div>

      <div class="chart-tabs">
        <button class="chart-tab-btn active" onclick="switchChart(1, this)">1. Giá Trung Vị Theo Vùng</button>
        <button class="chart-tab-btn" onclick="switchChart(2, this)">2. Tương Quan Cự Ly &amp; Giá</button>
        <button class="chart-tab-btn" onclick="switchChart(3, this)">3. Bản Đồ Nguồn Cung Mới</button>
        <button class="chart-tab-btn" onclick="switchChart(4, this)">4. Phân Hóa Cắt Giảm Di Trú</button>
        <button class="chart-tab-btn" onclick="switchChart(5, this)">5. Thước Đo An Toàn SAPOL</button>
        <button class="chart-tab-btn" onclick="switchChart(6, this)">6. Ma Trận Giá vs Đất vs Lối Sống</button>
        <button class="chart-tab-btn" onclick="switchChart(7, this)">7. Chi Phí House vs Townhouse vs Unit</button>
        <button class="chart-tab-btn" onclick="switchChart(8, this)" style="border: 2px solid #0284c7; font-weight:800; color:#0284c7;">8. Xu Hướng Giá &amp; Đấu Giá Tuần MỚI</button>
        <button class="chart-tab-btn" onclick="switchChart(9, this)" style="border: 2px solid #059669; font-weight:800; color:#059669;">9. Chu Kỳ Nhà Bán &amp; Giá 2 Năm MỚI</button>
        <button class="chart-tab-btn" onclick="switchChart(10, this)" style="border: 2px solid #0284c7; font-weight:800; color:#0284c7;">10. Loại Nhà &amp; Số Phòng Ngủ MỚI</button>
        <button class="chart-tab-btn" onclick="switchChart(11, this)" style="border: 2px solid #0d9488; font-weight:800; color:#0d9488;">11. Nhà Bán Theo 6 Vùng An Toàn MỚI</button>
        <button class="chart-tab-btn" onclick="switchChart(12, this)" style="border: 2px solid #7c3aed; font-weight:800; color:#7c3aed;">12. Chu Kỳ Tuần: Loại Nhà &amp; Số PN MỚI</button>
      </div>

      <div class="chart-display">
        <img id="activeChartImg" src="reports/charts/chart1_median_prices.png" alt="Adelaide Real Estate Chart" class="chart-img">
      </div>
    </section>

    <!-- Academic Urban Economics Research Section -->
    <section id="economicsSection" class="section-box" style="border: 2px solid #3b82f6; background: linear-gradient(to bottom, #ffffff, #eff6ff);">
      <div class="section-head" style="border-bottom: 2px solid #bfdbfe; padding-bottom: 14px; margin-bottom: 18px;">
        <div style="display:inline-block; background:#2563eb; color:white; font-size:11px; font-weight:800; padding:4px 10px; border-radius:6px; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.5px;">
          Nghiên Cứu Học Thuật &amp; Bằng Chứng RBA
        </div>
        <h2 style="color:#1e3a8a; font-size:22px;">🏛️ Vì Sao Cung Nhà Ngoại Ô Tăng Thì Giá Đất Nội Đô Lại Tăng?</h2>
        <p style="font-size:13.5px; color:#334155; font-weight:500;">
          Giải mã nghịch lý kinh tế học đô thị qua <strong>Mô hình Alonso-Muth-Mills</strong>, nghiên cứu của <strong>Ngân hàng Trung ương Úc (RBA RDP 2018-03)</strong> và thực nghiệm thị trường Sydney/Melbourne.
        </p>
      </div>

      <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px;">
        <div style="background:white; padding:18px; border-radius:10px; border:1px solid #dbeafe; box-shadow:0 2px 6px rgba(37,99,235,0.05);">
          <h4 style="color:#1d4ed8; font-size:14.5px; margin-bottom:8px;">📐 1. Mô hình Alonso–Muth–Mills &amp; Độ Dốc Địa Tô (Bid-Rent)</h4>
          <p style="font-size:12.5px; color:#475569; line-height:1.6;">
            Khi mở rộng đô thị ra xa (Riverlea 35km, Concordia 45km), bán kính đô thị tăng gấp đôi, làm thời gian và chi phí đi lại của cư dân ngoại ô tăng vọt. Theo công thức <code>R(d) = R(b) + t × (b - d)</code>, <strong>giá trị tiết kiệm thời gian (Accessibility Premium)</strong> của đất nội đô (Myrtle Bank, Burnside cách trung tâm 3-5km) bắt buộc phải tăng vọt để cân bằng trạng thái hữu dụng.
          </p>
        </div>

        <div style="background:white; padding:18px; border-radius:10px; border:1px solid #dbeafe; box-shadow:0 2px 6px rgba(37,99,235,0.05);">
          <h4 style="color:#1d4ed8; font-size:14.5px; margin-bottom:8px;">🏦 2. Nghiên cứu RBA (Kendall &amp; Tulip, 2018)</h4>
          <p style="font-size:12.5px; color:#475569; line-height:1.6;">
            Ngân hàng Trung ương Úc chứng minh: Đất ở rìa xa có thặng dư khan hiếm gần như bằng 0, trong khi tại các quận nội đô &lt; 10km, <strong>thặng dư khan hiếm quy hoạch (Zoning Shadow Price) chiếm tới 42% - 73% giá trị nhà</strong>. Càng nhiều nhà giá rẻ ở ngoại ô, tầng lớp có tích lũy tài sản càng đổ xô về tranh mua quỹ đất hữu hạn tại các quận an toàn nội đô.
          </p>
        </div>

        <div style="background:white; padding:18px; border-radius:10px; border:1px solid #dbeafe; box-shadow:0 2px 6px rgba(37,99,235,0.05);">
          <h4 style="color:#1d4ed8; font-size:14.5px; margin-bottom:8px;">🏫 3. Hàng Hóa Thay Thế Kém (Imperfect Substitutes)</h4>
          <p style="font-size:12.5px; color:#475569; line-height:1.6;">
            Suất học trường công điểm Tier 1 (Glenunga International High, Unley High) có ranh giới địa lý cố định không thể nhân bản. Người mua $1.1M tại Myrtle Bank và người mua $600k ở vùng rìa 40km thuộc hai phân khúc khách hàng hoàn toàn độc lập, không làm triệt tiêu sức cầu của nhau.
          </p>
        </div>

        <div style="background:white; padding:18px; border-radius:10px; border:1px solid #dbeafe; box-shadow:0 2px 6px rgba(37,99,235,0.05);">
          <h4 style="color:#1d4ed8; font-size:14.5px; margin-bottom:8px;">🏙️ 4. Bằng Chứng Lịch Sử Sydney &amp; Melbourne (2014-2021)</h4>
          <p style="font-size:12.5px; color:#475569; line-height:1.6;">
            Khi Tây Sydney bung hàng trăm ngàn lô đất mới, giá nhà vùng ven chỉ tăng chậm (+15% đến +25%) do dư cung. Ngược lại, giá nhà đất tại các quận nội đô và ven biển Sydney tăng vọt <strong>+80% đến +110%</strong>, nới rộng biên độ chênh lệch giá trị lên mức kỷ lục.
          </p>
        </div>
      </div>
    </section>

    <!-- Articles & Guide Section -->
    <section class="section-box">
      <div class="section-head">
        <h2>💡 Cẩm Nang Thực Chiến: Pháp Lý, Phí Strata &amp; Điện Mặt Trời Solar</h2>
        <p style="font-size:12.5px; color:var(--slate-600);">Những kiến thức thực tế bắt buộc phải biết khi mua nhà tại Nam Úc.</p>
      </div>

      <div class="article-grid">
        <div class="article-card">
          <h3>📜 Thời Hạn Sở Hữu (Torrens vs Strata)</h3>
          <p><strong>Torrens Title:</strong> Sở hữu vĩnh viễn 100% đất và công trình trọn đời (không có thời hạn 50/70 năm). Chủ nhà có toàn quyền đập đi xây lại.</p>
          <p><strong>Strata/Community Title:</strong> Sở hữu vĩnh viễn không gian bên trong; tường ngoài và mái thuộc tập thể quản lý chung.</p>
        </div>

        <div class="article-card">
          <h3>💰 Các Loại Phí Bắt Buộc Hàng Năm</h3>
          <p><strong>Council Rates:</strong> $1,600 - $2,600/năm (Burnside, Unley, Mitcham).</p>
          <p><strong>SA Water:</strong> $1,000 - $1,600/năm (Cấp thoát nước + số nước dùng).</p>
          <p><strong>Land Tax:</strong> <strong>$0 MIỄN PHÍ 100%</strong> đối với nhà ở chính (PPOR).</p>
          <p><strong>ESL (Cứu nạn cứu hỏa):</strong> $180 - $300/năm.</p>
        </div>

        <div class="article-card">
          <h3>☀️ Lắp Đặt Điện Mặt Trời Solar Tại Adelaide</h3>
          <p>Nam Úc có giá điện lưới đắt bậc nhất nước Úc (~40c/kWh). Lắp hệ thống <strong>6.6kW Solar</strong> (~$4,500-$6,500) giúp tiết kiệm <strong>$1,500 - $2,200 tiền điện/năm</strong>.</p>
          <p><strong>Thời gian hoàn vốn:</strong> Chỉ từ 2.5 - 3.5 năm. Nhà riêng lắp tự do; nhà Strata cần xin phép ban quản trị (90% được duyệt).</p>
        </div>

        <div class="article-card">
          <h3>📈 Nghiên Cứu: Tại Sao Cung Ngoại Ô Tăng Thì Giá Nội Đô Lại Tăng?</h3>
          <p><strong>Mô hình Alonso-Muth-Mills & RBA Research (Kendall & Tulip):</strong> Cung nhà ở rìa xa (Riverlea 35km, Concordia 45km) làm dãn bán kính đô thị, khiến giá trị tiết kiệm thời gian di chuyển của đất nội đô (Myrtle Bank, Burnside 3-5km) tăng vọt theo <em>Đường dốc địa tô (Bid-Rent Gradient)</em>.</p>
          <p><strong>Hàng hóa thay thế kém:</strong> Suất học trường công lập danh tiếng (GIHS, Unley High) có ranh giới cố định, không thể nhân bản ra ngoại ô. Càng nhiều nhà ngoại ô mọc lên, thặng dư khan hiếm (Zoning Scarcity Premium) tại các quận nội đô an toàn càng bị đẩy lên cao.</p>
        </div>
      </div>
    </section>

    <!-- ========================================================
         DEDICATED FULL-TEXT MARKET REPORT SECTION (10 CHAPTERS)
         ======================================================== -->
    <section id="fullReportSection" class="full-report-container">
      <div class="report-hero-head">
        <div class="report-badge-top">📖 Báo Cáo Nghiên Cứu &amp; Thẩm Định Toàn Văn</div>
        <h2>BÁO CÁO PHÂN TÍCH THỊ TRƯỜNG BẤT ĐỘNG SẢN GREATER ADELAIDE 2026</h2>
        <p>
          Khảo sát toàn diện 140+ Suburb &bull; Bổ sung phân tích chuyên sâu Unley Park, Toorak Gardens, Malvern &bull; Lọc sạch 100% rủi ro tội phạm SAPOL &bull; Nghiên cứu kinh tế đô thị RBA.
        </p>
        <div class="report-meta-row">
          <div class="report-meta-item">
            <span>✍️ Tác giả:</span> <strong>TOAN NGUYEN IT OZ</strong>
          </div>
          <div class="report-meta-item">
            <span>📅 Cập nhật:</span> <strong>{now_str}</strong>
          </div>
          <div class="report-meta-item">
            <span>⏱️ Thời lượng đọc:</span> <strong>~18 phút (10 Chương)</strong>
          </div>
          <div class="report-meta-item">
            <span>🛡️ Độ tin cậy:</span> <strong>100% Thẩm định thực tế</strong>
          </div>
          <div class="report-head-btns">
            <a href="reports/Bao_Cao_Bat_Dong_San_Greater_Adelaide_Toan_Nguyen_IT_OZ_v2.pdf" download class="report-action-btn report-btn-pdf">
              📥 Tải File PDF (18 Trang)
            </a>
            <button onclick="window.print()" class="report-action-btn report-btn-print">
              🖨️ In Báo Cáo
            </button>
          </div>
        </div>
      </div>

      <!-- Chapter Navigation Pill Bar -->
      <div class="chapter-nav-bar">
        <a href="#chuong-1-tong-quan" class="chap-nav-pill">1. Tổng Quan 140+ Suburb</a>
        <a href="#chuong-2-suburb-thuong-luu" class="chap-nav-pill">2. Unley Park &amp; Toorak Gdns</a>
        <a href="#chuong-3-bo-loc-an-ninh-sapol" class="chap-nav-pill">3. Lọc An Ninh SAPOL</a>
        <a href="#chuong-4-he-thong-7-bieu-do" class="chap-nav-pill">4. Bộ 11 Biểu Đồ</a>
        <a href="#chuong-5-phan-bien-kinh-te-do-thi" class="chap-nav-pill">5. Kinh Tế Đô Thị (RBA)</a>
        <a href="#chuong-6-phan-tich-6-hanh-lang" class="chap-nav-pill">6. 6 Hành Lang An Toàn</a>
        <a href="#chuong-7-so-sanh-chi-phi-house-townhouse-unit" class="chap-nav-pill">7. House vs Unit vs Townhouse</a>
        <a href="#chuong-8-huong-dan-thuc-chien-phap-ly-solar" class="chap-nav-pill">8. Pháp Lý &amp; Solar</a>
        <a href="#chuong-9-danh-gia-chien-luoc-mua-hay-doi" class="chap-nav-pill">9. Mua Ngay Hay Đợi?</a>
        <a href="#chuong-10-top-bat-dong-san-form-1" class="chap-nav-pill">10. Top BĐS &amp; Form 1</a>
      </div>

      <!-- Rendered Article Body -->
      <div class="report-article-body">
        {report_html}
      </div>
    </section>

  </main>

  <!-- Footer -->
  <footer>
    <p>Bản quyền báo cáo & hệ thống tự động hóa &copy; 2026 <strong>Toan Nguyen IT OZ</strong> (toannguyenitoz@gmail.com).</p>
    <p style="margin-top:6px; opacity:0.75;">Hệ thống chạy tự động mỗi ngày vào lúc 06:00 AM giờ Adelaide qua GitHub Actions.</p>
  </footer>

  <!-- Floating Action Button for Mortgage Calculator -->
  <button type="button" onclick="openMortgageModal('Mẫu Dự Toán Toàn Vùng', 1100000)" class="floating-calc-btn" title="Mở Bảng Tính Vay Mua Nhà &amp; Chi Phí Ban Đầu">
    <span>🧮</span>
    <span>Bảng Tính Vay Mua Nhà</span>
  </button>

  <!-- Mortgage & Financing Calculator Modal -->
  <div id="mortgageModal" class="modal-overlay" onclick="closeMortgageModalOnBackdrop(event)">
    <div class="modal-card" onclick="event.stopPropagation()">
      <div class="modal-header">
        <div>
          <h3>🧮 Công Cụ Dự Toán Tài Chính &amp; Dòng Tiền Vay Mua Nhà</h3>
          <div id="modalPropertyContext" style="font-size:12.5px; color:#cbd5e1; margin-top:4px;">
            Đang tính cho căn nhà: <strong id="modalPropAddress" style="color:white;">Mẫu Dự Toán</strong> | Giá tham chiếu: <strong id="modalPropPrice" style="color:#38bdf8;">$1,100,000 AUD</strong>
          </div>
        </div>
        <button type="button" class="modal-close-btn" onclick="closeMortgageModal()" title="Đóng">&times;</button>
      </div>

      <div class="modal-body">
        <!-- LEFT COLUMN: INPUTS -->
        <div class="calc-panel">
          <h4 style="font-size:14px; font-weight:800; color:#0f172a; margin-bottom:14px; display:flex; align-items:center; gap:6px;">
            <span>⚙️</span> Thông Số Khoản Vay &amp; Vốn Tự Có
          </h4>

          <!-- Purchase Price -->
          <div class="calc-group">
            <label class="calc-label">
              <span>1. Giá mua nhà dự kiến (Purchase Price):</span>
              <span id="labelPriceFormatted" style="color:#0284c7; font-weight:800;">$1,100,000 AUD</span>
            </label>
            <div class="calc-input-wrapper">
              <span class="calc-input-prefix">$</span>
              <input type="number" id="calcPrice" class="calc-input" value="1100000" step="10000" min="100000" max="10000000" oninput="onPriceChange()">
              <span class="calc-input-suffix">AUD</span>
            </div>
            <div class="calc-quick-btns">
              <button type="button" class="calc-pill" onclick="adjustPrice(-50000)">-50k</button>
              <button type="button" class="calc-pill" onclick="adjustPrice(50000)">+50k</button>
              <button type="button" class="calc-pill" onclick="setPrice(850000)">$850k</button>
              <button type="button" class="calc-pill" onclick="setPrice(1000000)">$1.0M</button>
              <button type="button" class="calc-pill" onclick="setPrice(1100000)">$1.1M</button>
              <button type="button" class="calc-pill" onclick="setPrice(1200000)">$1.2M (Trần)</button>
              <button type="button" class="calc-pill" onclick="setPrice(1400000)">$1.4M</button>
            </div>
          </div>

          <!-- Cash / Available Deposit -->
          <div class="calc-group">
            <label class="calc-label">
              <span>2. Số tiền vốn tự có hiện có (Available Cash):</span>
              <span id="labelCashRatio" style="color:#059669; font-weight:800;">20% vốn</span>
            </label>
            <div class="calc-input-wrapper">
              <span class="calc-input-prefix">$</span>
              <input type="number" id="calcCash" class="calc-input" value="220000" step="5000" min="0" oninput="updateMortgageCalculation()">
              <span class="calc-input-suffix">AUD</span>
            </div>
            <div class="calc-quick-btns">
              <button type="button" class="calc-pill" onclick="setCashPercent(10)">10% Cọc</button>
              <button type="button" class="calc-pill" onclick="setCashPercent(15)">15% Cọc</button>
              <button type="button" class="calc-pill active" onclick="setCashPercent(20)">20% Chuẩn (Miễn LMI)</button>
              <button type="button" class="calc-pill" onclick="setCashPercent(25)">25% Cọc</button>
              <button type="button" class="calc-pill" onclick="setCashPercent(30)">30% Cọc</button>
            </div>
          </div>

          <!-- Interest Rate -->
          <div class="calc-group">
            <label class="calc-label">
              <span>3. Lãi suất vay ngân hàng (%/năm):</span>
              <span id="labelRateDisplay" style="color:#7c3aed; font-weight:800;">5.99%/năm</span>
            </label>
            <div class="calc-input-wrapper">
              <input type="number" id="calcRate" class="calc-input" value="5.99" step="0.05" min="1.0" max="15.0" style="padding-left:14px;" oninput="updateMortgageCalculation()">
              <span class="calc-input-suffix">% / năm</span>
            </div>
            <div class="calc-quick-btns">
              <button type="button" class="calc-pill" onclick="setRate(5.85)">5.85% (Ưu đãi Big 4)</button>
              <button type="button" class="calc-pill active" onclick="setRate(5.99)">5.99% (Thị trường)</button>
              <button type="button" class="calc-pill" onclick="setRate(6.25)">6.25% (Cố định)</button>
              <button type="button" class="calc-pill" onclick="setRate(6.50)">6.50% (Biến đổi)</button>
            </div>
          </div>

          <!-- Loan Term & Repayment Type -->
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;" class="calc-group">
            <div>
              <label class="calc-label">4. Thời hạn vay:</label>
              <select id="calcYears" class="calc-input" style="padding-left:12px; cursor:pointer;" onchange="updateMortgageCalculation()">
                <option value="30" selected>30 năm (Chuẩn)</option>
                <option value="25">25 năm</option>
                <option value="20">20 năm</option>
                <option value="15">15 năm</option>
              </select>
            </div>
            <div>
              <label class="calc-label">5. Hình thức trả:</label>
              <select id="calcRepayType" class="calc-input" style="padding-left:12px; cursor:pointer;" onchange="updateMortgageCalculation()">
                <option value="PI" selected>Gốc + Lãi (P&amp;I)</option>
                <option value="IO">Chỉ trả lãi (Interest Only)</option>
              </select>
            </div>
          </div>

          <!-- SA Government Upfront Costs Breakdown -->
          <div style="background:#f1f5f9; border-radius:10px; padding:14px; margin-top:14px; border:1px solid #cbd5e1;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span style="font-size:12.5px; font-weight:800; color:#1e293b;">📋 Chi Phí Dự Kiến Mua Nhà (Nam Úc):</span>
              <strong id="labelTotalUpfront" style="color:#dc2626; font-size:13px;">$57,485 AUD</strong>
            </div>
            
            <div style="display:flex; justify-content:space-between; font-size:11.5px; color:#475569; padding:3px 0;">
              <span>• Thuế trước bạ SA (RevenueSA Stamp Duty):</span>
              <strong id="costStampDuty" style="color:#0f172a;">$48,830</strong>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:11.5px; color:#475569; padding:3px 0;">
              <span>• Phí trước bạ quyền sử dụng đất SA LTO:</span>
              <strong id="costLTO" style="color:#0f172a;">$9,365</strong>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:11.5px; color:#475569; padding:3px 0;">
              <span>• Phí luật sư sang tên (Conveyancing):</span>
              <strong id="costLegal" style="color:#0f172a;">$1,600</strong>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:11.5px; color:#475569; padding:3px 0;">
              <span>• Thẩm định nhà &amp; mối mọt (Building &amp; Pest):</span>
              <strong id="costPest" style="color:#0f172a;">$650</strong>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:11.5px; color:#475569; padding:3px 0;">
              <span>• Phí hồ sơ &amp; đăng ký thế chấp ngân hàng:</span>
              <strong id="costMortgageReg" style="color:#0f172a;">$550</strong>
            </div>

            <label style="display:flex; align-items:center; gap:6px; font-size:11.5px; color:#0369a1; font-weight:600; margin-top:8px; cursor:pointer;">
              <input type="checkbox" id="calcFirstHome" onchange="updateMortgageCalculation()">
              <span>Thuộc diện Miễn Thuế Trước Bạ (First Home Buyer nhà mới &le; $650k)</span>
            </label>
          </div>
        </div>

        <!-- RIGHT COLUMN: RESULTS -->
        <div style="display:flex; flex-direction:column; gap:16px;">
          <!-- 1. Highlight: Repayment Schedules (Weekly, Monthly, Annual) -->
          <div style="background:linear-gradient(135deg, #065f46 0%, #047857 60%, #059669 100%); color:white; border-radius:12px; padding:20px; box-shadow:0 8px 20px rgba(5, 150, 105, 0.25);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; color:#a7f3d0;">
                💰 SỐ TIỀN PHẢI TRẢ HÀNG TUẦN (WEEKLY REPAYMENT)
              </span>
              <span id="badgeRepayType" style="background:rgba(255,255,255,0.2); padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">
                P&amp;I 30 năm
              </span>
            </div>

            <div style="margin: 12px 0 6px 0;">
              <span id="resWeekly" style="font-size:36px; font-weight:900; letter-spacing:-0.5px; color:#ffffff; text-shadow:0 2px 4px rgba(0,0,0,0.15);">
                $1,216 AUD
              </span>
              <span style="font-size:14px; opacity:0.9; font-weight:600;">/ tuần</span>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-top:14px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.2);">
              <div>
                <div style="font-size:11.5px; color:#a7f3d0;">📅 Trả Mỗi Tháng:</div>
                <strong id="resMonthly" style="font-size:17px; font-weight:800; color:white;">$5,270 AUD</strong>
              </div>
              <div>
                <div style="font-size:11.5px; color:#a7f3d0;">🗓️ Trả Mỗi Năm:</div>
                <strong id="resAnnual" style="font-size:17px; font-weight:800; color:white;">$63,245 AUD</strong>
              </div>
            </div>
          </div>

          <!-- 2. Loan Breakdown & Total Financing Card -->
          <div class="calc-panel">
            <h4 style="font-size:13.5px; font-weight:800; color:#0f172a; margin-bottom:12px; display:flex; align-items:center; justify-content:space-between;">
              <span>🏦 Cơ Cấu Vốn &amp; Khoản Vay Ngân Hàng</span>
              <span id="resLVRBadge" style="background:#e0f2fe; color:#0369a1; padding:3px 8px; border-radius:6px; font-size:11px; font-weight:700;">
                LVR: 80.0%
              </span>
            </h4>

            <div style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #f1f5f9; font-size:12.5px;">
              <span style="color:#64748b;">Tổng chi phí cần có (Giá nhà + Thuế phí):</span>
              <strong id="resTotalAcquisition" style="color:#0f172a;">$1,157,485 AUD</strong>
            </div>

            <div style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #f1f5f9; font-size:12.5px;">
              <span style="color:#64748b;">Vốn tự có (Tiền cọc + Thanh toán ban đầu):</span>
              <strong id="resCashUsed" style="color:#059669;">$220,000 AUD</strong>
            </div>

            <div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #f1f5f9; font-size:13px;">
              <span style="font-weight:700; color:#1e293b;">Số tiền cần vay ngân hàng (Loan Amount):</span>
              <strong id="resLoanAmount" style="color:#1d4ed8; font-size:15px; font-weight:900;">$937,485 AUD</strong>
            </div>

            <div style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #f1f5f9; font-size:12.5px;">
              <span style="color:#64748b;">Tổng tiền lãi phải trả cả kỳ (Total Interest):</span>
              <strong id="resTotalInterest" style="color:#d97706;">$1,083,720 AUD</strong>
            </div>

            <div style="display:flex; justify-content:space-between; padding:5px 0; font-size:12.5px;">
              <span style="color:#64748b;">Tổng cộng gốc &amp; lãi phải trả suốt 30 năm:</span>
              <strong id="resTotalRepaid" style="color:#0f172a;">$2,021,205 AUD</strong>
            </div>

            <!-- Visual Bar: Principal vs Interest -->
            <div style="margin-top:12px;">
              <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;">
                <span style="color:#1d4ed8; font-weight:700;">Tiền Gốc: <span id="barPrincipalPct">46%</span></span>
                <span style="color:#d97706; font-weight:700;">Tiền Lãi: <span id="barInterestPct">54%</span></span>
              </div>
              <div style="height:10px; border-radius:5px; background:#f1f5f9; overflow:hidden; display:flex;">
                <div id="barPrincipal" style="width:46%; background:#2563eb;"></div>
                <div id="barInterest" style="width:54%; background:#f59e0b;"></div>
              </div>
            </div>

            <!-- LMI Warning / Safe Note -->
            <div id="resLMINote" style="margin-top:10px; font-size:11.5px; border-radius:6px; padding:8px 10px; background:#ecfdf5; color:#065f46; border:1px solid #a7f3d0;">
              ✅ <strong>Vốn an toàn:</strong> Tiền cọc tương đương &ge; 20% giá trị căn nhà, giúp anh được miễn hoàn toàn bảo hiểm vay thế chấp (LMI - tiết kiệm $15k - $25k).
            </div>
          </div>

          <!-- 3. Affordability & Stress Test Card -->
          <div style="background:#fff; border-radius:12px; padding:16px; border:1px solid #e2e8f0;">
            <h4 style="font-size:13px; font-weight:800; color:#0f172a; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
              <span>🛡️</span> Thước Đo Khả Năng Chi Trả &amp; Quản Trị Rủi Ro
            </h4>

            <div style="font-size:12px; color:#475569; line-height:1.5;">
              • <strong>Thu nhập gia đình khuyến nghị:</strong> Khoảng <strong id="resRecIncomeYear" style="color:#059669;">$210,000 AUD/năm</strong> (trước thuế) để tiền trả góp chiếm dưới ngưỡng an toàn 30% thu nhập gia đình (tránh rủi ro Mortgage Stress theo tiêu chuẩn RBA).
            </div>

            <div style="font-size:12px; color:#475569; line-height:1.5; margin-top:6px;">
              • <strong>Kịch bản Lãi suất tăng +1.0% (Stress Test):</strong> Số tiền phải trả sẽ là <strong id="resStressWeekly" style="color:#dc2626;">$1,385 AUD/tuần</strong> (tăng thêm khoảng <span id="resStressDiff">$169/tuần</span>).
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer" style="padding:14px 24px; background:#f1f5f9; border-top:1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center; border-bottom-left-radius:16px; border-bottom-right-radius:16px;">
        <span style="font-size:11.5px; color:#64748b;">
          * Công cụ ước tính độc quyền bởi Toan Nguyen IT OZ. Áp dụng bảng biểu thuế RevenueSA 2024-2026.
        </span>
        <button type="button" onclick="closeMortgageModal()" style="background:#0f172a; color:white; border:none; padding:8px 18px; border-radius:8px; font-weight:700; font-size:12px; cursor:pointer;">
          Đóng Bảng Tính
        </button>
      </div>
    </div>
  </div>

  <!-- Client Script for Filtering & Rendering -->
  <script>
    const allProps = {properties_json_str};
    let currentRegion = 'all';

    const cacheBuster = Date.now();
    const chartMap = {{
      1: 'reports/charts/chart1_median_prices.png?v=' + cacheBuster,
      2: 'reports/charts/chart2_distance_vs_price.png?v=' + cacheBuster,
      3: 'reports/charts/chart3_housing_supply_distribution.png?v=' + cacheBuster,
      4: 'reports/charts/chart4_immigration_impact_analysis.png?v=' + cacheBuster,
      5: 'reports/charts/chart5_safety_index_comparison_v2.png?v=' + cacheBuster,
      6: 'reports/charts/chart6_regional_value_matrix.png?v=' + cacheBuster,
      7: 'reports/charts/chart7_property_type_cost_comparison.png?v=' + cacheBuster,
      8: 'reports/charts/chart8_weekly_price_trends.png?v=' + cacheBuster,
      9: 'reports/charts/chart9_2year_weekly_sales_volume_price.png?v=' + cacheBuster,
      10: 'reports/charts/chart10_sold_by_type_and_bedrooms.png?v=' + cacheBuster,
      11: 'reports/charts/chart11_sold_by_region.png?v=' + cacheBuster,
      12: 'reports/charts/chart12_weekly_sold_by_type_and_bedrooms.png?v=' + cacheBuster
    }};

    function switchChart(id, btn) {{
      document.getElementById('activeChartImg').src = chartMap[id];
      document.querySelectorAll('.chart-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    }}

    // Auction Listings Data & Render
    const auctionListings = {auction_listings_json_str};

    function filterAuctionTable() {{
      const q = (document.getElementById('auctionSearch').value || '').toLowerCase().trim();
      const codeFilter = document.getElementById('auctionFilterResult').value;
      const tbody = document.getElementById('auctionTableBody');

      const filtered = auctionListings.filter(item => {{
        if (codeFilter === 'sold' && !(item.result_code === 'AUSD' || item.result_code === 'AUSP')) return false;
        else if (codeFilter !== 'all' && codeFilter !== 'sold' && item.result_code !== codeFilter) return false;
        if (q) {{
          const str = (item.address + ' ' + item.suburb + ' ' + (item.agency || '')).toLowerCase();
          if (!str.includes(q)) return false;
        }}
        return true;
      }});

      if (filtered.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:24px; color:#64748b;">Không tìm thấy kết quả đấu giá nào phù hợp.</td></tr>';
        return;
      }}

      tbody.innerHTML = filtered.map(item => {{
        let badgeClass = 'badge-aupi';
        if (item.result_code === 'AUSD') badgeClass = 'badge-ausd';
        else if (item.result_code === 'AUSP') badgeClass = 'badge-ausp';
        else if (item.result_code === 'AUW') badgeClass = 'badge-auw';

        const priceStr = item.price ? ('$' + Number(item.price).toLocaleString('en-US')) : '<span style="color:#94a3b8; font-style:italic;">Không tiết lộ</span>';
        const specStr = `${{item.property_type || 'House'}} • ${{item.bedrooms || '-'}}PN ${{item.bathrooms || '-'}}WC ${{item.carspaces || '-'}}Xe`;

        return `
          <tr>
            <td>
              <strong style="color:#0f172a;">${{item.address}}</strong>
            </td>
            <td style="color:#475569; font-weight:600;">${{specStr}}</td>
            <td><span class="${{badgeClass}}">${{item.result_label}}</span></td>
            <td style="font-weight:800; color:#1e3a8a; font-size:13.5px;">${{priceStr}}</td>
            <td style="color:#64748b; font-size:12px;">${{item.agency || 'N/A'}}</td>
            <td style="white-space:nowrap;">
              <button type="button" onclick="openMortgageModal('${{encodeURIComponent(item.address)}}', ${{item.price || 950000}})" style="background:#7c3aed; color:white; border:none; padding:4px 8px; border-radius:4px; font-weight:700; font-size:11px; cursor:pointer; margin-right:4px;" title="Tính toán chi phí & dòng tiền vay mua">
                🧮 Vay
              </button>
              ${{item.domain_url ? `
                <a href="${{item.domain_url}}" target="_blank" rel="noopener noreferrer" style="background:#f1f5f9; border:1px solid #cbd5e1; color:#0284c7; padding:4px 8px; border-radius:4px; font-weight:700; font-size:11px; white-space:nowrap; text-decoration:none;">
                  Domain &rarr;
                </a>
              ` : '-'}}
            </td>
          </tr>
        `;
      }}).join('');
    }}

    // Recently Sold Properties Data & Render
    const soldListings = {sold_listings_json_str};

    function filterSoldTable() {{
      const q = (document.getElementById('soldSearch').value || '').toLowerCase().trim();
      const timeFilter = document.getElementById('soldFilterTime').value;
      const typeFilter = document.getElementById('soldFilterType').value;
      const priceFilter = document.getElementById('soldFilterPrice').value;
      const propTypeFilter = document.getElementById('soldFilterPropType') ? document.getElementById('soldFilterPropType').value : 'all';
      const bedFilter = document.getElementById('soldFilterBedrooms') ? document.getElementById('soldFilterBedrooms').value : 'all';
      const regFilter = document.getElementById('soldFilterRegion') ? document.getElementById('soldFilterRegion').value : 'all';
      const sort = document.getElementById('soldSort').value;
      const tbody = document.getElementById('soldTableBody');
      const countEl = document.getElementById('soldMatchCount');

      const now = new Date();
      const d7 = new Date(now.getTime() - 7 * 24 * 3600 * 1000).toISOString().split('T')[0];
      const d14 = new Date(now.getTime() - 14 * 24 * 3600 * 1000).toISOString().split('T')[0];
      const d30 = new Date(now.getTime() - 30 * 24 * 3600 * 1000).toISOString().split('T')[0];

      let filtered = soldListings.filter(item => {{
        // Time filter
        if (timeFilter === '7d' && item.sold_date < d7) return false;
        if (timeFilter === '14d' && item.sold_date < d14) return false;
        if (timeFilter === '30d' && item.sold_date < d30) return false;

        // Sale Type filter (Private Treaty vs Auction)
        if (typeFilter !== 'all' && !item.sale_type.includes(typeFilter)) return false;

        // Price filter
        if (priceFilter === 'Disclosed' && !item.price_val) return false;
        if (priceFilter === 'Undisclosed' && item.price_val) return false;

        // Property Type filter
        if (propTypeFilter !== 'all' && (item.property_type || 'House') !== propTypeFilter) return false;

        // Bedrooms filter
        if (bedFilter !== 'all') {{
          const b = item.bedrooms || 3;
          if (bedFilter === '1' && b !== 1) return false;
          if (bedFilter === '2' && b !== 2) return false;
          if (bedFilter === '3' && b !== 3) return false;
          if (bedFilter === '4' && b !== 4) return false;
          if (bedFilter === '5+' && b < 5) return false;
        }}

        // Region filter
        if (regFilter !== 'all' && item.region !== regFilter) return false;

        // Search text
        if (q) {{
          const str = (item.address + ' ' + item.suburb + ' ' + item.region + ' ' + (item.property_type || '')).toLowerCase();
          if (!str.includes(q)) return false;
        }}
        return true;
      }});

      // Sort
      if (sort === 'date_desc') {{
        filtered.sort((a, b) => (b.sold_date || '').localeCompare(a.sold_date || ''));
      }} else if (sort === 'price_asc') {{
        filtered.sort((a, b) => (a.price_val || 999999999) - (b.price_val || 999999999));
      }} else if (sort === 'price_desc') {{
        filtered.sort((a, b) => (b.price_val || 0) - (a.price_val || 0));
      }} else if (sort === 'dist') {{
        filtered.sort((a, b) => (a.distance_km_from_wilgena || 99) - (b.distance_km_from_wilgena || 99));
      }}

      if (countEl) countEl.innerText = filtered.length;

      if (filtered.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:24px; color:#64748b;">Không tìm thấy bất động sản vừa bán nào phù hợp với bộ lọc này.</td></tr>';
        return;
      }}

      tbody.innerHTML = filtered.slice(0, 100).map(item => {{
        const isAuction = item.sale_type.includes('Auction') || item.sale_type.includes('Đấu giá');
        const badgeClass = isAuction ? 'badge-auction-type' : 'badge-private-type';
        const badgeText = isAuction ? '🔨 Bán Đấu Giá' : '🤝 Bán Thỏa Thuận';

        const pt = item.property_type || 'House';
        let ptBadge = '<span style="background:#e0e7ff; color:#3730a3; font-weight:700; font-size:10.5px; padding:2px 6px; border-radius:4px; margin-right:4px;">🏡 House</span>';
        if (pt === 'Townhouse') ptBadge = '<span style="background:#e0f2fe; color:#0369a1; font-weight:700; font-size:10.5px; padding:2px 6px; border-radius:4px; margin-right:4px;">🏘️ Townhouse</span>';
        else if (pt === 'Unit') ptBadge = '<span style="background:#ecfdf5; color:#047857; font-weight:700; font-size:10.5px; padding:2px 6px; border-radius:4px; margin-right:4px;">🏢 Unit</span>';
        else if (pt === 'Apartment') ptBadge = '<span style="background:#fef3c7; color:#92400e; font-weight:700; font-size:10.5px; padding:2px 6px; border-radius:4px; margin-right:4px;">🏙️ Apartment</span>';

        const priceHtml = item.price_val 
          ? `<strong style="color:#047857; font-size:13.5px;">$${{Number(item.price_val).toLocaleString('en-US')}} AUD</strong>`
          : `<span style="background:#f1f5f9; color:#64748b; font-size:11px; padding:3px 8px; border-radius:4px; font-weight:600;">Chờ công bố</span>`;

        const specStr = `${{ptBadge}} ${{item.bedrooms || '-'}} PN • ${{item.bathrooms || '-'}} WC • ${{item.carspaces || '-'}} Xe ${{item.land_size ? '• ' + item.land_size : ''}}`;

        return `
          <tr>
            <td>
              <span style="display:inline-block; background:#e0f2fe; color:#0369a1; font-weight:700; font-size:11px; padding:2px 7px; border-radius:4px; margin-bottom:3px;">
                📅 ${{item.sold_date_formatted || item.sold_date}}
              </span>
              <br>
              <strong style="color:#0f172a; font-size:13px;">${{item.address}}</strong>
              <div style="font-size:11px; color:#64748b; margin-top:2px;">${{item.region}} &bull; Cách bạn ${{item.distance_km_from_wilgena}} km</div>
            </td>
            <td style="color:#475569; font-weight:600; font-size:12px;">${{specStr}}</td>
            <td><span class="${{badgeClass}}">${{badgeText}}</span></td>
            <td>${{priceHtml}}</td>
            <td style="white-space:nowrap;">
              <button type="button" onclick="openMortgageModal('${{encodeURIComponent(item.address)}}', ${{item.price_val || 1000000}})" style="background:#7c3aed; color:white; border:none; padding:4px 8px; border-radius:4px; font-weight:700; font-size:11px; cursor:pointer; margin-right:4px;" title="Tính toán chi phí & dòng tiền vay mua căn nhà này">
                🧮 Vay
              </button>
              <a href="${{item.homely_url}}" target="_blank" rel="noopener noreferrer" style="background:#f1f5f9; border:1px solid #cbd5e1; color:#0284c7; padding:4px 8px; border-radius:4px; font-weight:700; font-size:11px; white-space:nowrap; text-decoration:none;">
                Hồ Sơ &rarr;
              </a>
            </td>
          </tr>
        `;
      }}).join('');
    }}

    function setRegion(reg, btn) {{
      currentRegion = reg;
      document.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderProperties();
    }}

    function renderProperties() {{
      const search = document.getElementById('searchInput').value.toLowerCase().trim();
      const type = document.getElementById('typeFilter').value;
      const sort = document.getElementById('sortFilter').value;

      let filtered = allProps.filter(p => {{
        // Region filter
        if (currentRegion !== 'all' && p.region !== currentRegion) return false;
        // Type filter
        if (type !== 'all' && !p.property_type.toLowerCase().includes(type.toLowerCase())) return false;
        // Search text
        if (search) {{
          const str = (p.address + ' ' + p.suburb + ' ' + p.school_zone + ' ' + p.region).toLowerCase();
          if (!str.includes(search)) return false;
        }}
        return true;
      }});

      // Sort
      if (sort === 'dist') {{
        filtered.sort((a, b) => a.distance_km_from_wilgena - b.distance_km_from_wilgena);
      }} else if (sort === 'price_asc') {{
        filtered.sort((a, b) => (a.price_min || 9999999) - (b.price_min || 9999999));
      }} else if (sort === 'price_desc') {{
        filtered.sort((a, b) => (b.price_min || 0) - (a.price_min || 0));
      }}

      document.getElementById('matchCount').innerText = filtered.length;
      const grid = document.getElementById('propertyGrid');

      if (filtered.length === 0) {{
        grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding: 40px; color:#64748b;">Không tìm thấy căn nhà nào phù hợp với bộ lọc này.</div>';
        return;
      }}

      grid.innerHTML = filtered.slice(0, 48).map(p => `
        <div class="property-card">
          <div class="card-head">
            <div>
              <div class="card-region">${{p.region || 'Greater Adelaide'}}</div>
              <div class="card-address">${{p.address}}</div>
            </div>
            <div class="card-badge-safe">🛡️ An Toàn SAPOL</div>
          </div>
          <div class="card-body">
            <div class="card-price">${{p.price_raw}}</div>
            <div class="card-features">
              <span class="feat-item">🛏️ ${{p.bedrooms}} PN</span>
              <span class="feat-item">🚿 ${{p.bathrooms}} WC</span>
              <span class="feat-item">🚗 ${{p.car_spaces}} Xe</span>
              <span class="feat-item">📐 ${{p.land_size}}</span>
            </div>
            <div class="card-tags">
              <div class="tag-row">
                <span class="tag-label">Trường học:</span>
                <span style="color:var(--primary); font-weight:700;">${{p.school_zone}}</span>
              </div>
              <div class="tag-row">
                <span class="tag-label">Loại hình:</span>
                <span>${{p.property_type}}</span>
              </div>
              <div class="tag-row">
                <span class="tag-label">Năm xây dựng:</span>
                <span style="color:var(--emerald); font-weight:700;">🔨 ${{p.year_built || 'Chưa rõ'}}</span>
              </div>
              <div class="tag-row">
                <span class="tag-label">Ngày lên web:</span>
                <span style="color:#0284c7; font-weight:700;">📅 ${{p.listed_date || '14/09/2026'}}</span>
              </div>
            </div>
          </div>
          <div class="card-foot">
            <span class="card-dist">📍 Cách bạn: ${{p.distance_km_from_wilgena}} km</span>
            <div class="btn-group-foot">
              <button type="button" onclick="openMortgageModal('${{encodeURIComponent(p.address)}}', ${{p.price_min || 1000000}})" class="btn-calc" title="Tính toán chi phí &amp; số tiền trả mỗi tuần/năm cho căn nhà này">
                🧮 Tính Vay
              </button>
              ${{p.homely_url ? `
                <a href="${{p.homely_url}}" target="_blank" rel="noopener noreferrer" class="btn-homely" title="Xem ảnh & chi tiết bài đăng gốc 100% chính xác">
                  Chi Tiết &rarr;
                </a>
              ` : ''}}
              <a href="${{p.google_domain_url || ('https://www.google.com/search?q=' + encodeURIComponent(p.address + ' domain.com.au'))}}" target="_blank" rel="noopener noreferrer" class="btn-domain" title="Tìm bài đăng căn nhà này trên sàn Domain.com.au qua Google">
                Domain
              </a>
            </div>
          </div>
        </div>
      `).join('');
    }}

    // ==========================================
    // MORTGAGE & FINANCING CALCULATOR ENGINE
    // ==========================================
    function calculateSAStampDuty(val, isFirstHome) {{
      if (isFirstHome && val <= 650000) return 0;
      if (val <= 10000) return val * 0.01;
      if (val <= 20000) return 100 + (val - 10000) * 0.02;
      if (val <= 30000) return 300 + (val - 20000) * 0.03;
      if (val <= 50000) return 600 + (val - 30000) * 0.04;
      if (val <= 100000) return 1400 + (val - 50000) * 0.045;
      if (val <= 200000) return 3650 + (val - 100000) * 0.05;
      if (val <= 250000) return 8650 + (val - 200000) * 0.05;
      if (val <= 300000) return 11150 + (val - 250000) * 0.055;
      if (val <= 500000) return 13900 + (val - 300000) * 0.055;
      return 24900 + (val - 500000) * 0.055;
    }}

    function calculateLTOTransferFee(val) {{
      if (val <= 50000) return 198;
      const units = Math.ceil((val - 50000) / 10000);
      return 198 + units * 96.50;
    }}

    function openMortgageModal(addressEncoded, price) {{
      const addr = decodeURIComponent(addressEncoded || 'Căn nhà mẫu');
      const p = Number(price) > 0 ? Number(price) : 1100000;

      document.getElementById('modalPropAddress').innerText = addr;
      document.getElementById('modalPropPrice').innerText = '$' + p.toLocaleString('en-US') + ' AUD';
      document.getElementById('calcPrice').value = p;

      // Default deposit: 20%
      document.getElementById('calcCash').value = Math.round(p * 0.20);

      updateMortgageCalculation();

      const modal = document.getElementById('mortgageModal');
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    }}

    function closeMortgageModal() {{
      const modal = document.getElementById('mortgageModal');
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }}

    function closeMortgageModalOnBackdrop(e) {{
      if (e.target.id === 'mortgageModal') {{
        closeMortgageModal();
      }}
    }}

    document.addEventListener('keydown', function(e) {{
      if (e.key === 'Escape') {{
        closeMortgageModal();
      }}
    }});

    function onPriceChange() {{
      const p = Math.max(10000, Number(document.getElementById('calcPrice').value) || 0);
      document.getElementById('calcCash').value = Math.round(p * 0.20);
      updateMortgageCalculation();
    }}

    function adjustPrice(delta) {{
      const el = document.getElementById('calcPrice');
      let val = (Number(el.value) || 1000000) + delta;
      if (val < 100000) val = 100000;
      el.value = val;
      onPriceChange();
    }}

    function setPrice(val) {{
      document.getElementById('calcPrice').value = val;
      onPriceChange();
    }}

    function setCashPercent(pct) {{
      const p = Math.max(10000, Number(document.getElementById('calcPrice').value) || 0);
      document.getElementById('calcCash').value = Math.round(p * (pct / 100.0));
      updateMortgageCalculation();
    }}

    function setRate(val) {{
      document.getElementById('calcRate').value = val;
      updateMortgageCalculation();
    }}

    function updateMortgageCalculation() {{
      const price = Math.max(10000, Number(document.getElementById('calcPrice').value) || 0);
      const cash = Math.max(0, Number(document.getElementById('calcCash').value) || 0);
      const rate = Math.max(0.01, Number(document.getElementById('calcRate').value) || 5.99);
      const years = Number(document.getElementById('calcYears').value) || 30;
      const repayType = document.getElementById('calcRepayType').value;
      const isFirstHome = document.getElementById('calcFirstHome').checked;

      // Update price display labels
      document.getElementById('labelPriceFormatted').innerText = '$' + price.toLocaleString('en-US') + ' AUD';
      const cashPct = price > 0 ? ((cash / price) * 100).toFixed(1) : 0;
      document.getElementById('labelCashRatio').innerText = cashPct + '% giá nhà';
      document.getElementById('labelRateDisplay').innerText = rate.toFixed(2) + '%/năm';

      // 1. Upfront SA purchase costs
      const stampDuty = calculateSAStampDuty(price, isFirstHome);
      const ltoFee = calculateLTOTransferFee(price);
      const legalFee = 1600;
      const pestFee = 650;
      const bankFee = 550;
      const totalUpfrontFees = stampDuty + ltoFee + legalFee + pestFee + bankFee;
      const totalAcquisition = price + totalUpfrontFees;

      document.getElementById('costStampDuty').innerText = '$' + Math.round(stampDuty).toLocaleString('en-US');
      document.getElementById('costLTO').innerText = '$' + Math.round(ltoFee).toLocaleString('en-US');
      document.getElementById('costLegal').innerText = '$' + legalFee.toLocaleString('en-US');
      document.getElementById('costPest').innerText = '$' + pestFee.toLocaleString('en-US');
      document.getElementById('costMortgageReg').innerText = '$' + bankFee.toLocaleString('en-US');
      document.getElementById('labelTotalUpfront').innerText = '$' + Math.round(totalUpfrontFees).toLocaleString('en-US') + ' AUD';

      // 2. Financing & Loan Amount Required
      const loanAmount = Math.max(0, totalAcquisition - cash);
      const lvr = price > 0 ? (loanAmount / price) * 100 : 0;

      document.getElementById('resTotalAcquisition').innerText = '$' + Math.round(totalAcquisition).toLocaleString('en-US') + ' AUD';
      document.getElementById('resCashUsed').innerText = '$' + Math.round(cash).toLocaleString('en-US') + ' AUD';
      document.getElementById('resLoanAmount').innerText = '$' + Math.round(loanAmount).toLocaleString('en-US') + ' AUD';

      const lvrBadge = document.getElementById('resLVRBadge');
      const lmiNote = document.getElementById('resLMINote');
      lvrBadge.innerText = 'LVR: ' + lvr.toFixed(1) + '%';

      if (lvr <= 80.0) {{
        lvrBadge.style.background = '#ecfdf5';
        lvrBadge.style.color = '#047857';
        lmiNote.style.background = '#ecfdf5';
        lmiNote.style.color = '#065f46';
        lmiNote.style.borderColor = '#a7f3d0';
        lmiNote.innerHTML = '✅ <strong>Vốn an toàn (LVR &le; 80%):</strong> Được miễn phí bảo hiểm rủi ro thế chấp Lenders Mortgage Insurance (LMI), tiết kiệm từ $15,000 – $25,000 AUD.';
      }} else {{
        lvrBadge.style.background = '#fef3c7';
        lvrBadge.style.color = '#b45309';
        lmiNote.style.background = '#fffbeb';
        lmiNote.style.color = '#92400e';
        lmiNote.style.borderColor = '#fcd34d';
        const estLMI = Math.round(loanAmount * 0.02);
        lmiNote.innerHTML = '⚠️ <strong>Lưu ý LVR > 80%:</strong> Khoản vay vượt 80% giá trị định giá. Ngân hàng sẽ yêu cầu mua bảo hiểm thế chấp LMI (ước tính ~$' + estLMI.toLocaleString('en-US') + ' AUD) hoặc cần người thân bảo lãnh (Guarantor).';
      }}

      // 3. Repayment calculations
      const r = (rate / 100.0) / 12.0;
      const n = years * 12;
      let monthly = 0;
      let annual = 0;
      let weekly = 0;
      let totalRepaid = 0;
      let totalInterest = 0;

      if (loanAmount > 0) {{
        if (repayType === 'PI') {{
          monthly = loanAmount * (r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
          totalRepaid = monthly * n;
          totalInterest = totalRepaid - loanAmount;
          document.getElementById('badgeRepayType').innerText = 'P&I ' + years + ' năm';
        }} else {{
          monthly = loanAmount * r;
          totalInterest = monthly * n;
          totalRepaid = loanAmount + totalInterest;
          document.getElementById('badgeRepayType').innerText = 'Interest Only ' + years + ' năm';
        }}
        annual = monthly * 12;
        weekly = annual / 52;
      }}

      document.getElementById('resWeekly').innerText = '$' + Math.round(weekly).toLocaleString('en-US') + ' AUD';
      document.getElementById('resMonthly').innerText = '$' + Math.round(monthly).toLocaleString('en-US') + ' AUD';
      document.getElementById('resAnnual').innerText = '$' + Math.round(annual).toLocaleString('en-US') + ' AUD';
      document.getElementById('resTotalInterest').innerText = '$' + Math.round(totalInterest).toLocaleString('en-US') + ' AUD';
      document.getElementById('resTotalRepaid').innerText = '$' + Math.round(totalRepaid).toLocaleString('en-US') + ' AUD';

      // Visual Breakdown
      const principalPct = totalRepaid > 0 ? Math.round((loanAmount / totalRepaid) * 100) : 50;
      const interestPct = totalRepaid > 0 ? (100 - principalPct) : 50;
      document.getElementById('barPrincipalPct').innerText = principalPct + '%';
      document.getElementById('barInterestPct').innerText = interestPct + '%';
      document.getElementById('barPrincipal').style.width = principalPct + '%';
      document.getElementById('barInterest').style.width = interestPct + '%';

      // Affordability & Stress Test
      const recIncome = annual > 0 ? Math.round(annual / 0.30) : 0;
      document.getElementById('resRecIncomeYear').innerText = '$' + recIncome.toLocaleString('en-US') + ' AUD/năm';

      const rateStress = rate + 1.0;
      const rStress = (rateStress / 100.0) / 12.0;
      let monthlyStress = 0;
      if (loanAmount > 0) {{
        if (repayType === 'PI') {{
          monthlyStress = loanAmount * (rStress * Math.pow(1 + rStress, n)) / (Math.pow(1 + rStress, n) - 1);
        }} else {{
          monthlyStress = loanAmount * rStress;
        }}
      }}
      const weeklyStress = (monthlyStress * 12) / 52;
      const diffWeekly = weeklyStress - weekly;
      document.getElementById('resStressWeekly').innerText = '$' + Math.round(weeklyStress).toLocaleString('en-US') + ' AUD/tuần';
      document.getElementById('resStressDiff').innerText = '+$' + Math.round(diffWeekly).toLocaleString('en-US') + '/tuần';
    }}

    // Initial render
    renderProperties();
    filterSoldTable();
    filterAuctionTable();
    updateMortgageCalculation();
  </script>
</body>
</html>
"""
    with open(OUTPUT_INDEX, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Interactive website successfully built at: {OUTPUT_INDEX}")

if __name__ == '__main__':
    build()
