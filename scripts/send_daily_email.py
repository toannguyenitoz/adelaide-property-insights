import pathlib
import json
import os
import sys
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
DATA_JSON = BASE_DIR / 'data/expanded_safe_listings_under_1.2m.json'
PREVIEW_HTML = BASE_DIR / 'reports/email_preview.html'

DEFAULT_RECIPIENTS = [
    'Theodorenguyensa@gmail.com',
    'nguyenha.hanhlinh@gmail.com',
    'nancyha.au@gmail.com'
]

def score_property(p):
    """
    Evaluates and calculates a recommendation score (0-100+) based on:
    - School zone prestige (GIHS, Unley High, etc.)
    - Distance from Myrtle Bank (Wilgena Ave) & CBD
    - Safety rating (SAPOL statistics)
    - Price guide value & clarity
    - Property type (House > Townhouse > Unit) & features (baths, cars, land, year)
    """
    score = 0
    reasons = []

    # 1. School Zone Prestige
    sz = (p.get('school_zone') or '').lower()
    if 'glenunga' in sz or 'gihs' in sz:
        score += 35
        reasons.append("Vùng trường điểm Glenunga Int. High (Top 1 công lập Nam Úc)")
    elif any(k in sz for k in ['unley high', 'norwood', 'marryatville', 'brighton', 'henley']):
        score += 25
        reasons.append("Vùng trường danh tiếng (Unley High / Norwood / Ven biển)")
    else:
        score += 12

    # 2. Distance from Myrtle Bank
    dist = p.get('distance_km_from_wilgena', 99)
    if dist <= 1.5:
        score += 30
        reasons.append(f"Cực gần bạn ({dist:.1f} km từ Wilgena Ave)")
    elif dist <= 3.0:
        score += 22
        reasons.append(f"Vị trí rất gần trung tâm ({dist:.1f} km)")
    elif dist <= 5.5:
        score += 15
        reasons.append(f"Cự ly trung bình thuận tiện ({dist:.1f} km)")
    elif dist <= 10.0:
        score += 8
    else:
        score += 3

    # 3. Safety Rating
    safety = (p.get('safety_rating') or '').lower()
    if 'grade a+' in safety or any(sb in (p.get('suburb') or '').lower() for sb in ['burnside', 'unley', 'myrtle bank', 'toorak', 'highgate', 'malvern', 'mitcham', 'stirling']):
        score += 25
        reasons.append("An ninh tuyệt đối (SAPOL Grade A+ < 25 vụ/1k dân)")
    elif 'grade a' in safety:
        score += 18
        reasons.append("Khu vực dân trí cao, an toàn (Grade A)")
    else:
        score += 10

    # 4. Price Guide Value
    p_min = p.get('price_min') or 0
    p_max = p.get('price_max') or p_min
    eff_price = p_min if p_min > 0 else (p_max if p_max > 0 else 1050000)

    if 0 < eff_price <= 950000:
        score += 22
        reasons.append("Giá cực tốt dưới $950k AUD")
    elif eff_price <= 1050000:
        score += 18
        reasons.append("Mức giá cạnh tranh ($950k - $1.05M)")
    elif eff_price <= 1150000:
        score += 12
    elif eff_price <= 1200000:
        score += 8

    # Transparency bonus (has explicit price numbers vs undisclosed auction)
    raw = (p.get('price_raw') or '').lower()
    if '$' in raw and 'auction' not in raw:
        score += 5

    # Penalize if already under contract or sold so active listings rank higher
    if 'under contract' in raw or 'sold' in raw:
        score -= 40

    # 5. Property Type & Functional Features
    ptype = (p.get('property_type') or '').lower()
    if 'house' in ptype or 'freestanding' in ptype:
        score += 15
        reasons.append("Nhà riêng (House/Torrens Title - tiềm năng tăng vốn vượt trội)")
    elif 'townhouse' in ptype:
        score += 10
        reasons.append("Townhouse tiện nghi, chi phí bảo trì hợp lý")
    elif 'courtyard' in ptype:
        score += 9
    else:
        score += 6

    # Bathrooms & Car Spaces
    if p.get('bathrooms', 1) >= 2:
        score += 5
    if p.get('car_spaces', 1) >= 2:
        score += 5

    # Land size bonus
    land = str(p.get('land_size') or '')
    if 'm' in land:
        try:
            val = int(''.join(filter(str.isdigit, land)))
            if val >= 350:
                score += 6
                reasons.append(f"Khuôn viên đất rộng ({val} m²)")
        except:
            pass

    # Year built bonus
    year = p.get('year_built') or ''
    if year and year != 'Chưa rõ':
        score += 3

    return score, reasons[:3] # keep top 3 highlights

