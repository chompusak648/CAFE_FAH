import matplotlib.pyplot as plt
import matplotlib as mpl

# Set Thai font - Windows common font or fallback
plt.rcParams['font.family'] = 'Tahoma' # Common on Windows
plt.rcParams['axes.unicode_minus'] = False

# Data
menus = ['กาแฟ', 'โกโก้', 'ชาเขียว', 'นมสด', 'ชาไทย']
sugar_per_100g = [8.5, 12.0, 14.0, 10.0, 16.0] # Sample data based on Thai Cafe standards (grams per 100g)
colors = ['#8B4513', '#D2691E', '#228B22', '#F5F5DC', '#FF8C00']

# Create plot
plt.figure(figsize=(10, 6), dpi=100)
bars = plt.bar(menus, sugar_per_100g, color=colors, edgecolor='black', alpha=0.8)

# Add titles and labels
plt.title('เปรียบเทียบปริมาณน้ำตาลในเมนูเครื่องดื่ม (ต่อ 100 กรัม)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('ปริมาณน้ำตาล (กรัม)', fontsize=12)
plt.xlabel('เมนูเครื่องดื่ม', fontsize=12)

# Add value labels on top of bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.3, f'{yval}g', ha='center', va='bottom', fontsize=10, fontweight='bold')

# styling
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.gca().set_facecolor('#FFFDF9')
plt.gcf().set_facecolor('#FFFDF9')

# Save and show
plt.tight_layout()
plt.savefig('sugar_comparison.png')
print("Graph saved as sugar_comparison.png")
# plt.show() # Uncomment if running in interactive env
