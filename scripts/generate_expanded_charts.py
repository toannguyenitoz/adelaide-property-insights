import matplotlib.pyplot as plt
import numpy as np
import os

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

os.makedirs('d:/Looking for a home/reports/charts', exist_ok=True)

# -------------------------------------------------------------
# CHART 5: Safety Index & Crime Rate Comparison (SAPOL Offenses per 1,000 Residents)
# -------------------------------------------------------------
suburbs = [
    'Adelaide Hills (Stirling/Crafers/Aldgate)',
    'Burnside (Myrtle Bank/Glenunga)',
    'Mitcham & Foothills (Belair/Kingswood)',
    'Holdfast Bay Coast (Brighton/Somerton)',
    'Charles Sturt Coast (Henley/Grange)',
    'Unley (Fullarton/Highgate)',
    'Tea Tree Gully (Golden Grove/Greenwith)',
    'Campbelltown (Magill/Rostrevor)',
    '--- EXCLUDED UNSAFE AREAS ---',
    'Morphett Vale / Hackham (South Pocket)',
    'Salisbury / Paralowie (North Central)',
    'Kilburn / Mansfield Park (North-West)',
    'Elizabeth / Davoren Park (Far North)',
    'Adelaide CBD (Postcode 5000)'
]

crime_rates = [
    14.8, 21.5, 26.2, 34.6, 36.2, 38.0, 39.4, 41.8,
    0, # separator
    88.5, 92.8, 104.2, 165.4, 245.0
]

colors = [
    '#059669', '#059669', '#10b981', '#10b981', '#10b981', '#10b981', '#34d399', '#34d399',
    '#ffffff',
    '#ef4444', '#dc2626', '#b91c1c', '#991b1b', '#7f1d1d'
]

fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
y_pos = np.arange(len(suburbs))
bars = ax.barh(y_pos[::-1], crime_rates[::-1], color=colors[::-1], alpha=0.9, height=0.65)

ax.set_yticks(y_pos[::-1])
ax.set_yticklabels(suburbs, fontsize=10, fontweight='bold')
ax.set_xlabel('Annual Offences per 1,000 Residents (SAPOL Official Crime Statistics)', fontsize=11, fontweight='bold', labelpad=10)
ax.set_title('Adelaide Safety Benchmark: Included Safe Corridors vs Excluded High-Crime Suburbs\n(Strict Security Filtering for 3-Bedroom Property Search)', 
             fontsize=12.5, fontweight='bold', pad=15)

# Annotate bars
for bar, rate in zip(bars, crime_rates[::-1]):
    if rate > 0:
        label = f'{rate:.1f} / 1k'
        tag = ' [SAFE / APPROVED]' if rate < 50 else ' [EXCLUDED / UNSAFE]'
        ax.text(rate + 2, bar.get_y() + bar.get_height()/2, label + tag, 
                va='center', ha='left', fontsize=8.5, fontweight='bold', 
                color='#059669' if rate < 50 else '#991b1b')

ax.set_xlim(0, 290)

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#059669', label='Selected Safe Regions (Grade A / A+ Safety)'),
    Patch(facecolor='#dc2626', label='Excluded High-Crime / Social Housing Pockets (Filtered Out)')
]
ax.legend(handles=legend_elements, loc='lower right', frameon=True, framealpha=0.95, facecolor='white', edgecolor='#e5e7eb', fontsize=10)

plt.tight_layout()
chart5_path = 'd:/Looking for a home/reports/charts/chart5_safety_index_comparison.png'
plt.savefig(chart5_path)
plt.close()
print(f'Saved Chart 5: {chart5_path}')


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
chart6_path = 'd:/Looking for a home/reports/charts/chart6_regional_value_matrix.png'
plt.savefig(chart6_path)
plt.close()
print(f'Saved Chart 6: {chart6_path}')