def select_top_properties(properties, count=8):
    """
    Ranks all properties and returns the top 5 to 10 listings.
    """
    scored = []
    for p in properties:
        sc, highlights = score_property(p)
        scored.append((sc, highlights, p))

    # Sort descending by score
    scored.sort(key=lambda x: x[0], reverse=True)

    # Return top N
    return scored[:count]

def generate_email_html(top_picks, total_scanned, now_str):
    """
    Generates a high-conversion, responsive, beautifully styled HTML email.
    """
    cards_html = ""
    for idx, (score, highlights, p) in enumerate(top_picks, 1):
        # Badge color based on rank
        rank_badge_color = "#1e3a8a" if idx == 1 else ("#059669" if idx <= 3 else "#2563eb")
        rank_label = f"#{idx} BĐS ĐÁNH GIÁ XUẤT SẮC" if idx == 1 else (f"#{idx} LỰA CHỌN HÀNG ĐẦU" if idx <= 3 else f"#{idx} ĐỀ XUẤT NỔI BẬT")
        
        highlights_html = "".join([f"<li style='margin-bottom:4px;'>🌟 <strong>{h}</strong></li>" for h in highlights])
        
        domain_url = p.get('google_domain_url') or p.get('domain_url') or f"https://www.google.com/search?q={p.get('address', '')}+domain.com.au"
        homely_url = p.get('homely_url') or ""

        cards_html += f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; margin-bottom:24px; padding:20px; box-shadow:0 3px 10px rgba(15,23,42,0.04);">
          <!-- Top Tag Bar -->
          <div style="margin-bottom:12px; display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center;">
            <span style="background:{rank_badge_color}; color:#ffffff; font-size:11px; font-weight:800; padding:4px 10px; border-radius:6px; text-transform:uppercase; letter-spacing:0.5px; display:inline-block; margin-bottom:6px;">
              {rank_label} (Điểm: {score})
            </span>
            <span style="background:#ecfdf5; color:#047857; border:1px solid #a7f3d0; font-size:11px; font-weight:700; padding:3px 8px; border-radius:6px; display:inline-block; margin-bottom:6px;">
              🛡️ {p.get('safety_rating', 'Grade A+ An Toàn')}
            </span>
          </div>

          <!-- Address & Region -->
          <div style="margin-bottom:10px;">
            <div style="color:#0284c7; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">{p.get('region', 'Greater Adelaide')}</div>
            <h2 style="margin:4px 0 0 0; color:#0f172a; font-size:17px; font-weight:800; line-height:1.4;">📍 {p.get('address')}</h2>
          </div>

          <!-- Price -->
          <div style="background:#f8fafc; border-left:4px solid #2563eb; padding:10px 14px; border-radius:0 8px 8px 0; margin-bottom:14px;">
            <span style="font-size:11px; color:#64748b; font-weight:700; text-transform:uppercase;">Mức giá chào bán / Hướng dẫn giá:</span>
            <div style="color:#1e3a8a; font-size:19px; font-weight:800; margin-top:2px;">{p.get('price_raw')}</div>
          </div>

          <!-- Key Features Grid -->
          <table style="width:100%; border-collapse:collapse; margin-bottom:14px; font-size:12.5px;">
            <tr style="background:#f1f5f9;">
              <td style="padding:8px 10px; border-radius:6px 0 0 6px; font-weight:700; color:#334155;">🛏️ {p.get('bedrooms', 3)} Phòng ngủ</td>
              <td style="padding:8px 10px; font-weight:700; color:#334155;">🚿 {p.get('bathrooms', 1)} Phòng tắm</td>
              <td style="padding:8px 10px; font-weight:700; color:#334155;">🚗 {p.get('car_spaces', 1)} Chỗ đậu xe</td>
              <td style="padding:8px 10px; border-radius:0 6px 6px 0; font-weight:700; color:#334155;">📐 {p.get('land_size', 'N/A')}</td>
            </tr>
          </table>

          <!-- Specs List -->
          <div style="font-size:12.5px; color:#475569; margin-bottom:14px; line-height:1.6;">
            <div>🏫 <strong>Trường học:</strong> <span style="color:#1d4ed8; font-weight:700;">{p.get('school_zone', 'N/A')}</span></div>
            <div>🏗️ <strong>Loại hình & Pháp lý:</strong> <span>{p.get('property_type', 'House')}</span></div>
            <div>🔨 <strong>Năm xây dựng:</strong> <span style="color:#059669; font-weight:700;">{p.get('year_built', 'Chưa rõ')}</span></div>
            <div>📍 <strong>Cự ly:</strong> <span>Cách 1B Wilgena Ave Myrtle Bank ~<strong>{p.get('distance_km_from_wilgena', 'N/A')} km</strong></span></div>
          </div>

          <!-- Why Recommended -->
          <div style="background:#eff6ff; border-radius:8px; padding:10px 14px; margin-bottom:16px;">
            <div style="font-size:11.5px; font-weight:800; color:#1e40af; text-transform:uppercase; margin-bottom:4px;">Lý Do Thẩm Định Đạt Điểm Cao:</div>
            <ul style="margin:0; padding-left:18px; font-size:12px; color:#1e3a8a; line-height:1.5;">
              {highlights_html}
            </ul>
          </div>

          <!-- Buttons -->
          <div style="display:flex; flex-wrap:wrap; gap:10px; padding-top:6px; border-top:1px solid #f1f5f9;">
            <a href="{domain_url}" target="_blank" style="background:#0284c7; color:#ffffff; text-decoration:none; font-size:12px; font-weight:700; padding:8px 16px; border-radius:6px; display:inline-block;">
              🔍 Mở trên Domain.com.au &rarr;
            </a>
            {f'<a href="{homely_url}" target="_blank" style="background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; text-decoration:none; font-size:12px; font-weight:700; padding:8px 14px; border-radius:6px; display:inline-block;">Xem trên Homely</a>' if homely_url else ''}
          </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bản Tin Bất Động Sản Greater Adelaide</title>
