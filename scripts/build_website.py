import pathlib
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
import json
import os
import datetime

DATA_JSON = str(BASE_DIR / 'data/expanded_safe_listings_under_1.2m.json')
OUTPUT_INDEX = str(BASE_DIR / 'index.html')

def build():
    with open(DATA_JSON, 'r', encoding='utf-8') as f:
        properties = json.load(f)

    # Sort by distance
    properties.sort(key=lambda x: (x.get('distance_km_from_wilgena', 99), x.get('price_min') or 9999999))

    total_listings = len(properties)
    prices = [p['price_min'] for p in properties if p.get('price_min')]
    median_price = int(sorted(prices)[len(prices)//2]) if prices else 890000

    now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    properties_json_str = json.dumps(properties, ensure_ascii=False)

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
  </style>
</head>
<body>

  <!-- Navbar -->
  <nav class="navbar">
    <div class="nav-brand">
      <div>
        <span class="brand-title">TOAN NGUYEN IT OZ</span>
        <span class="brand-sub">Adelaide Real Estate Intelligence &bull; Daily Automated Updates @ 6:00 AM ACST</span>
      </div>
    </div>
    <div class="nav-actions">
      <a href="reports/Bao_Cao_Bat_Dong_San_Greater_Adelaide_Toan_Nguyen_IT_OZ_v2.pdf" download class="btn-pdf">
        📥 Tải Báo Cáo PDF (17 Trang)
      </a>
    </div>
  </nav>

  <!-- Hero -->
  <header class="hero">
    <div class="hero-badge">
      🛡️ Dữ Liệu Thực Tế Tuyển Chọn &bull; Loại Trừ Vùng Tội Phạm &bull; Cập nhật lúc {now_str}
    </div>
    <h1>CỔNG PHÂN TÍCH BẤT ĐỘNG SẢN AN TOÀN GREATER ADELAIDE</h1>
    <p>Hệ thống tự động quét và thẩm định nhà 3 phòng ngủ có giá dưới $1.2M AUD, đối soát ranh giới trường công lập danh tiếng và chỉ số an ninh cảnh sát SAPOL.</p>
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
        <div class="stat-lbl">Giá Trung Vị Toàn Vùng</div>
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

    <!-- Analytics Section -->
    <section class="section-box">
      <div class="section-head">
        <h2>📊 Hệ Thống Biểu Đồ Thẩm Định Thị Trường Adelaide</h2>
        <p style="font-size:12.5px; color:var(--slate-600);">Dữ liệu độc quyền phân tích rủi ro, cung cầu và chi phí vận hành thực tế bởi Toan Nguyen IT OZ.</p>
      </div>

      <div class="chart-tabs">
        <button class="chart-tab-btn active" onclick="switchChart(1, this)">1. Giá Trung Vị Theo Vùng</button>
        <button class="chart-tab-btn" onclick="switchChart(2, this)">2. Tương Quan Cự Ly & Giá</button>
        <button class="chart-tab-btn" onclick="switchChart(3, this)">3. Bản Đồ Nguồn Cung Mới</button>
        <button class="chart-tab-btn" onclick="switchChart(4, this)">4. Phân Hóa Cắt Giảm Di Trú</button>
        <button class="chart-tab-btn" onclick="switchChart(5, this)">5. Thước Đo An Toàn SAPOL</button>
        <button class="chart-tab-btn" onclick="switchChart(6, this)">6. Ma Trận Giá vs Đất vs Lối Sống</button>
        <button class="chart-tab-btn" onclick="switchChart(7, this)">7. Chi Phí House vs Townhouse vs Unit</button>
      </div>

      <div class="chart-display">
        <img id="activeChartImg" src="reports/charts/chart1_median_prices.png" alt="Adelaide Real Estate Chart" class="chart-img">
      </div>
    </section>

    <!-- Academic Urban Economics Research Section -->
    <section class="section-box" style="border: 2px solid #3b82f6; background: linear-gradient(to bottom, #ffffff, #eff6ff);">
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

  </main>

  <!-- Footer -->
  <footer>
    <p>Bản quyền báo cáo & hệ thống tự động hóa &copy; 2026 <strong>Toan Nguyen IT OZ</strong> (toannguyenitoz@gmail.com).</p>
    <p style="margin-top:6px; opacity:0.75;">Hệ thống chạy tự động mỗi ngày vào lúc 06:00 AM giờ Adelaide qua GitHub Actions.</p>
  </footer>

  <!-- Client Script for Filtering & Rendering -->
  <script>
    const allProps = {properties_json_str};
    let currentRegion = 'all';

    const chartMap = {{
      1: 'reports/charts/chart1_median_prices.png',
      2: 'reports/charts/chart2_distance_vs_price.png',
      3: 'reports/charts/chart3_housing_supply_distribution.png',
      4: 'reports/charts/chart4_immigration_impact_analysis.png',
      5: 'reports/charts/chart5_safety_index_comparison.png',
      6: 'reports/charts/chart6_regional_value_matrix.png',
      7: 'reports/charts/chart7_property_type_cost_comparison.png'
    }};

    function switchChart(id, btn) {{
      document.getElementById('activeChartImg').src = chartMap[id];
      document.querySelectorAll('.chart-tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
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
            </div>
          </div>
          <div class="card-foot">
            <span class="card-dist">📍 Cách bạn: ${{p.distance_km_from_wilgena}} km</span>
            <div class="btn-group-foot">
              ${{p.homely_url ? `
                <a href="${{p.homely_url}}" target="_blank" rel="noopener noreferrer" class="btn-homely" title="Xem ảnh & chi tiết bài đăng gốc 100% chính xác">
                  Xem Chi Tiết &rarr;
                </a>
              ` : ''}}
              <a href="${{p.google_domain_url || ('https://www.google.com/search?q=' + encodeURIComponent(p.address + ' domain.com.au'))}}" target="_blank" rel="noopener noreferrer" class="btn-domain" title="Tìm bài đăng căn nhà này trên sàn Domain.com.au qua Google">
                Domain.com.au
              </a>
            </div>
          </div>
        </div>
      `).join('');
    }}

    // Initial render
    renderProperties();
  </script>
</body>
</html>
"""
    with open(OUTPUT_INDEX, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Interactive website successfully built at: {OUTPUT_INDEX}")

if __name__ == '__main__':
    build()
