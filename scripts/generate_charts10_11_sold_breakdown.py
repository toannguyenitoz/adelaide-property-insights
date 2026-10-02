import pathlib
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
INPUT_JSON = BASE_DIR / 'data/recently_sold_properties.json'
CHART10_PATH = BASE_DIR / 'reports/charts/chart10_sold_by_type_and_bedrooms.png'
CHART11_PATH = BASE_DIR / 'reports/charts/chart11_sold_by_region.png'

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 1.0

def load_data():
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('listings', [])

def generate_chart10(listings):
    print("=== GENERATING CHART 10: SOLD VOLUME & PRICE BY PROPERTY TYPE & BEDROOMS ===")
    
    # 1. By Property Type
    types_order = ['House', 'Townhouse', 'Unit', 'Apartment']
    type_display = {
        'House': 'House (Nhà riêng)',
        'Townhouse': 'Townhouse (Nhà liên kế)',
        'Unit': 'Unit (Căn hộ thấp tầng)',
        'Apartment': 'Apartment (Chung cư)'
    }
    type_colors = {
        'House': '#1e3a8a',
        'Townhouse': '#0284c7',
        'Unit': '#059669',
        'Apartment': '#d97706'
    }
    
    type_vol = {t: 0 for t in types_order}
    type_prices = {t: [] for t in types_order}
    
    for item in listings:
        pt = item.get('property_type') or 'House'
        if pt in type_vol:
            type_vol[pt] += 1
            if item.get('price_val') and item['price_val'] > 100000:
                type_prices[pt].append(item['price_val'])

    type_medians = {t: (np.median(type_prices[t]) if type_prices[t] else 0) for t in types_order}
    type_p25 = {t: (np.percentile(type_prices[t], 25) if type_prices[t] else 0) for t in types_order}
    type_p75 = {t: (np.percentile(type_prices[t], 75) if type_prices[t] else 0) for t in types_order}

    # 2. By Bedrooms
    bed_order = ['1 BR', '2 BR', '3 BR', '4 BR', '5+ BR']
    bed_display = ['1 Phòng Ngủ', '2 Phòng Ngủ', '3 Phòng Ngủ', '4 Phòng Ngủ', '5+ Phòng Ngủ']
    bed_colors = ['#64748b', '#0284c7', '#059669', '#d97706', '#dc2626']
    
    bed_vol = {b: 0 for b in bed_order}
    bed_prices = {b: [] for b in bed_order}
    
    for item in listings:
        b_num = item.get('bedrooms') or 3
        if b_num <= 1: b_key = '1 BR'
        elif b_num == 2: b_key = '2 BR'
        elif b_num == 3: b_key = '3 BR'
        elif b_num == 4: b_key = '4 BR'
        else: b_key = '5+ BR'
        
        bed_vol[b_key] += 1
        if item.get('price_val') and item['price_val'] > 100000:
            bed_prices[b_key].append(item['price_val'])

    bed_medians = {b: (np.median(bed_prices[b]) if bed_prices[b] else 0) for b in bed_order}
    bed_p25 = {b: (np.percentile(bed_prices[b], 25) if bed_prices[b] else 0) for b in bed_order}
    bed_p75 = {b: (np.percentile(bed_prices[b], 75) if bed_prices[b] else 0) for b in bed_order}

    # Create 2x2 Subplots Figure
    fig, axes = plt.subplots(2, 2, figsize=(16, 12), gridspec_kw={'hspace': 0.35, 'wspace': 0.28})
    fig.patch.set_facecolor('#f8fafc')
    
    total_sales = len(listings)
    
    # ----------------- SUBPLOT 1: Property Type Volume -----------------
    ax1 = axes[0, 0]
    ax1.set_facecolor('white')
    y_pos = np.arange(len(types_order))
    vols = [type_vol[t] for t in types_order]
    cols = [type_colors[t] for t in types_order]
    
    bars1 = ax1.barh(y_pos, vols, color=cols, height=0.6, edgecolor='none', alpha=0.9)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([type_display[t] for t in types_order], fontsize=11, fontweight='600')
    ax1.invert_yaxis()
    ax1.set_xlabel('Số Lượng Căn Nhà Đã Bán (Transactions)', fontsize=11, fontweight='bold', color='#1e293b')
    ax1.set_title('A. Khối Lượng Nhà Bán Theo Loại Hình (Total: 8,121 Căn)', fontsize=13, fontweight='bold', color='#0f172a', pad=12)
    ax1.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax1.set_xlim(0, max(vols) * 1.22)
    
    for bar, v in zip(bars1, vols):
        pct = (v / total_sales) * 100
        ax1.text(bar.get_width() + 100, bar.get_y() + bar.get_height()/2,
                 f"{v:,} căn ({pct:.1f}%)",
                 va='center', ha='left', fontsize=10.5, fontweight='bold', color='#0f172a')
        
    ax1.grid(axis='x', linestyle='--', alpha=0.5)

    # ----------------- SUBPLOT 2: Property Type Median Price -----------------
    ax2 = axes[0, 1]
    ax2.set_facecolor('white')
    meds = [type_medians[t] / 1000 for t in types_order]
    err_low = [type_medians[t]/1000 - type_p25[t]/1000 for t in types_order]
    err_high = [type_p75[t]/1000 - type_medians[t]/1000 for t in types_order]
    
    bars2 = ax2.bar(y_pos, meds, color=cols, width=0.52, alpha=0.9, edgecolor='#334155', linewidth=0.8,
                    yerr=[err_low, err_high], capsize=6, error_kw={'ecolor': '#475569', 'lw': 1.6})
    ax2.set_xticks(y_pos)
    ax2.set_xticklabels([t for t in types_order], fontsize=11, fontweight='700')
    ax2.set_ylabel('Giá Bán Trung Vị (nghìn AUD)', fontsize=11, fontweight='bold', color='#1e293b')
    ax2.set_title('B. Giá Bán Trung Vị & Biên Độ IQR 25-75% Theo Loại Hình', fontsize=13, fontweight='bold', color='#0f172a', pad=12)
    ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}k'))
    ax2.set_ylim(0, 2300)
    
    # Reference Line $1.2M budget
    ax2.axhline(1200, color='#dc2626', linestyle='--', linewidth=1.6, alpha=0.85)
    ax2.text(3.35, 1235, 'Ngân sách $1.20M', color='#dc2626', fontsize=10, fontweight='bold', ha='right')

    for bar, m_val, t, e_h in zip(bars2, meds, types_order, err_high):
        ax2.text(bar.get_x() + bar.get_width()/2, m_val + e_h + 55,
                 f"${m_val:,.0f}k",
                 ha='center', va='bottom', fontsize=10.5, fontweight='bold', color=type_colors[t])

    ax2.grid(axis='y', linestyle='--', alpha=0.5)

    # ----------------- SUBPLOT 3: Bedrooms Volume -----------------
    ax3 = axes[1, 0]
    ax3.set_facecolor('white')
    b_ypos = np.arange(len(bed_order))
    b_vols = [bed_vol[b] for b in bed_order]
    
    bars3 = ax3.bar(b_ypos, b_vols, color=bed_colors, width=0.56, edgecolor='none', alpha=0.9)
    ax3.set_xticks(b_ypos)
    ax3.set_xticklabels(bed_display, fontsize=10.5, fontweight='600')
    ax3.set_ylabel('Số Lượng Căn Nhà Đã Bán', fontsize=11, fontweight='bold', color='#1e293b')
    ax3.set_title('C. Phân Bổ Giao Dịch Nhà Đã Bán Theo Số Phòng Ngủ', fontsize=13, fontweight='bold', color='#0f172a', pad=12)
    ax3.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax3.set_ylim(0, max(b_vols) * 1.20)
    
    for bar, v in zip(bars3, b_vols):
        pct = (v / total_sales) * 100
        ax3.text(bar.get_x() + bar.get_width()/2, v + 80,
                 f"{v:,}\n({pct:.1f}%)",
                 ha='center', va='bottom', fontsize=10, fontweight='bold', color='#0f172a')
        
    ax3.grid(axis='y', linestyle='--', alpha=0.5)

    # ----------------- SUBPLOT 4: Bedrooms Median Price -----------------
    ax4 = axes[1, 1]
    ax4.set_facecolor('white')
    b_meds = [bed_medians[b] / 1000 for b in bed_order]
    b_err_low = [bed_medians[b]/1000 - bed_p25[b]/1000 for b in bed_order]
    b_err_high = [bed_p75[b]/1000 - bed_medians[b]/1000 for b in bed_order]
    
    bars4 = ax4.bar(b_ypos, b_meds, color=bed_colors, width=0.56, alpha=0.9, edgecolor='#334155', linewidth=0.8,
                    yerr=[b_err_low, b_err_high], capsize=6, error_kw={'ecolor': '#475569', 'lw': 1.6})
    ax4.set_xticks(b_ypos)
    ax4.set_xticklabels(bed_display, fontsize=10.5, fontweight='600')
    ax4.set_ylabel('Giá Bán Trung Vị (nghìn AUD)', fontsize=11, fontweight='bold', color='#1e293b')
    ax4.set_title('D. Giá Bán Trung Vị & Biên Độ Giá Theo Số Phòng Ngủ', fontsize=13, fontweight='bold', color='#0f172a', pad=12)
    ax4.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}k'))
    ax4.set_ylim(0, 2750)
    
    # Reference Line $1.2M budget
    ax4.axhline(1200, color='#dc2626', linestyle='--', linewidth=1.6, alpha=0.85)
    ax4.text(4.35, 1235, 'Ngân sách $1.20M', color='#dc2626', fontsize=10, fontweight='bold', ha='right')

    for bar, m_val, b, e_h in zip(bars4, b_meds, bed_order, b_err_high):
        ax4.text(bar.get_x() + bar.get_width()/2, m_val + e_h + 60,
                 f"${m_val:,.0f}k",
                 ha='center', va='bottom', fontsize=10.5, fontweight='bold', color='#0f172a')

    ax4.grid(axis='y', linestyle='--', alpha=0.5)

    # Super Title & Footer
    fig.suptitle('HỆ THỐNG BIỂU ĐỒ 10: PHÂN TÍCH NHÀ ĐÃ BÁN & GIÁ CHỐT THEO LOẠI HÌNH & PHÒNG NGỦ (GREATER ADELAIDE)',
                 fontsize=15, fontweight='900', color='#0f172a', y=0.98)
    
    fig.text(0.5, 0.01,
             'Nguồn dữ liệu: Toan Nguyen IT OZ (Tổng hợp giao dịch thực tế Homely & Domain Auctions trên 137 suburb an toàn) • Cập nhật Tháng 10/2026',
             ha='center', fontsize=9.5, color='#64748b', style='italic')

    plt.tight_layout(rect=[0, 0.025, 1, 0.96])
    CHART10_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(CHART10_PATH, dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"Chart 10 saved to: {CHART10_PATH}")


