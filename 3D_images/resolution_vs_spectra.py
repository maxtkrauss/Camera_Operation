import matplotlib.pyplot as plt
import numpy as np

# Groups for X-axis labels
groups = ["Group 2-1", "Group 2-6", "Group 3-1", "Group 3-2", "Group 3-3", "Group 3-4", "Group 3-5", "Group 3-6"]

# Contrast values for different images
contrast_data = {
    "(255,255,255)": [0.78, 0.35, 0.23, 0.17, 0.15, 0.11, 0.12, 0.1],
    "(255,0,255)": [0.82, 0.51, 0.42, 0.37, 0.33, 0.25, 0.22, 0.16],
    "(255,0,0)": [0.86, 0.62, 0.56, 0.52, 0.48, 0.38, 0.29, 0.18],
    "(0,255,0)": [0.89, 0.67, 0.59, 0.53, 0.44, 0.33, 0.28, 0.18],
    "(0,255,0)/(255,0,255)": [0.9, 0.77, 0.73, 0.68, 0.59, 0.5, 0.44, 0.35]
}

# Define custom colors for each spectral condition
color_map = {
    "(255,255,255)": "black",  # White appears as black for visibility
    "(255,0,255)": (1, 0, 1),  # Magenta
    "(255,0,0)": (1, 0, 0),  # Red
    "(0,255,0)": (0, 1, 0),  # Green
}

# Define striped color for (0,255,0)-(255,0,255)
striped_colors = [(0, 1, 0), (1, 0, 1)]  # Alternating between green and magenta

# Plot contrast values
plt.figure(figsize=(10, 6))

for label, contrasts in contrast_data.items():
    plt.plot(groups, contrasts, marker='o', linestyle='-', label=label)

plt.axhline(y=0.1, color='r', linestyle='--', label="Resolution Threshold (0.10)")

plt.xlabel("Resolution Chart Groups")
plt.ylabel("Average Contrast")
plt.title("Contrast Across Resolution Groups for Different Spectral Variations")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)

plt.show()


# Groups for X-axis labels
groups = ["Group 2-1", "Group 2-6", "Group 3-1", "Group 3-2", "Group 3-3", "Group 3-4", "Group 3-5", "Group 3-6"]

# Contrast values for different images and their corresponding peak wavelengths
contrast_peak_data = {
    "(255,255,255)": ([0.8783, 0.5771, 0.4632, 0.2839, 0.3375, 0.4587, 0.4032, 0.2823], 
                       [478.4, 474.4, 697.9, 482.5, 701.9, 701.9, 701.9, 701.9]),
    "(255,0,255)": ([0.9558, 0.9245, 0.8856, 0.8263, 0.7662, 0.5673, 0.6311, 0.5109], 
                    [559.7, 559.7, 563.8, 563.8, 555.7, 543.5, 563.8, 563.8]),
    "(255,0,0)": ([0.9967, 0.9749, 0.9258, 0.9288, 0.8993, 0.7587, 0.6401, 0.5172], 
                  [478.4, 486.6, 482.5, 482.5, 478.4, 454.1, 563.8, 563.9]),
    "(0,255,0)": ([0.9753, 0.9578, 0.9152, 0.8785, 0.8371, 0.7708, 0.5567, 0.4702], 
                  [657.2, 466.3, 466.3, 466.3, 466.3, 454.1, 645.0, 616.6]),
    "(0,255,0)-(255,0,255)": ([0.9646, 0.9375, 0.9374, 0.8872, 0.8716, 0.7897, 0.8170, 0.7451], 
                               [657.2, 555.7, 563.8, 563.8, 563.8, 567.8, 563.8, 563.8])
}

# Create a figure for Peak Contrast Values
plt.figure(figsize=(10, 6))
for label, (contrast_values, _) in contrast_peak_data.items():
    plt.plot(groups, contrast_values, marker='o', linestyle='-', label=label)

plt.xlabel("Resolution Chart Groups")
plt.ylabel("Peak Contrast Value")
plt.title("Peak Contrast Across Resolution Groups")
plt.legend()
plt.grid(True)
plt.show()

# Create a figure for Peak Contrast Wavelengths
plt.figure(figsize=(10, 6))
for label, (_, wavelengths) in contrast_peak_data.items():
    plt.plot(groups, wavelengths, marker='o', linestyle='-', label=label)

plt.xlabel("Resolution Chart Groups")
plt.ylabel("Peak Contrast Wavelength (nm)")
plt.title("Peak Contrast Wavelengths Across Resolution Groups")
plt.legend()
plt.grid(True)
plt.show()



