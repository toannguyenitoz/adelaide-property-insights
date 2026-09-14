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
# CHART 7: Annual Operating & Holding Cost Breakdown: House vs Townhouse vs Unit vs Apartment
# -------------------------------------------------------------
types = ['Freestanding House\n(Torrens Title)', 'Townhouse\n(Community Title)', 'Single-Storey Unit\n(Strata / Villa)', 'Apartment\n(Mid/High-Rise)']

# Stacked Cost Components ($k / year)
council_water_esl = np.array([3.8, 3.0, 2.5, 2.3]) # Council + SA Water + ESL
strata_body_corp = np.array([0.0, 2.0, 1.4, 6.2])  # Strata levies (Admin + Sinking)
insurance = np.array([1.8, 0.4, 0.4, 0.4])         # Building + Contents (only contents for strata)
maint_reserve = np.array([3.0, 1.5, 1.0, 1.2])     # Repairs, gardening, replacement
net_energy = np.array([1.2, 1.6, 1.5, 2.8])        # Electricity & Gas (House with 6.6kW Solar vs Apartment on Grid)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5), dpi=300, gridspec_kw={'width_ratios': [1.2, 1]})

# Subplot 1: Stacked Annual Holding Costs
bar_width = 0.55
indices = np.arange(len(types))

p1 = ax1.bar(indices, council_water_esl, bar_width, label='Council Rates + SA Water + ESL', color='#1e3a8a')
p2 = ax1.bar(indices, strata_body_corp, bar_width, bottom=council_water_esl, label='Strata / Community Levies', color='#dc2626')
p3 = ax1.bar(indices, insurance, bar_width, bottom=council_water_esl + strata_body_corp, label='Insurance (Building + Contents)', color='#059669')
p4 = ax1.bar(indices, maint_reserve, bar_width, bottom=council_water_esl + strata_body_corp + insurance, label='Maintenance & Repairs Reserve', color='#d97706')
p5 = ax1.bar(indices, net_energy, bar_width, bottom=council_water_esl + strata_body_corp + insurance + maint_reserve, label='Energy & Utilities (Net of Solar)', color='#7c3aed')

totals = council_water_esl + strata_body_corp + insurance + maint_reserve + net_energy

for i, total in enumerate(totals):
    ax1.text(i, total + 0.25, f'${total:.1f}k / yr\n(~${int(total*1000/12)}/mo)', 
             ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#0f172a')

ax1.set_ylabel('Annual Operating & Holding Cost ($k AUD)', fontsize=11, fontweight='bold')
ax1.set_title('Annual Holding & Operating Cost Breakdown\n(3-Bedroom Home in Adelaide)', fontsize=12, fontweight='bold', pad=12)
ax1.set_xticks(indices)
ax1.set_xticklabels(types, fontsize=9.5, fontweight='bold')
ax1.set_ylim(0, 16)
ax1.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.95, fontsize=8.5)

# Subplot 2: 10-Year Wealth Creation Outlook (Capital Growth vs Holding Costs)
# Estimated 10-year Capital Gain on $1M purchase vs 10-year Cumulative Holding Costs
gains_10yr = [850, 680, 520, 260] # $k (House gains ~85% in Adelaide, Townhouse ~68%, Unit ~52%, Apartment ~26%)
costs_10yr = [totals[0]*10*1.1, totals[1]*10*1.1, totals[2]*10*1.1, totals[3]*10*1.1] # $k with 2% inflation

x = np.arange(len(types))
w = 0.35

b1 = ax2.bar(x - w/2, gains_10yr, w, label='Estimated 10-Yr Capital Gain ($k)', color='#10b981')
b2 = ax2.bar(x + w/2, costs_10yr, w, label='10-Yr Cumulative Holding Cost ($k)', color='#f43f5e')

for rect in b1:
    h = rect.get_height()
    ax2.annotate(f'+${int(h)}k', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                 textcoords="offset points", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#047857')

for rect in b2:
    h = rect.get_height()
    ax2.annotate(f'-${int(h)}k', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                 textcoords="offset points", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#be123c')

ax2.set_ylabel('10-Year Projection Value ($k AUD)', fontsize=11, fontweight='bold')
ax2.set_title('10-Year Net Wealth Creation Comparison\n(Capital Growth vs Holding Costs)', fontsize=12, fontweight='bold', pad=12)
ax2.set_xticks(x)
ax2.set_xticklabels(types, fontsize=9.5, fontweight='bold')
ax2.set_ylim(0, 1050)
ax2.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.95, fontsize=8.5)

plt.tight_layout()
chart7_path = str(BASE_DIR / 'reports/charts/chart7_property_type_cost_comparison.png')
plt.savefig(chart7_path)
plt.close()
print(f'Saved Chart 7: {chart7_path}')