def generate_chart11(listings):
    print("=== GENERATING CHART 11: SOLD VOLUME & PRICE ACROSS 6 SAFE REGIONS ===")
    
    # Defined Regions
    regions_order = [
        'Western Coastal Corridors',
        'Norwood, Campbelltown & North-East Core',
        'City of Mitcham & Foothills',
        'Adelaide Hills & Tea Tree Gully Safe Enclaves',
        'City of Burnside & Core East',
        'City of Unley & Prestige South'
    ]
    
    region_short = {
        'Western Coastal Corridors': 'Western Coastal\n(Holdfast, Charles Sturt)',
        'Norwood, Campbelltown & North-East Core': 'Norwood & NE Core\n(Campbelltown, NPSP)',
        'City of Mitcham & Foothills': 'Mitcham & Foothills\n(Blackwood, Mitcham)',
        'Adelaide Hills & Tea Tree Gully Safe Enclaves': 'Hills & TTG Enclaves\n(Stirling, Golden Grv)',
        'City of Burnside & Core East': 'Burnside & Core East\n(Toorak Gdns, Burnside)',
        'City of Unley & Prestige South': 'Unley & Prestige South\n(Unley Park, Malvern)'
    }
    
    reg_colors = ['#0284c7', '#0d9488', '#059669', '#16a34a', '#8b5cf6', '#d97706']
    
    reg_data = {r: {'vol': 0, 'prices': [], 'types': {'House': 0, 'Townhouse': 0, 'Unit': 0, 'Apartment': 0}} for r in regions_order}
    
    for item in listings:
        r = item.get('region')
        if r in reg_data:
            reg_data[r]['vol'] += 1
            pt = item.get('property_type') or 'House'
            if pt in reg_data[r]['types']:
                reg_data[r]['types'][pt] += 1
            if item.get('price_val') and item['price_val'] > 100000:
                reg_data[r]['prices'].append(item['price_val'])

    reg_medians = {r: (np.median(reg_data[r]['prices']) if reg_data[r]['prices'] else 0) for r in regions_order}
    reg_p25 = {r: (np.percentile(reg_data[r]['prices'], 25) if reg_data[r]['prices'] else 0) for r in regions_order}
    reg_p75 = {r: (np.percentile(reg_data[r]['prices'], 75) if reg_data[r]['prices'] else 0) for r in regions_order}

    # Create 3-panel figure: 1 top wide panel (volume & price comparison), 2 bottom panels (type breakdown & type prices)
    fig = plt.figure(figsize=(16, 13))
    fig.patch.set_facecolor('#f8fafc')
    
    gs = fig.add_gridspec(2, 2, height_ratios=[1.1, 1], hspace=0.35, wspace=0.25)
    
    # ----------------- PANEL 1 (Top Spanning): Volume and Median Price by Region -----------------
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor('white')
    
    x = np.arange(len(regions_order))
    width = 0.38
    
    vols = [reg_data[r]['vol'] for r in regions_order]
    meds = [reg_medians[r] / 1000 for r in regions_order]
    
    # Dual axis: left for Volume, right for Price
    bars1 = ax1.bar(x - width/2, vols, width=width, color='#3b82f6', alpha=0.9, label='Số Lượng Căn Đã Bán (Transactions)', edgecolor='#1e40af', lw=1)
    ax1.set_ylabel('Số Lượng Nhà Đã Bán', fontsize=11, fontweight='bold', color='#1e40af')
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax1.set_ylim(0, 2450)
    
    # Add count labels on bars
    for bar, v in zip(bars1, vols):
        y_text = v + 40
        if 1150 <= v <= 1260:
            y_text = v - 90  # Put inside if near red line
            col = 'white'
        else:
            col = '#1e40af'
        ax1.text(bar.get_x() + bar.get_width()/2, y_text, f"{v:,} căn", ha='center', va='bottom' if col != 'white' else 'center', fontsize=10, fontweight='bold', color=col)
    
    ax1_twin = ax1.twinx()
    err_low = [reg_medians[r]/1000 - reg_p25[r]/1000 for r in regions_order]
    err_high = [reg_p75[r]/1000 - reg_medians[r]/1000 for r in regions_order]
    
    bars2 = ax1_twin.bar(x + width/2, meds, width=width, color='#10b981', alpha=0.85, label='Giá Bán Trung Vị (Median Price)', edgecolor='#047857', lw=1,
                         yerr=[err_low, err_high], capsize=5, error_kw={'ecolor': '#065f46', 'lw': 1.5})
    ax1_twin.set_ylabel('Giá Bán Trung Vị (nghìn AUD)', fontsize=11, fontweight='bold', color='#047857')
    ax1_twin.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}k'))
    ax1_twin.set_ylim(0, 2450)
    
    # Add price labels on bars
    for bar, m, eh in zip(bars2, meds, err_high):
        ax1_twin.text(bar.get_x() + bar.get_width()/2, m + eh + 50, f"${m:,.0f}k", ha='center', va='bottom', fontsize=10, fontweight='bold', color='#047857')
    
    # Budget line
    ax1_twin.axhline(1200, color='#dc2626', linestyle='--', linewidth=1.8, alpha=0.9)
    ax1_twin.text(len(regions_order)-0.55, 1235, 'Ngưỡng ngân sách $1.20M', color='#dc2626', fontsize=10, fontweight='bold', ha='right')

    ax1.set_xticks(x)
    ax1.set_xticklabels([region_short[r] for r in regions_order], fontsize=10, fontweight='600')
    ax1.set_title('A. Quy Mô Giao Dịch Nhà Đã Bán & Giá Bán Trung Vị Trên 6 Hành Lang An Toàn Greater Adelaide', fontsize=13, fontweight='bold', color='#0f172a', pad=14)
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', frameon=True, facecolor='white', framealpha=0.9, fontsize=10)
    ax1.grid(axis='y', linestyle='--', alpha=0.4)

    # ----------------- PANEL 2: Property Type Breakdown (% Stacked) -----------------
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor('white')
    
    house_pcts = []
    th_pcts = []
    unit_pcts = []
    apt_pcts = []
    
    for r in regions_order:
        t_dict = reg_data[r]['types']
        tot = sum(t_dict.values()) or 1
        house_pcts.append(t_dict['House'] / tot * 100)
        th_pcts.append(t_dict['Townhouse'] / tot * 100)
        unit_pcts.append(t_dict['Unit'] / tot * 100)
        apt_pcts.append(t_dict['Apartment'] / tot * 100)
        
    y_reg = np.arange(len(regions_order))
    
    p1 = ax2.barh(y_reg, house_pcts, color='#1e3a8a', height=0.55, label='House', alpha=0.9)
    p2 = ax2.barh(y_reg, th_pcts, left=house_pcts, color='#0284c7', height=0.55, label='Townhouse', alpha=0.9)
    left_unit = [h + t for h, t in zip(house_pcts, th_pcts)]
    p3 = ax2.barh(y_reg, unit_pcts, left=left_unit, color='#059669', height=0.55, label='Unit / Villa', alpha=0.9)
    left_apt = [u + a for u, a in zip(left_unit, unit_pcts)]
    p4 = ax2.barh(y_reg, apt_pcts, left=left_apt, color='#d97706', height=0.55, label='Apartment', alpha=0.9)
    
    # Add text inside large slices
    for idx, (h, t, u) in enumerate(zip(house_pcts, th_pcts, unit_pcts)):
        if h > 20:
            ax2.text(h/2, idx, f"{h:.0f}%", ha='center', va='center', color='white', fontsize=9.5, fontweight='bold')
        if t > 8:
            ax2.text(h + t/2, idx, f"{t:.0f}%", ha='center', va='center', color='white', fontsize=8.5, fontweight='bold')
        if u > 10:
            ax2.text(h + t + u/2, idx, f"{u:.0f}%", ha='center', va='center', color='white', fontsize=8.5, fontweight='bold')

    ax2.set_yticks(y_reg)
    ax2.set_yticklabels([region_short[r].split('\n')[0] for r in regions_order], fontsize=10, fontweight='600')
    ax2.invert_yaxis()
    ax2.set_xlabel('Tỷ Trọng (%) Loại Hình Trong Tổng Số Nhà Đã Bán', fontsize=10.5, fontweight='bold', color='#1e293b')
    ax2.set_title('B. Cơ Cấu Loại Nhà Giao Dịch Theo Khu Vực', fontsize=12.5, fontweight='bold', color='#0f172a', pad=12)
    ax2.set_xlim(0, 100)
    ax2.xaxis.set_major_formatter(ticker.PercentFormatter())
    ax2.legend(loc='lower center', bbox_to_anchor=(0.5, -0.22), ncol=4, frameon=True, fontsize=9.5)
    ax2.grid(axis='x', linestyle='--', alpha=0.5)

    # ----------------- PANEL 3: Median Price by Type across Regions -----------------
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor('white')
    
    house_reg_meds = []
    th_reg_meds = []
    unit_reg_meds = []
    
    for r in regions_order:
        r_props = [p for p in listings if p.get('region') == r and p.get('price_val') and p['price_val'] > 100000]
        h_p = [p['price_val'] for p in r_props if (p.get('property_type') or 'House') == 'House']
        t_p = [p['price_val'] for p in r_props if p.get('property_type') == 'Townhouse']
        u_p = [p['price_val'] for p in r_props if p.get('property_type') in ['Unit', 'Apartment']]
        
        house_reg_meds.append(np.median(h_p)/1000 if h_p else 0)
        th_reg_meds.append(np.median(t_p)/1000 if t_p else 0)
        unit_reg_meds.append(np.median(u_p)/1000 if u_p else 0)

    y_bar = np.arange(len(regions_order))
    h_bar = 0.25
    
    bars_h = ax3.barh(y_bar - h_bar, house_reg_meds, height=h_bar, color='#1e3a8a', label='House', alpha=0.9)
    bars_t = ax3.barh(y_bar, th_reg_meds, height=h_bar, color='#0284c7', label='Townhouse', alpha=0.9)
    bars_u = ax3.barh(y_bar + h_bar, unit_reg_meds, height=h_bar, color='#059669', label='Unit / Apt', alpha=0.9)
    
    # Budget line
    ax3.axvline(1200, color='#dc2626', linestyle='--', linewidth=1.6, alpha=0.85)
    ax3.text(1220, 5.2, '$1.2M', color='#dc2626', fontsize=10, fontweight='bold')

    ax3.set_yticks(y_bar)
    ax3.set_yticklabels([region_short[r].split('\n')[0] for r in regions_order], fontsize=10, fontweight='600')
    ax3.invert_yaxis()
    ax3.set_xlabel('Giá Bán Chốt Trung Vị (nghìn AUD)', fontsize=10.5, fontweight='bold', color='#1e293b')
    ax3.set_title('C. So Sánh Giá Chốt Thực Tế Giữa Các Loại Nhà', fontsize=12.5, fontweight='bold', color='#0f172a', pad=12)
    ax3.xaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}k'))
    ax3.set_xlim(0, 2100)
    ax3.legend(loc='lower center', bbox_to_anchor=(0.5, -0.22), ncol=3, frameon=True, fontsize=9.5)
    ax3.grid(axis='x', linestyle='--', alpha=0.5)

    # Super Title & Footer
    fig.suptitle('HỆ THỐNG BIỂU ĐỒ 11: PHÂN TÍCH NHÀ ĐÃ BÁN & GIÁ CHỐT THEO 6 KHU VỰC AN TOÀN GREATER ADELAIDE',
                 fontsize=15, fontweight='900', color='#0f172a', y=0.98)
    
    fig.text(0.5, 0.01,
             'Nguồn dữ liệu: Toan Nguyen IT OZ (Tổng hợp giao dịch thực tế Homely & Domain Auctions trên 137 suburb an toàn) • Cập nhật Tháng 10/2026',
             ha='center', fontsize=9.5, color='#64748b', style='italic')

    plt.tight_layout(rect=[0, 0.025, 1, 0.96])
    CHART11_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(CHART11_PATH, dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"Chart 11 saved to: {CHART11_PATH}")

def main():
    listings = load_data()
    print(f"Loaded {len(listings)} listings.")
    generate_chart10(listings)
    generate_chart11(listings)
    print("Done generating charts 10 & 11!")

if __name__ == '__main__':
    main()
