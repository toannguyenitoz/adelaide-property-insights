import pathlib
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
import base64
import os
import re
import asyncio
import shutil
from markdown_it import MarkdownIt
from playwright.async_api import async_playwright

MASTER_MD_PATH = str(BASE_DIR / 'reports/real_estate_market_report.md')
SEP_MD_PATH = str(BASE_DIR / 'reports/proptrack_september_2026_home_price_report.md')
CHARTS_DIR = str(BASE_DIR / 'reports/charts')

# Master full report outputs
MASTER_HTML = str(BASE_DIR / 'reports/report_preview.html')
MASTER_PDF_PRIMARY = str(BASE_DIR / 'reports/Bao_Cao_Bat_Dong_San_Greater_Adelaide_Toan_Nguyen_IT_OZ.pdf')
MASTER_PDF_V2 = str(BASE_DIR / 'reports/Bao_Cao_Bat_Dong_San_Greater_Adelaide_Toan_Nguyen_IT_OZ_v2.pdf')

# September / October latest report outputs
SEP_HTML = str(BASE_DIR / 'reports/proptrack_report_preview.html')
SEP_PDF_PRIMARY = str(BASE_DIR / 'reports/Bao_Cao_Gia_Nha_Adelaide_Thang_10_2026_PropTrack.pdf')
SEP_PDF_SHORT = str(BASE_DIR / 'reports/Bao_Cao_Adelaide_Thang_10_2026.pdf')

def image_to_base64(img_path):
    if os.path.exists(img_path):
        with open(img_path, 'rb') as f:
            return 'data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8')
    return ''

def prepare_master_html():
    with open(MASTER_MD_PATH, 'r', encoding='utf-8') as f:
        md_text = f.read()

    md_text = re.sub(
        r'> \[!IMPORTANT\]\n((?:> .*\n?)+)',
        lambda m: '<div class="alert alert-important">' + m.group(1).replace('> ', '') + '</div>\n',
        md_text
    )
    md_text = re.sub(
        r'> \[!NOTE\]\n((?:> .*\n?)+)',
        lambda m: '<div class="alert alert-note">' + m.group(1).replace('> ', '') + '</div>\n',
        md_text
    )

    md = MarkdownIt('gfm-like', {'linkify': False, 'html': True})
    content_html = md.render(md_text)

    chart_files = [
        'chart1_median_prices.png',
        'chart2_distance_vs_price.png',
        'chart3_housing_supply_distribution.png',
        'chart4_immigration_impact_analysis.png',
        'chart5_safety_index_comparison.png',
        'chart5_safety_index_comparison_v2.png',
        'chart6_regional_value_matrix.png',
        'chart7_property_type_cost_comparison.png',
        'chart8_weekly_price_trends.png',
        'chart9_2year_weekly_sales_volume_price.png',
        'chart10_sold_by_type_and_bedrooms.png',
        'chart11_sold_by_region.png',
        'chart12_weekly_sold_by_type_and_bedrooms.png'
    ]

    for c_file in chart_files:
        rel_path = f'charts/{c_file}'
        abs_path = os.path.join(CHARTS_DIR, c_file)
        b64 = image_to_base64(abs_path)
        if b64:
            content_html = content_html.replace(f'src="{rel_path}"', f'src="{b64}"')

    # Page break markers
    content_html = content_html.replace('<h2>2. BỘ LỌC AN NINH', '<div style="page-break-before: always;"></div><h2>2. BỘ LỌC AN NINH')
    content_html = content_html.replace('<h2>3. HỆ THỐNG 7 BIỂU ĐỒ', '<div style="page-break-before: always;"></div><h2>3. HỆ THỐNG 7 BIỂU ĐỒ')
    content_html = content_html.replace('<h2>4. PHẢN BIỆN VĨ MÔ', '<div style="page-break-before: always;"></div><h2>4. PHẢN BIỆN VĨ MÔ')
    content_html = content_html.replace('<h2>5. PHÂN TÍCH 5 HÀNH LANG', '<div style="page-break-before: always;"></div><h2>5. PHÂN TÍCH 5 HÀNH LANG')
    content_html = content_html.replace('<h2>6. SO SÁNH TOÀN DIỆN CHI PHÍ', '<div style="page-break-before: always;"></div><h2>6. SO SÁNH TOÀN DIỆN CHI PHÍ')
    content_html = content_html.replace('<h2>7. HƯỚNG DẪN THỰC CHI', '<div style="page-break-before: always;"></div><h2>7. HƯỚNG DẪN THỰC CHI')
    content_html = content_html.replace('<h2>8. ĐÁNH GIÁ CHIẾN LƯỢC', '<div style="page-break-before: always;"></div><h2>8. ĐÁNH GIÁ CHIẾN LƯỢC')
    content_html = content_html.replace('<h2>9. TOP BẤT ĐỘNG SẢN', '<div style="page-break-before: always;"></div><h2>9. TOP BẤT ĐỘNG SẢN')

    full_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Báo Cáo Bất Động Sản Greater Adelaide - Toan Nguyen IT OZ</title>
