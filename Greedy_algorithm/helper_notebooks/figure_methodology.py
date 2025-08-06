import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import scienceplots
# Use scienceplots style
plt.style.use(['science', 'grid', 'no-latex'])
# Create figure and axis
fig, ax = plt.subplots(figsize=(10, 6))




x_min = 0.7
x_max = 1.0
y_min = 2.0
y_max = 2.8


# Define rectangles (x_start, width, y_height)
rects = [
    {'x': 0, 'width': x_max, 'height': y_max, 'color': '#ff9999', 'label': 'Sec. 2.3'},      # full rectangle
    {'x': 0, 'width': x_min, 'height': y_max, 'color': '#ffd966', 'label': 'Sec. 2.4'},     # narrower rectangle
    {'x': 0, 'width': x_min, 'height': y_min, 'color': '#b6d7a8', 'label': 'Sec. 2.5'}  # shorter and same width
]

labels = ['Sec. 2.3 - Existence of the cycle', 
          'Sec. 2.4 - Reducing the length', 
          'Sec. 2.5 - Reducing $\mathcal{D}_J$ (eq. 6)']

# Plot rectangles
for i, rect in enumerate(rects):
    ax.add_patch(Rectangle((rect['x'], 0), rect['width'], rect['height'],
                               color=rect['color'], alpha=0.8, label=labels[i]))


ax.tick_params(axis='both', labelsize=15) 
# Add ticks and labels for x axis at ends of rectangles
ax.set_xticks([x_max, x_min])
ax.set_xticklabels(['Sec. 2.3', 'Sec. 2.4'])
ax.set_yticks([y_min, y_max])
ax.set_yticklabels(['Sec. 2.5', 'Sec. 2.3'])
# Histogram-style bars inside the smallest rectangle (just outlines)
bar_x = np.linspace(0.05, 0.65, 7)
bar_heights = [2.0, 1.7, 1.9, 2.0, 1.4, 1.7, 2.0]
bar_width = 0.10
for x, h in zip(bar_x, bar_heights):
    rect = Rectangle((x - bar_width / 2, 0), bar_width, h,
                         edgecolor='black', facecolor='none')
    ax.add_patch(rect)

# Add label 2.4 inside the smallest rectangle


# Dashed line (negative exponential style)
x_line = np.linspace(0, 1.2, 100)
y_line = 2.0 * np.exp(-2 * x_line) + 0.0
ax.plot(x_line, y_line, linestyle='--', color='blue', label='Sec. 2.6 - The Greedy Algorithm')
ax.text(0.86, y_line[-1] + 0.25, 'Sec. 2.6', color='blue', fontsize=15)

ax.text(0.293, 1.60, 'Sec. 2.7', fontsize=15, ha='center')
ax.plot([], [], color='black', label='Sec. 2.7 - Reducing $\mathcal{H}_J$ (eq. 7)')
# Final touches
ax.set_xlim(0, 1.37)
ax.set_ylim(0, 3.3)
ax.set_ylabel('Inequity of the assignment (eq. 8)', fontsize=18)
ax.set_xlabel('Cycle Length (days)', fontsize=18)
ax.spines[['top', 'right']].set_visible(False)

# add legend decribing what 2.1 to 2.5 mean, make it more transparent, and set fontsize
ax.legend(loc='upper right', fontsize=15, title='Cycle construction', title_fontsize='18', framealpha=0.4)

plt.grid(False)
plt.tight_layout()
# plt.show()

# save the figure
plt.savefig('cycle_construction.png', dpi=300, bbox_inches='tight', transparent=True)
plt.show()