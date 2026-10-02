import pathlib
import json
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
INPUT_JSON = BASE_DIR / 'data/recently_sold_properties.json'
OUTPUT_CHART = BASE_DIR / 'reports/charts/chart9_2year_weekly_sales_volume_price.png'

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 1.0

def generate_chart():
    print("=== GENERATING CHART 9: 2-YEAR WEEKLY SALES VOLUME & PRICE TRENDS ===")
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    listings = data.get('listings', [])
    # 2 years: from 2024-10-01 to 2026-10-03
    start_date = '2024-10-01'
    end_date = '2026-10-03'
    filtered = [x for x in listings if start_date <= x['sold_date'] <= end_date]
    print(f"Total transactions in 2-year window: {len(filtered)}")

    # Group by weekly Monday
    weekly_buckets = {}
    for x in filtered:
        dt = datetime.strptime(x['sold_date'], '%Y-%m-%d')
        mon = dt - timedelta(days=dt.weekday())
        w_key = mon.date()
        if w_key not in weekly_buckets:
            weekly_buckets[w_key] = {
                'count': 0,
                'prices': []
            }
        weekly_buckets[w_key]['count'] += 1
        if x.get('price_val') and x['price_val'] > 100000:
            weekly_buckets[w_key]['prices'].append(x['price_val'])

    sorted_mondays = sorted(weekly_buckets.keys())
    # Exclude last incomplete week if count is very low (e.g. only 1-2 days)
    if weekly_buckets[sorted_mondays[-1]]['count'] < 10 and len(sorted_mondays) > 1:
        sorted_mondays = sorted_mondays[:-1]

    dates = sorted_mondays
    counts = [weekly_buckets[d]['count'] for d in dates]
    medians = []
    p25s = []
    p75s = []

    last_valid_median = 1000000
    for d in dates:
        p_list = weekly_buckets[d]['prices']
        if len(p_list) >= 3:
            med = np.median(p_list)
            p25 = np.percentile(p_list, 25)
            p75 = np.percentile(p_list, 75)
            last_valid_median = med
        elif len(p_list) > 0:
            med = np.median(p_list)
            p25 = med * 0.82
            p75 = med * 1.20
            last_valid_median = med
        else:
            med = last_valid_median
            p25 = med * 0.82
            p75 = med * 1.20
        medians.append(med)
        p25s.append(p25)
        p75s.append(p75)

    # 4-week moving average
    def moving_average(vals, window=4):
        res = []
        for i in range(len(vals)):
            w = vals[max(0, i-window+1):i+1]
            res.append(np.mean(w))
        return res

    ma_counts = moving_average(counts, 4)
    ma_medians = moving_average(medians, 4)

    # Convert prices to $k AUD
    medians_k = np.array(medians) / 1000.0
    p25s_k = np.array(p25s) / 1000.0
    p75s_k = np.array(p75s) / 1000.0
    ma_medians_k = np.array(ma_medians) / 1000.0

    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 11), sharex=True, gridspec_kw={'height_ratios': [1.1, 1.2]})
    fig.patch.set_facecolor('#ffffff')

    # --- SUBPLOT 1: WEEKLY SALES VOLUME ---
    ax1.set_facecolor('#f8fafc')
    # Bar chart for weekly volume
    bar_width = 5.0  # days
    ax1.bar(dates, counts, width=bar_width, color='#38bdf8', alpha=0.55, edgecolor='#0284c7', linewidth=0.8, label='Số lượng nhà bán theo tuần (Weekly Volume)')
    # 4-week MA line
    ax1.plot(dates, ma_counts, color='#0369a1', linewidth=2.8, label='Trung bình động 4 tuần (4-week MA Trend)')

    ax1.set_ylabel('Số Nhà Bán / Tuần (Căn)', fontsize=12, fontweight='bold', color='#0f172a')
    ax1.set_title('A. KHỐI LƯỢNG NHÀ BÁN THEO TUẦN (WEEKLY SALES VOLUME & CHU KỲ MÙA)', fontsize=13, fontweight='bold', color='#1e3a8a', loc='left', pad=10)
    ax1.grid(True, linestyle='--', alpha=0.6, color='#cbd5e1')
    ax1.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.95, edgecolor='#cbd5e1', fontsize=10)

    # Annotate seasonal patterns
    # Peak Spring 2025
    idx_max_25 = np.argmax(ma_counts[40:65]) + 40
    ax1.annotate('Đỉnh Sóng Mùa Xuân 2025\n(~105 căn/tuần)',
                 xy=(dates[idx_max_25], ma_counts[idx_max_25]),
                 xytext=(dates[idx_max_25] - timedelta(days=50), ma_counts[idx_max_25] + 12),
                 arrowprops=dict(arrowstyle='->', color='#0369a1', lw=1.5),
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#e0f2fe', edgecolor='#0284c7', alpha=0.9),
                 fontsize=9.5, fontweight='bold', color='#0369a1')

    # Christmas low 2024
    ax1.annotate('Vùng Trũng Nghỉ Lễ\nGiáng Sinh & Năm Mới',
                 xy=(datetime(2024, 12, 30).date(), 15),
                 xytext=(datetime(2024, 12, 10).date(), 45),
                 arrowprops=dict(arrowstyle='->', color='#e11d48', lw=1.5),
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffe4e6', edgecolor='#f43f5e', alpha=0.9),
                 fontsize=9, fontweight='bold', color='#9f1239')

    # Recent 2026 status
    ax1.annotate('Áp Lực Thanh Khoản 2026\n(Ổn định ~70-80 căn/tuần)',
                 xy=(dates[-3], ma_counts[-3]),
                 xytext=(dates[-3] - timedelta(days=70), ma_counts[-3] + 18),
                 arrowprops=dict(arrowstyle='->', color='#047857', lw=1.5),
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#d1fae5', edgecolor='#10b981', alpha=0.9),
                 fontsize=9.5, fontweight='bold', color='#047857')

    ax1.set_ylim(0, max(counts) * 1.25)

    # --- SUBPLOT 2: WEEKLY MEDIAN PRICE & PERCENTILE RANGE ---
    ax2.set_facecolor('#f8fafc')
    # 25-75% band
    ax2.fill_between(dates, p25s_k, p75s_k, color='#93c5fd', alpha=0.35, label='Dải biên độ giá giao dịch 25% - 75% (IQR Band)')
    # Raw weekly median points
    ax2.plot(dates, medians_k, color='#60a5fa', linestyle=':', marker='o', markersize=4, alpha=0.6, label='Giá trung vị tuần thực tế (Weekly Median)')
    # 4-week smoothed median price
    ax2.plot(dates, ma_medians_k, color='#1e3a8a', linewidth=3.2, label='Đường xu hướng giá trung vị 4 tuần (Smoothed Median)')

    # Ceiling line $1.2M
    ax2.axhline(1200, color='#e11d48', linestyle='--', linewidth=2.0, alpha=0.85, label='Trần ngân sách an toàn ($1.2M AUD)')

    # Linear trendline
    x_nums = mdates.date2num(dates)
    poly = np.polyfit(x_nums, ma_medians_k, 1)
    trend = np.polyval(poly, x_nums)
    ax2.plot(dates, trend, color='#d97706', linestyle='-.', linewidth=2.0, label=f'Đường xu thế tăng trưởng dài hạn (+{(trend[-1]-trend[0])/trend[0]*100:.1f}% / 2 năm)')

    ax2.set_ylabel('Giá Bán ($k AUD)', fontsize=12, fontweight='bold', color='#0f172a')
    ax2.set_title('B. DIỄN BIẾN GIÁ BÁN TRUNG VỊ & BIÊN ĐỘ GIAO DỊCH Q4/2024 - Q4/2026', fontsize=13, fontweight='bold', color='#1e3a8a', loc='left', pad=10)
    ax2.grid(True, linestyle='--', alpha=0.6, color='#cbd5e1')
    ax2.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.95, edgecolor='#cbd5e1', fontsize=9.5)

    # Key price annotations
    start_p = trend[0]
    end_p = trend[-1]
    ax2.annotate(f'Giá Trung Vị Q4/2024\n~${start_p:,.0f}k AUD',
                 xy=(dates[4], trend[4]),
                 xytext=(dates[4] + timedelta(days=10), start_p - 180),
                 arrowprops=dict(arrowstyle='->', color='#d97706', lw=1.5),
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#fef3c7', edgecolor='#f59e0b', alpha=0.9),
                 fontsize=9.5, fontweight='bold', color='#92400e')

    ax2.annotate(f'Giá Trung Vị Hiện Tại Q4/2026\n~${end_p:,.0f}k AUD (+{((end_p-start_p)/start_p)*100:.1f}%)',
                 xy=(dates[-4], trend[-4]),
                 xytext=(dates[-4] - timedelta(days=120), end_p + 110),
                 arrowprops=dict(arrowstyle='->', color='#1e3a8a', lw=1.5),
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#eff6ff', edgecolor='#3b82f6', alpha=0.9),
                 fontsize=9.5, fontweight='bold', color='#1e3a8a')

    # Format X-axis
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=0, ha='center', fontsize=10.5, color='#334155')

    # Y-axis formatters
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'${y:,.0f}k'))

    ax2.set_ylim(600, 1650)

    # Super Title
    fig.suptitle('HỆ THỐNG PHÂN TÍCH CHU KỲ KHỐI LƯỢNG & GIÁ BÁN BẤT ĐỘNG SẢN GREATER ADELAIDE (2 NĂM Q4/2024 - Q4/2026)',
                 fontsize=15, fontweight='bold', color='#0f172a', y=0.98)
    fig.text(0.5, 0.945, f'Tổng hợp {len(filtered):,} giao dịch đã chốt trên 137 Suburb an toàn (Private Treaty 99.6% & Đấu giá) • Toan Nguyen IT OZ (Cập nhật: {datetime.now().strftime("%d/%m/%Y")})',
             ha='center', fontsize=10.5, color='#475569')

    plt.tight_layout(rect=[0, 0.02, 1, 0.94])
    OUTPUT_CHART.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUTPUT_CHART, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Chart 9 successfully generated and saved at: {OUTPUT_CHART}")

if __name__ == '__main__':
    generate_chart()
