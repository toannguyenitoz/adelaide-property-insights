import pathlib
import matplotlib.pyplot as plt
import numpy as np
import os

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / 'reports/charts'
os.makedirs(str(OUTPUT_DIR), exist_ok=True)

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

# 23 Suburbs spanning all councils of Greater Adelaide
# Ordered from Safest (lowest crime rate) to Highest Crime Rate
suburbs_data = [
    # (Suburb / Area, Council / Region, Rate 2023-24, Rate 2024-25)
    ("Adelaide Hills (Stirling / Crafers)", "Adelaide Hills", 15.2, 14.8),
    ("Burnside (Toorak Gardens / Myrtle Bank)", "City of Burnside", 20.8, 21.5),
    ("Walkerville (Walkerville / Medindie)", "Town of Walkerville", 22.5, 23.2),
    ("Unley (Unley Park / Malvern / Highgate)", "City of Unley", 24.8, 25.5),
    ("Mitcham (Belair / Kingswood)", "City of Mitcham", 25.6, 26.2),
    ("Holdfast Bay (Brighton / Somerton)", "City of Holdfast Bay", 33.8, 34.6),
    ("Charles Sturt Coast (Henley Beach / Grange)", "City of Charles Sturt", 35.1, 36.2),
    ("Norwood Payneham (Norwood / Kensington)", "City of NPSP", 36.9, 37.8),
    ("Tea Tree Gully North (Golden Grove / Greenwith)", "City of Tea Tree Gully", 38.5, 39.4),
    ("Campbelltown (Magill / Rostrevor)", "City of Campbelltown", 40.7, 41.8),
    ("Marion South (Hallett Cove / Sheidow Park)", "City of Marion", 44.2, 45.6),
    ("Charles Sturt Mid (Woodville / Findon)", "City of Charles Sturt", 48.6, 50.2),
    ("Tea Tree Gully Mid (Modbury / Ridgehaven)", "City of Tea Tree Gully", 51.2, 53.0),
    ("West Torrens (Mile End / Torrensville)", "City of West Torrens", 61.5, 63.8),
    ("Marion Central (Marion / Park Holme)", "City of Marion", 66.8, 69.4),
    ("Port Adelaide Enfield East (Blair Athol / Enfield)", "City of PAE", 78.5, 81.2),
    ("Onkaparinga Central (Morphett Vale / Hackham)", "City of Onkaparinga", 85.9, 88.5),
    ("Salisbury Central (Salisbury / Paralowie)", "City of Salisbury", 89.8, 92.8),
    ("Port Adelaide Enfield West (Kilburn / Mansfield Park)", "City of PAE", 100.5, 104.2),
    ("Port Adelaide Historic (Port Adelaide / Rosewater)", "City of PAE", 118.2, 122.5),
    ("Onkaparinga Outer (Christie Downs / Hackham West)", "City of Onkaparinga", 124.0, 128.6),
    ("Playford Central (Elizabeth / Davoren Park)", "City of Playford", 159.5, 165.4),
    ("Adelaide CBD (Central Business District 5000)", "City of Adelaide", 238.5, 245.0),
]

# Reverse for horizontal bar chart (so safest appears at the TOP)
suburbs_data_rev = suburbs_data[::-1]

labels = [f"{d[0]}" for d in suburbs_data_rev]
rates_23_24 = [d[2] for d in suburbs_data_rev]
rates_24_25 = [d[3] for d in suburbs_data_rev]

n = len(suburbs_data_rev)
y = np.arange(n)
height = 0.38

fig, ax = plt.subplots(figsize=(14, 12.5), dpi=300)

# Colors
color_23_24 = '#94a3b8' # Slate grey / light cool grey for past year
colors_24_25 = []
for r in rates_24_25:
    if r < 30:
        colors_24_25.append('#047857') # Dark Emerald (Very Safe)
    elif r < 50:
        colors_24_25.append('#0d9488') # Teal / Green (Safe)
    elif r < 75:
        colors_24_25.append('#d97706') # Amber (Moderate)
    elif r < 120:
        colors_24_25.append('#ea580c') # Orange-Red (Elevated)
    else:
        colors_24_25.append('#b91c1c') # Dark Crimson (High Crime)