<style>
  @page {{ size: A4; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.6;
    font-size: 11.5px;
    margin: 0;
    padding: 0;
  }}
  .brand-cover {{
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 60%, #2563eb 100%);
    color: white;
    padding: 24px 28px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  }}
  .brand-logo-text {{
    font-size: 22px;
    font-weight: 800;
    letter-spacing: 1px;
    color: #38bdf8;
    text-transform: uppercase;
  }}
  .brand-badge {{
    display: inline-block;
    background: rgba(255,255,255,0.18);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    margin-top: 8px;
  }}
  h1 {{
    font-size: 19px;
    color: #0f172a;
    border-bottom: 2px solid #2563eb;
    padding-bottom: 8px;
    margin-top: 16px;
    margin-bottom: 12px;
  }}
  h2 {{
    font-size: 14.5px;
    color: #1e3a8a;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 6px;
    margin-top: 20px;
    margin-bottom: 10px;
    page-break-after: avoid;
  }}
  h3 {{
    font-size: 13px;
    color: #0f172a;
    margin-top: 14px;
    margin-bottom: 8px;
    page-break-after: avoid;
  }}
  h4 {{
    font-size: 12px;
    color: #1e40af;
    margin-top: 12px;
    margin-bottom: 6px;
  }}
  p, li {{
    font-size: 11.5px;
    color: #334155;
  }}
  ul, ol {{
    padding-left: 20px;
    margin-top: 4px;
    margin-bottom: 8px;
  }}
  li {{ margin-bottom: 3px; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0 16px 0;
    font-size: 10.5px;
    page-break-inside: avoid;
  }}
  th, td {{
    padding: 6px 8px;
    text-align: left;
    border: 1px solid #e2e8f0;
  }}
  th {{
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
  }}
  tr:nth-child(even) {{ background-color: #f8fafc; }}
  img {{
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    margin: 10px 0 14px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    page-break-inside: avoid;
  }}
  .alert {{
    padding: 10px 14px;
    border-radius: 8px;
    margin: 12px 0;
    font-size: 11px;
    page-break-inside: avoid;
  }}
  .alert-important {{
    background-color: #eff6ff;
    border-left: 4px solid #2563eb;
    color: #1e3a8a;
  }}
  .alert-note {{
    background-color: #f8fafc;
    border-left: 4px solid #64748b;
    color: #334155;
  }}
  a {{
    color: #2563eb;
    text-decoration: none;
    font-weight: 600;
  }}
  hr {{
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 16px 0;
  }}
  code {{
    background-color: #f1f5f9;
    padding: 2px 5px;
    border-radius: 4px;
    font-family: Consolas, monospace;
    font-size: 10.5px;
    color: #0f172a;
  }}
</style>
</head>
<body>

<div class="brand-cover">
  <div class="brand-logo-text">TOAN NGUYEN IT OZ</div>
  <div style="font-size: 15.5px; font-weight: 700; margin-top: 6px;">BÁO CÁO PHÂN TÍCH BẤT ĐỘNG SẢN GREATER ADELAIDE (KHU VỰC AN TOÀN)</div>
  <div class="brand-badge">🛡️ Tuyển Chọn 5 Hành Lang An Toàn &bull; Loại Trừ Vùng Tội Phạm Cao &bull; Dưới $1.2M AUD</div>
  <div style="font-size: 10.5px; opacity: 0.85; margin-top: 8px;">
    Tiêu chí: 3 Phòng ngủ | An toàn chuẩn SAPOL | Pháp lý Vĩnh viễn | Phí Strata &amp; Chi phí Vận hành | Năng lượng Solar | Thẩm định: Toan Nguyen IT OZ
  </div>
</div>

{content_html}

</body>
</html>
"""
    with open(MASTER_HTML, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"HTML Preview saved: {MASTER_HTML}")
    return MASTER_HTML

def prepare_september_html():
    with open(SEP_MD_PATH, 'r', encoding='utf-8') as f:
        md_text = f.read()

    md_text = re.sub(
        r'> \[!IMPORTANT\]\n((?:> .*\n?)+)',
        lambda m: '<div class="alert alert-important">' + m.group(1).replace('> ', '') + '</div>\n',
        md_text
    )
    md_text = re.sub(
        r'> \[!NOTE\]\n((?:> .*\n?)+)',
        lambda m: '<div class="alert alert-note">' + m.group(1).replace('> ', '') + '</div>\n',
        md_text
    )

    md = MarkdownIt('gfm-like', {'linkify': False, 'html': True})
    content_html = md.render(md_text)

    # Insert page breaks before main chapters for elegant reading
    content_html = content_html.replace('<h2>3. HOUSE VÀ APARTMENT', '<div style="page-break-before: always;"></div><h2>3. HOUSE VÀ APARTMENT')
    content_html = content_html.replace('<h2>5. FIRST HOME BUYERS', '<div style="page-break-before: always;"></div><h2>5. FIRST HOME BUYERS')
    content_html = content_html.replace('<h2>7. NHÀ ĐẦU TƯ', '<div style="page-break-before: always;"></div><h2>7. NHÀ ĐẦU TƯ')

    full_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Báo Cáo Giá Nhà Adelaide Tháng 10/2026 - PropTrack & Toan Nguyen IT OZ</title>
<style>
  @page {{ size: A4; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.6;
    font-size: 11.5px;
    margin: 0;
    padding: 0;
  }}
  .brand-cover {{
    background: linear-gradient(135deg, #78350f 0%, #b45309 50%, #d97706 100%);
    color: white;
    padding: 24px 28px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(217,119,6,0.15);
  }}
  .brand-logo-text {{
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 1px;
    color: #fef3c7;
    text-transform: uppercase;
  }}
  .brand-badge {{
    display: inline-block;
    background: rgba(255,255,255,0.22);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    margin-top: 8px;
  }}
  h1 {{
    font-size: 18px;
    color: #78350f;
    border-bottom: 2px solid #d97706;
    padding-bottom: 8px;
    margin-top: 16px;
    margin-bottom: 12px;
  }}
  h2 {{
    font-size: 14px;
    color: #92400e;
    border-bottom: 1px solid #fde68a;
    padding-bottom: 6px;
    margin-top: 20px;
    margin-bottom: 10px;
    page-break-after: avoid;
  }}
  h3 {{
    font-size: 12.5px;
    color: #0f172a;
    margin-top: 14px;
    margin-bottom: 8px;
    page-break-after: avoid;
  }}
  p, li {{
    font-size: 11.5px;
    color: #334155;
  }}
  ul, ol {{
    padding-left: 20px;
    margin-top: 4px;
    margin-bottom: 8px;
  }}
  li {{ margin-bottom: 3px; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0 16px 0;
    font-size: 10.5px;
    page-break-inside: avoid;
  }}
  th, td {{
    padding: 6px 8px;
    text-align: left;
    border: 1px solid #fed7aa;
  }}
  th {{
    background-color: #ffedd5;
    color: #7c2d12;
    font-weight: 700;
  }}
  tr:nth-child(even) {{ background-color: #fff7ed; }}
  .alert {{
    padding: 10px 14px;
    border-radius: 8px;
    margin: 12px 0;
    font-size: 11px;
    page-break-inside: avoid;
  }}
  .alert-important {{
    background-color: #fffbeb;
    border-left: 4px solid #d97706;
    color: #92400e;
  }}
  .alert-note {{
    background-color: #f8fafc;
    border-left: 4px solid #64748b;
    color: #334155;
  }}
  a {{
    color: #b45309;
    text-decoration: none;
    font-weight: 600;
  }}
  hr {{
    border: none;
    border-top: 1px solid #fed7aa;
    margin: 16px 0;
  }}
  code {{
    background-color: #fef3c7;
    padding: 2px 5px;
    border-radius: 4px;
    font-family: Consolas, monospace;
    font-size: 10.5px;
    color: #92400e;
  }}
</style>
</head>
<body>

<div class="brand-cover">
  <div class="brand-logo-text">PROPTRACK &bull; REALESTATE.COM.AU &bull; TOAN NGUYEN IT OZ</div>
  <div style="font-size: 15.5px; font-weight: 700; margin-top: 6px;">BÁO CÁO GIÁ NHÀ ADELAIDE THÁNG 10/2026 (SỐ LIỆU THÁNG 9)</div>
  <div class="brand-badge">📉 Giá Nhà Adelaide Giảm -0.6% &bull; Lớn Nhất Toàn Úc &bull; Tăng Trưởng YoY +5.6%</div>
  <div style="font-size: 10.5px; opacity: 0.9; margin-top: 8px;">
    Tác giả: Eleanor Creagh (Senior Economist, REA Group) &bull; Đối soát &amp; Bản quyền phân tích: Toan Nguyen IT OZ (Adelaide Property Insights)
  </div>
</div>

{content_html}

</body>
</html>
"""
    with open(SEP_HTML, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"HTML Preview saved: {SEP_HTML}")
    return SEP_HTML

async def generate_single_pdf(html_path, target_pdf, doc_title):
    print(f"Generating PDF: {os.path.basename(target_pdf)}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f'file:///{html_path.replace(os.sep, "/")}', wait_until='load')

        header_template = f'''
        <div style="font-family: -apple-system, sans-serif; font-size: 7.5px; color: #64748b; width: 100%; display: flex; justify-content: space-between; align-items: center; padding: 0 14mm; border-bottom: 1px solid #e2e8f0; padding-bottom: 3px;">
          <style>div, span {{ font-size: 7.5px; font-family: -apple-system, sans-serif; }}</style>
          <span style="font-weight: 700; color: #1e3a8a; letter-spacing: 0.5px;">TOAN NGUYEN IT OZ</span>
          <span>{doc_title}</span>
        </div>
        '''

        footer_template = '''
        <div style="font-family: -apple-system, sans-serif; font-size: 7.5px; color: #94a3b8; width: 100%; display: flex; justify-content: space-between; align-items: center; padding: 0 14mm; border-top: 1px solid #e2e8f0; padding-top: 3px;">
          <style>div, span { font-size: 7.5px; font-family: -apple-system, sans-serif; }</style>
          <span>Thẩm định độc lập bởi <strong>Toan Nguyen IT OZ</strong> &bull; Confidential &amp; Proprietary</span>
          <span>Trang <span class="pageNumber"></span> / <span class="totalPages"></span></span>
        </div>
        '''

        await page.pdf(
            path=target_pdf,
            format='A4',
            print_background=True,
            display_header_footer=True,
            header_template=header_template,
            footer_template=footer_template,
            margin={
                'top': '22mm',
                'bottom': '22mm',
                'left': '14mm',
                'right': '14mm'
            }
        )
        await browser.close()
    print(f"PDF Successfully generated at: {target_pdf}")

async def run_all():
    # 1. Master Report PDF
    master_html = prepare_master_html()
    await generate_single_pdf(
        master_html, 
        MASTER_PDF_PRIMARY, 
        "BÁO CÁO BẤT ĐỘNG SẢN GREATER ADELAIDE &bull; VÙNG AN TOÀN"
    )
    shutil.copyfile(MASTER_PDF_PRIMARY, MASTER_PDF_V2)
    print(f"Copied Master PDF to: {MASTER_PDF_V2}")

    # 2. September/October Latest PropTrack Report PDF
    sep_html = prepare_september_html()
    await generate_single_pdf(
        sep_html,
        SEP_PDF_PRIMARY,
        "BÁO CÁO GIÁ NHÀ ADELAIDE THÁNG 10/2026 (PROPTRACK)"
    )
    shutil.copyfile(SEP_PDF_PRIMARY, SEP_PDF_SHORT)
    print(f"Copied October PDF to: {SEP_PDF_SHORT}")

def main():
    asyncio.run(run_all())

if __name__ == '__main__':
    main()