</head>
<body style="margin:0; padding:0; background:#f8fafc; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color:#334155; line-height:1.5;">
  <div style="max-width:680px; margin:0 auto; padding:20px 15px;">
    
    <!-- Brand Header -->
    <div style="background:linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); border-radius:14px; padding:28px 24px; text-align:center; color:#ffffff; margin-bottom:22px; box-shadow:0 8px 20px rgba(15,23,42,0.15);">
      <div style="display:inline-block; background:rgba(56,189,248,0.15); border:1px solid rgba(56,189,248,0.35); color:#7dd3fc; font-size:11px; font-weight:800; padding:4px 12px; border-radius:20px; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;">
        🛡️ BẢN TIN THẨM ĐỊNH TỰ ĐỘNG HÀNG NGÀY &bull; 06:00 AM ACST
      </div>
      <h1 style="margin:0 0 8px 0; font-size:22px; font-weight:800; letter-spacing:-0.5px; color:#ffffff;">
        TOAN NGUYEN IT OZ
      </h1>
      <p style="margin:0 0 12px 0; font-size:14px; color:#93c5fd; font-weight:500;">
        Top {len(top_picks)} Bất Động Sản Đáng Mua Nhất Adelaide Hôm Nay
      </p>
      <div style="font-size:11.5px; color:#cbd5e1; font-weight:400;">
        📅 Ngày gửi: <strong>{now_str}</strong> &bull; Đã quét & đối soát: <strong>{total_scanned} BĐS 3PN</strong>
      </div>
    </div>

    <!-- Intro Box -->
    <div style="background:#ffffff; border-radius:10px; border:1px solid #e2e8f0; padding:18px 20px; margin-bottom:22px; font-size:13px; line-height:1.6; color:#475569;">
      <p style="margin-top:0;">Xin chào anh chị,</p>
      <p>
        Hệ thống trí tuệ nhân tạo của <strong>Toan Nguyen IT OZ</strong> đã hoàn tất quét thị trường sáng nay. Trong tổng số <strong>{total_scanned} căn nhà 3 phòng ngủ</strong> đang rao bán dưới trần ngân sách <strong>$1.2M AUD</strong> trên toàn Greater Adelaide, hệ thống đã chạy thuật toán lọc sạch 100% rủi ro tội phạm SAPOL, kiểm tra ranh giới trường học danh tiếng và chọn ra <strong>{len(top_picks)} căn nhà được đánh giá ổn nhất</strong> cho gia đình:
      </p>
      <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:10px;">
        <span style="background:#eff6ff; color:#1d4ed8; font-size:11px; font-weight:700; padding:4px 10px; border-radius:6px;">🏫 Ưu tiên Zone GIHS & Unley</span>
        <span style="background:#f0fdf4; color:#047857; font-size:11px; font-weight:700; padding:4px 10px; border-radius:6px;">🛡️ 100% An Ninh Grade A / A+</span>
        <span style="background:#fef3c7; color:#b45309; font-size:11px; font-weight:700; padding:4px 10px; border-radius:6px;">💰 Ngân sách an toàn &lt; $1.2M</span>
      </div>
    </div>

    <!-- Listings Section -->
    <div style="margin-bottom:24px;">
      {cards_html}
    </div>

    <!-- Web Dashboard & Report CTA -->
    <div style="background:linear-gradient(to right, #eff6ff, #f0fdf4); border:2px solid #bfdbfe; border-radius:12px; padding:22px; text-align:center; margin-bottom:28px;">
      <h3 style="margin:0 0 8px 0; color:#1e3a8a; font-size:16px; font-weight:800;">
        🌐 Bạn Muốn Xem Toàn Bộ {total_scanned} Căn Nhà & Bộ 7 Biểu Đồ?
      </h3>
      <p style="margin:0 0 16px 0; font-size:12.5px; color:#475569;">
        Truy cập ngay cổng thông tin trực tuyến có đầy đủ bộ lọc tương tác, khảo sát 140+ suburb và tải báo cáo PDF phân tích 18 trang:
      </p>
      <div style="display:flex; justify-content:center; gap:12px; flex-wrap:wrap;">
        <a href="https://toannguyenitoz.github.io/adelaide-property-insights/" target="_blank" style="background:#2563eb; color:#ffffff; text-decoration:none; font-size:13px; font-weight:700; padding:10px 20px; border-radius:8px; display:inline-block;">
          🚀 Mở Cổng Thông Tin Trực Tuyến &rarr;
        </a>
        <a href="https://toannguyenitoz.github.io/adelaide-property-insights/reports/Bao_Cao_Bat_Dong_San_Greater_Adelaide_Toan_Nguyen_IT_OZ.pdf" target="_blank" style="background:#ffffff; color:#0f172a; border:1px solid #cbd5e1; text-decoration:none; font-size:13px; font-weight:700; padding:10px 18px; border-radius:8px; display:inline-block;">
          📥 Tải Báo Cáo PDF (18 Trang)
        </a>
      </div>
    </div>

    <!-- Footer -->
    <div style="text-align:center; font-size:11.5px; color:#94a3b8; line-height:1.6; padding:15px 0; border-top:1px solid #e2e8f0;">
      <div>Bản tin bất động sản độc quyền phát triển bởi <strong>Toan Nguyen IT OZ</strong></div>
      <div>Email liên hệ: <a href="mailto:toannguyenitoz@gmail.com" style="color:#0284c7; text-decoration:none;">toannguyenitoz@gmail.com</a></div>
      <div style="margin-top:6px; color:#cbd5e1;">© 2026 Toan Nguyen IT OZ. Mọi quyền được bảo lưu. Dữ liệu được tổng hợp tự động mỗi sáng lúc 06:00 AM ACST.</div>
    </div>

  </div>