# Plot grouped horizontal bars
bars1 = ax.barh(y - height/2, rates_23_24, height, label='Năm 2023 - 2024 (Năm trước)', color=color_23_24, alpha=0.85, edgecolor='none')
bars2 = ax.barh(y + height/2, rates_24_25, height, label='Năm 2024 - 2025 (Năm gần nhất)', color=colors_24_25, alpha=0.95, edgecolor='none')

# Add value annotations
for b1, b2, r1, r2 in zip(bars1, bars2, rates_23_24, rates_24_25):
    diff = r2 - r1
    sign = "+" if diff > 0 else ""
    ax.text(r2 + 2.5, b2.get_y() + b2.get_height()/2, f"{r2:.1f} ({sign}{diff:.1f})", 
            va='center', ha='left', fontsize=8.5, fontweight='bold', color='#0f172a')

# Metro Adelaide Average Line (~71.2 / 1k in 2024-25)
ax.axvline(x=71.2, color='#6366f1', linestyle='--', linewidth=1.8, label='Trung bình toàn Greater Adelaide (71.2 / 1k dân)')

# Threshold lines for safety tiers
ax.axvline(x=50.0, color='#10b981', linestyle=':', linewidth=1.5, alpha=0.8, label='Ngưỡng an toàn cao (< 50 vụ / 1.000 dân)')

# Set ticks and labels
ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=9.5, fontweight='bold', color='#1e293b')
ax.set_xlabel('Số Vụ Vi Phạm Ghi Nhận Hàng Năm Trên 1.000 Dân Cư (Recorded Offences per 1,000 Population)\nNguồn dữ liệu: Thống kê chính thức Cảnh sát Nam Úc (SAPOL Crime Statistics)', 
              fontsize=10.5, fontweight='bold', labelpad=12, color='#0f172a')

# Title (Pure Crime, No Real Estate)
ax.set_title('BẢNG SO SÁNH TỶ LỆ TỘI PHẠM CÁC KHU VỰC TẠI GREATER ADELAIDE TRONG 2 NĂM GẦN NHẤT\n(Tương quan thống kê an ninh thường niên 2023-2024 so với 2024-2025 theo cảnh sát SAPOL)', 
             fontsize=12.5, fontweight='bold', pad=18, color='#0f172a', linespacing=1.4)

ax.set_xlim(0, 310)

from matplotlib.patches import Patch
from matplotlib.lines import Line2D

legend_elements = [
    Patch(facecolor=color_23_24, label='Năm 2023 - 2024 (Năm trước)'),
    Patch(facecolor='#047857', label='Năm 2024 - 2025: Rất an toàn (< 30 vụ/1k)'),
    Patch(facecolor='#0d9488', label='Năm 2024 - 2025: An toàn (< 50 vụ/1k)'),
    Patch(facecolor='#d97706', label='Năm 2024 - 2025: Mức trung bình (50 - 75 vụ/1k)'),
    Patch(facecolor='#ea580c', label='Năm 2024 - 2025: Mức cao (75 - 120 vụ/1k)'),
    Patch(facecolor='#b91c1c', label='Năm 2024 - 2025: Mức rất cao (> 120 vụ/1k)'),
    Line2D([0], [0], color='#6366f1', linestyle='--', linewidth=1.8, label='Mức trung bình toàn Adelaide (71.2/1k)'),
    Line2D([0], [0], color='#10b981', linestyle=':', linewidth=1.5, label='Ngưỡng an toàn cao (< 50/1k)')
]

ax.legend(handles=legend_elements, loc='upper right', frameon=True, framealpha=0.96, facecolor='white', edgecolor='#cbd5e1', fontsize=9.5, ncol=1)

plt.tight_layout()

chart_path = str(OUTPUT_DIR / 'adelaide_suburb_crime_rates_2year_comparison.png')
plt.savefig(chart_path, bbox_inches='tight')
plt.close()
print(f"Chart saved successfully at: {chart_path}")
