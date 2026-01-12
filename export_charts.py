"""
Export visualizations to PNG using matplotlib (reliable, no hanging)
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
import os

print("Configuring matplotlib for high-quality PNG export...")
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['font.size'] = 12

# Create outputs/charts directory
os.makedirs('outputs/charts', exist_ok=True)

# Load the data
print("Loading data...")
df = pd.read_csv('data/sample_hces_data.csv')
print(f"✓ Loaded {len(df):,} records")

print("\nCreating visualizations for export...\n")

# 1. Household Size vs Adoption Chart
print("1. Creating HH size vs adoption chart...")
hh_size_groups = df.groupby('Household_Size').agg({
    'Online_Purchase': 'mean'
}).reset_index()
hh_size_groups['Online_Purchase'] = hh_size_groups['Online_Purchase'] * 100

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(hh_size_groups['Household_Size'], hh_size_groups['Online_Purchase'], 
        marker='o', linewidth=3, markersize=10, color='#1f77b4')
ax.set_xlabel('Household Size', fontsize=14, fontweight='bold')
ax.set_ylabel('Online Purchase Adoption (%)', fontsize=14, fontweight='bold')
ax.set_title('Household Size vs Online Purchase Adoption', fontsize=16, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)
ax.set_ylim(0, max(hh_size_groups['Online_Purchase']) * 1.1)
plt.tight_layout()
print("   Exporting hh_size_adoption.png...")
plt.savefig('outputs/charts/hh_size_adoption.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved hh_size_adoption.png")

# 2. Category Skew Chart
print("\n2. Creating category skew chart...")
categories = ['Food', 'Medicine', 'Consumables', 'Electronics']
single_rates = []
family_rates = []

for cat in categories:
    col_name = f'Online_{cat}'
    single_rate = df[df['Household_Size'] <= 2][col_name].mean() * 100
    family_rate = df[df['Household_Size'] >= 4][col_name].mean() * 100
    single_rates.append(single_rate)
    family_rates.append(family_rate)

skew_index = [s/f if f > 0 else 0 for s, f in zip(single_rates, family_rates)]

fig, ax = plt.subplots(figsize=(12, 6))
colors = ['#2ecc71' if x > 1 else '#e74c3c' for x in skew_index]
bars = ax.bar(categories, skew_index, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax.axhline(y=1.0, color='gray', linestyle='--', linewidth=2, alpha=0.7, label='Baseline (1.0x)')
ax.set_xlabel('Category', fontsize=14, fontweight='bold')
ax.set_ylabel('Skew Index (>1 = Singles Over-Index)', fontsize=14, fontweight='bold')
ax.set_title('Category Skew Index: Single/Small HH vs Family HH', fontsize=16, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')
ax.legend(fontsize=12)

# Add value labels on bars
for bar, value in zip(bars, skew_index):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{value:.2f}x',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.tight_layout()
print("   Exporting category_skew.png...")
plt.savefig('outputs/charts/category_skew.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved category_skew.png")

# 3. State-wise Penetration (Top 10)
print("\n3. Creating state penetration chart...")
state_penetration = df.groupby('State').agg({
    'Online_Purchase': 'mean'
}).reset_index()
state_penetration['Online_Purchase'] = state_penetration['Online_Purchase'] * 100
state_penetration = state_penetration.sort_values('Online_Purchase', ascending=False).head(10)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(range(len(state_penetration)), state_penetration['Online_Purchase'], 
              color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
ax.set_xticks(range(len(state_penetration)))
ax.set_xticklabels(state_penetration['State'], rotation=45, ha='right')
ax.set_xlabel('State', fontsize=14, fontweight='bold')
ax.set_ylabel('Penetration (%)', fontsize=14, fontweight='bold')
ax.set_title('Top 10 States by Online Purchase Penetration', fontsize=16, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar, value in zip(bars, state_penetration['Online_Purchase']):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{value:.1f}%',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
print("   Exporting state_penetration.png...")
plt.savefig('outputs/charts/state_penetration.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved state_penetration.png")

# 4. Internet Access Impact
print("\n4. Creating internet impact chart...")
internet_impact = df.groupby('Internet_Access').agg({
    'Online_Purchase': 'mean'
}).reset_index()
internet_impact['Online_Purchase'] = internet_impact['Online_Purchase'] * 100
internet_labels = ['No Internet', 'Has Internet']

fig, ax = plt.subplots(figsize=(12, 6))
colors_internet = ['#e74c3c', '#2ecc71']
bars = ax.bar(internet_labels, internet_impact['Online_Purchase'], 
              color=colors_internet, alpha=0.8, edgecolor='black', linewidth=2, width=0.5)
ax.set_xlabel('Internet Access', fontsize=14, fontweight='bold')
ax.set_ylabel('Adoption (%)', fontsize=14, fontweight='bold')
ax.set_title('Internet Access vs Online Purchase Adoption', fontsize=16, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')
ax.set_ylim(0, max(internet_impact['Online_Purchase']) * 1.15)

# Add value labels on bars
for bar, value in zip(bars, internet_impact['Online_Purchase']):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{value:.1f}%',
            ha='center', va='bottom', fontsize=14, fontweight='bold')

# Add gap annotation
gap = internet_impact['Online_Purchase'].iloc[1] - internet_impact['Online_Purchase'].iloc[0]
ax.text(0.5, max(internet_impact['Online_Purchase']) * 0.5, 
        f'{gap:.0f}pp gap',
        ha='center', fontsize=14, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

plt.tight_layout()
print("   Exporting internet_impact.png...")
plt.savefig('outputs/charts/internet_impact.png', dpi=150, bbox_inches='tight')
plt.close()
print("   ✓ Saved internet_impact.png")

print("\n" + "="*60)
print("✅ All charts exported successfully to outputs/charts/")
print("="*60)
print("\nGenerated files:")
print("  📊 hh_size_adoption.png")
print("  📈 category_skew.png")
print("  🗺️  state_penetration.png")
print("  🌐 internet_impact.png")
print("\nNo hanging issues - matplotlib export completed successfully!")