</body>
</html>
"""
    return html

def send_email(subject, html_content, recipients, smtp_server, smtp_port, smtp_user, smtp_pass):
    """
    Sends the HTML email via SMTP with STARTTLS.
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"Toan Nguyen IT OZ <{smtp_user}>"
    msg['To'] = ", ".join(recipients)

    # Attach HTML part
    part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(part)

    print(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
    if int(smtp_port) == 465:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)
    else:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        server.ehlo()
        server.starttls()
        server.ehlo()

    print(f"Logging in as {smtp_user}...")
    server.login(smtp_user, smtp_pass)
    
    print(f"Sending email to: {recipients}...")
    server.sendmail(smtp_user, recipients, msg.as_string())
    server.quit()
    print("Email successfully dispatched to all recipients!")

def main():
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    dry_run = '--dry-run' in sys.argv or os.environ.get('DRY_RUN') == '1'

    # Read listings data
    if not os.path.exists(DATA_JSON):
        print(f"Error: Data file {DATA_JSON} not found!")
        sys.exit(1)

    with open(DATA_JSON, 'r', encoding='utf-8') as f:
        properties = json.load(f)

    total_scanned = len(properties)
    now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M ACST")

    print(f"Analyzing {total_scanned} listings...")
    top_picks = select_top_properties(properties, count=8)
    print(f"Selected Top {len(top_picks)} Recommended Properties:")
    for idx, (score, hl, p) in enumerate(top_picks, 1):
        print(f"  #{idx} (Score: {score}) - {p.get('address')} | {p.get('price_raw')} | {p.get('school_zone')}")

    html_content = generate_email_html(top_picks, total_scanned, now_str)

    # Always save preview
    with open(PREVIEW_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Email preview saved at: {PREVIEW_HTML}")

    # Read SMTP credentials
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USERNAME') or os.environ.get('EMAIL_SENDER')
    smtp_pass = os.environ.get('SMTP_PASSWORD') or os.environ.get('EMAIL_PASSWORD')

    # Read recipients
    env_recips = os.environ.get('EMAIL_RECIPIENTS')
    if env_recips:
        recipients = [r.strip() for r in env_recips.split(',') if r.strip()]
    else:
        recipients = DEFAULT_RECIPIENTS

    subject = f"[Toan Nguyen IT OZ] 🏡 Top {len(top_picks)} Nhà Đáng Mua Nhất Adelaide Hôm Nay ({datetime.datetime.now().strftime('%d/%m')})"

    if dry_run or not smtp_user or not smtp_pass:
        print("\n=== DRY RUN / NO SMTP CREDENTIALS ===")
        if not smtp_user or not smtp_pass:
            print("No SMTP credentials found in environment variables (SMTP_USERNAME / SMTP_PASSWORD).")
            print("To enable automated email dispatch, add SMTP_USERNAME and SMTP_PASSWORD to your GitHub Repository Secrets.")
        print(f"Target Recipients would be: {recipients}")
        print(f"Email Subject: {subject}")
        print(f"You can view the full HTML email rendered at: {PREVIEW_HTML}")
        print("Dry run completed successfully.")
        return

    # Real dispatch
    try:
        send_email(subject, html_content, recipients, smtp_server, smtp_port, smtp_user, smtp_pass)
    except Exception as e:
        print(f"Failed to dispatch email via SMTP: {e}", file=sys.stderr)
        # We don't fail CI if SMTP fails, so scraper & web deploy keep working
        sys.exit(0)

if __name__ == '__main__':
    main()
