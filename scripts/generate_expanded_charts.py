import pathlib
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
import matplotlib.pyplot as plt
import numpy as np
import os

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

os.makedirs(str(BASE_DIR / 'reports/charts'), exist_ok=True)

# -------------------------------------------------------------
# CHART 5: Safety Index & Crime Rate Comparison (SAPOL Offenses per 1,000 Residents)
# -------------------------------------------------------------
# Ordered strictly from bottom (y=0: highest crime) to top (y=max: lowest crime/safest)
data_chart5 = [
    # EXCLUDED HIGH-CRIME AREAS (Red / Danger)
    {'name': 'Adelaide CBD (Postcode 5000)', 'rate': 245.0, 'safe': False, 'color': '#7f1d1d'},
    {'name': 'City of Playford (Elizabeth / Davoren Park)', 'rate': 165.4, 'safe': False, 'color': '#991b1b'},
    {'name': 'North-West Industrial (Kilburn / Mansfield Park)', 'rate': 104.2, 'safe': False, 'color': '#b91c1c'},
    {'name': 'City of Salisbury (Salisbury / Paralowie)', 'rate': 92.8, 'safe': False, 'color': '#dc2626'},
    {'name': 'South Pocket (Morphett Vale / Hackham)', 'rate': 88.5, 'safe': False, 'color': '#ef4444'},
    # APPROVED SAFE RESIDENTIAL CORRIDORS (Green / Safe)
    {'name': 'Campbelltown (Magill / Rostrevor)', 'rate': 41.8, 'safe': True, 'color': '#10b981'},
    {'name': 'Tea Tree Gully (Golden Grove / Greenwith)', 'rate': 39.4, 'safe': True, 'color': '#10b981'},
    {'name': 'City of Unley (Fullarton / Highgate / Malvern)', 'rate': 38.0, 'safe': True, 'color': '#059669'},
    {'name': 'Charles Sturt Coast (Henley Beach / Grange)', 'rate': 36.2, 'safe': True, 'color': '#059669'},
    {'name': 'Holdfast Bay Coast (Brighton / Somerton)', 'rate': 34.6, 'safe': True, 'color': '#059669'},
    {'name': 'City of Mitcham (Belair / Kingswood / Hawthorn)', 'rate': 26.2, 'safe': True, 'color': '#047857'},
    {'name': 'City of Burnside (Myrtle Bank / Glenunga / Toorak Gdns)', 'rate': 21.5, 'safe': True, 'color': '#047857'},
    {'name': 'Adelaide Hills (Stirling / Crafers / Aldgate)', 'rate': 14.8, 'safe': True, 'color': '#064e3b'},
]

suburbs = [d['name'] for d in data_chart5]
crime_rates = [d['rate'] for d in data_chart5]
colors = [d['color'] for d in data_chart5]

fig, ax = plt.subplots(figsize=(13, 8), dpi=300)
y_pos = np.arange(len(suburbs))
bars = ax.barh(y_pos, crime_rates, color=colors, alpha=0.9, height=0.68)

ax.set_yticks(y_pos)
ax.set_yticklabels(suburbs, fontsize=10, fontweight='bold')
ax.set_xlabel('Annual Offences per 1,000 Residents (SAPOL Official Crime Statistics)', fontsize=11, fontweight='bold', labelpad=10)
ax.set_title('Adelaide Safety Benchmark: Included Safe Corridors vs Excluded High-Crime Suburbs\n(Strict Security Filtering for 3-Bedroom Family Home Search)', 
             fontsize=12.5, fontweight='bold', pad=15)

# Add SAPOL High-Risk threshold line at 50 offences / 1,000
ax.axvline(x=50, color='#dc2626', linestyle='--', linewidth=1.8, alpha=0.85, label='SAPOL Safety Benchmark (<50 per 1,000)')

# Add horizontal dividing line between excluded and approved
ax.axhline(y=4.5, color='#94a3b8', linestyle=':', linewidth=1.5)
ax.text(180, 4.5, '--- KHU VUC BI LOAI TRU VI AN NINH (EXCLUDED REGIONS) ---', 
        color='#991b1b', fontsize=8.5, fontweight='bold', va='center', ha='center',
        bbox=dict(boxstyle='round,pad=0.25', facecolor='#fee2e2', edgecolor='#ef4444', alpha=0.9))

