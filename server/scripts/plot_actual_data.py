import matplotlib.pyplot as plt
import numpy as np

# Data extraction
minutes = []
y_values = []

# Raw data
data = '''
0 (bottom) y=495.5
1 (bottom) y=495.5
2 Left Click at: x=568, y=417
3 Left Click at: x=590, y=404
4 Left Click at: x=589, y=386
5 Left Click at: x=656, y=331
6 Left Click at: x=676, y=316
7 Left Click at: x=698, y=291
8 Left Click at: x=714, y=271
9 Left Click at: x=709, y=280
10 Left Click at: x=730, y=250
11 Left Click at: x=734, y=251
12 Left Click at: x=755, y=231
13 Left Click at: x=754, y=232
14 Left Click at: x=753, y=236
15 Left Click at: x=766, y=230
16 Left Click at: x=783, y=210
17 Left Click at: x=790, y=204
18 Left Click at: x=801, y=190
19 Left Click at: x=798, y=196
20 Left Click at: x=800, y=189
21 Left Click at: x=806, y=183
22 Left Click at: x=817, y=179
23 Left Click at: x=824, y=168
24 Left Click at: x=823, y=169
25 Left Click at: x=828, y=167
26 Left Click at: x=833, y=158
29 Left Click at: x=845, y=144
30 Left Click at: x=835, y=158
'''

# Constants
TOP = 153.5
BOTTOM = 495.5
TOTAL_HEIGHT = BOTTOM - TOP

# Process data
for line in data.strip().split('\n'):
    if 'y=' in line:
        minute = int(line.split()[0])
        y_value = float(line.split('y=')[1])
        
        # Skip minutes 27 and 28 as specified
        if minute not in [27, 28]:
            minutes.append(minute)
            y_values.append(y_value)

# Calculate fill percentages
fill_percentages = [(BOTTOM - y) / TOTAL_HEIGHT * 100 for y in y_values]

# Create the plot
plt.figure(figsize=(12, 6))
plt.plot(minutes, fill_percentages, 'b-o', linewidth=2, markersize=6)
plt.grid(True, linestyle='--', alpha=0.7)

# Customize the plot
plt.title('Rick\'s Line Length Over Time (Actual)', fontsize=14, pad=15)
plt.xlabel('Time (minutes)', fontsize=12)
plt.ylabel('Fill Percentage (%)', fontsize=12)

# Set y-axis limits from 0 to 100%
plt.ylim(0, 100)

# Add minor gridlines
plt.grid(True, which='minor', linestyle=':', alpha=0.4)
plt.minorticks_on()

# Show the plot
plt.tight_layout()
plt.show()

# Print some statistics
print(f"\nStatistics:")
print(f"Initial fill percentage: {fill_percentages[0]:.1f}%")
print(f"Final fill percentage: {fill_percentages[-1]:.1f}%")
print(f"Maximum fill percentage: {max(fill_percentages):.1f}%")