# Annotate bars
for bar, d in zip(bars, data_chart5):
    rate = d['rate']
    label = f'{rate:.1f} / 1k'
    tag = ' [DUYET - AN TOAN]' if d['safe'] else ' [LOAI TRU - NGUY CO CAO]'
    txt_color = '#047857' if d['safe'] else '#991b1b'
    ax.text(rate + 3, bar.get_y() + bar.get_height()/2, f'{label}{tag}', 
            va='center', ha='left', fontsize=8.5, fontweight='bold', 
            color=txt_color)

ax.set_xlim(0, 355)

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#047857', label='Duyệt: Khu vực An toàn Cao cấp (Rate < 50 / 1k)'),
    Patch(facecolor='#dc2626', label='Loại trừ: Khu vực Phức tạp / Tội phạm cao (Rate > 50 / 1k)'),
    plt.Line2D([0], [0], color='#dc2626', linestyle='--', linewidth=1.8, label='Ngưỡng An toàn SAPOL (< 50 offences / 1k)')
]
ax.legend(handles=legend_elements, loc='lower right', frameon=True, framealpha=0.95, facecolor='white', edgecolor='#e5e7eb', fontsize=9.5)

plt.tight_layout()
chart5_path = str(BASE_DIR / 'reports/charts/chart5_safety_index_comparison.png')
chart5_v2_path = str(BASE_DIR / 'reports/charts/chart5_safety_index_comparison_v2.png')
plt.savefig(chart5_path)
plt.savefig(chart5_v2_path)
plt.close()
print(f'Saved Chart 5: {chart5_path} and {chart5_v2_path}')


# -------------------------------------------------------------
# CHART 6: Greater Adelaide Safe Regions - Value vs Land Size vs Lifestyle Matrix
# -------------------------------------------------------------
regions = [
    'Inner East & South\n(Myrtle Bank/Glenunga)',
    'Western Coastal\n(Henley/Brighton)',
    'Eastern Foothills\n(Magill/Rostrevor)',
    'Adelaide Hills\n(Blackwood/Belair)',
    'North-East Haven\n(Golden Grove)'
]
typical_price = [1.08, 1.05, 0.94, 0.89, 0.78] # in $M
typical_land = [260, 380, 520, 820, 560] # in sqm

fig, ax1 = plt.subplots(figsize=(11, 6), dpi=300)
ax2 = ax1.twinx()

x = np.arange(len(regions))
width = 0.35

rects1 = ax1.bar(x - width/2, typical_price, width, label='Typical Asking Price ($M AUD)', color='#1e3a8a', alpha=0.9)
rects2 = ax2.bar(x + width/2, typical_land, width, label='Median Land Size (m²)', color='#059669', alpha=0.85)

ax1.set_ylabel('Typical Price for 3-Bedroom ($M AUD)', color='#1e3a8a', fontsize=11, fontweight='bold')
ax2.set_ylabel('Median Land Size (m²)', color='#059669', fontsize=11, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(regions, fontsize=10, fontweight='bold')
ax1.set_ylim(0.5, 1.3)
ax2.set_ylim(0, 1000)

for rect in rects1:
    h = rect.get_height()
    ax1.annotate(f'${h:.2f}M', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                 textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1e3a8a')

for rect in rects2:
    h = rect.get_height()
    ax2.annotate(f'{int(h)} m²', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                 textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#059669')

plt.title('Trade-Off Matrix across Safe Greater Adelaide Regions (3-Bedrooms < $1.2M)\n[Location Prestige vs Land Size vs Affordability]', 
          fontsize=12, fontweight='bold', pad=15)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', frameon=True, facecolor='white', framealpha=0.95)

plt.tight_layout()
chart6_path = str(BASE_DIR / 'reports/charts/chart6_regional_value_matrix.png')
plt.savefig(chart6_path)
plt.close()
print(f'Saved Chart 6: {chart6_path}')
