import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.colors as mcolors

# ---------------------------
# Primary Dataset: Angular Resolution vs. Wavelength
# ---------------------------

directory_angular = r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral"
file_paths_angular = [os.path.join(directory_angular, f) for f in sorted(os.listdir(directory_angular)) if f.endswith(".csv")]

# Remove "Magenta & Green Striped"
titles_angular = [
    "Ground Truth",
    "Blue",
    "Green",
    "Magenta",
    "Red"
]

angular_resolution = [0.19, 0.18, 0.17, 0.15, 0.13, 0.11, 0.09, 0.07, 0.06]

soft_colors_angular = {
    "Blue": "steelblue",
    "Green": "mediumseagreen",
    "Magenta": "mediumpurple",
    "Red": "indianred",
    "Ground Truth": "black"
}

# ---------------------------
# Secondary Dataset: Polarization Angular Resolution vs. Wavelength
# ---------------------------

directory_polarization = r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\bifringence_1-29"
file_paths_polarization = [os.path.join(directory_polarization, f) for f in sorted(os.listdir(directory_polarization)) if f.endswith(".csv")]

titles_polarization = [
    "0° Polarized",
    "45° Polarized",
    "90° Polarized",
    "Ground Truth"
]

soft_colors_polarization = {
    "0° Polarized": "darkkhaki",
    "45° Polarized": "lightsalmon",
    "90° Polarized": "cadetblue",
    "Ground Truth": "black"
}

# ---------------------------
# Set Up Figure with Two Subplots
# ---------------------------

fig, axes = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={'width_ratios': [1, 1]})
plt.style.use("seaborn-v0_8-muted")

# Collect legend handles
all_handles = []
all_labels = []

# ---------------------------
# Plot 1: Angular Resolution vs. Wavelength
# ---------------------------
ax1 = axes[0]

for i, (file_path, title) in enumerate(zip(file_paths_angular, titles_angular)):
    df = pd.read_csv(file_path, delimiter=",", encoding="utf-8-sig").drop_duplicates(subset=["Wavelength"])

    resolution_points = []
    for _, row in df.iterrows():
        wavelength = row["Wavelength"]
        for j, col in enumerate(df.columns[1:]):  
            if row[col] < 0.2:
                resolution_points.append((wavelength, angular_resolution[j]))
                break

    resolution_df = pd.DataFrame(resolution_points, columns=["Wavelength", "Angular Resolution"])
    color = soft_colors_angular.get(title, "gray")

    line, = ax1.plot(resolution_df["Wavelength"], resolution_df["Angular Resolution"],
                      marker='o', linestyle='-', color=color, markersize=4, linewidth=1.5, label=title)

    all_handles.append(line)
    all_labels.append(title)

#ax1.set_xlabel("Wavelength (nm)", fontsize=12)
#ax1.set_ylabel("Angular Resolution (Degrees)", fontsize=12)
ax1.set_yticks(angular_resolution)
ax1.set_yticklabels(["" if tick == 0.19 else str(tick) for tick in angular_resolution])
ax1.grid(True, linestyle="--", alpha=0.5)

# ---------------------------
# Plot 2: Polarization Angular Resolution vs. Wavelength
# ---------------------------

angular_resolution_polarization = [0.19, 0.18, 0.17, 0.15, 0.13, 0.11]

ax2 = axes[1]
for i, (file_path, title) in enumerate(zip(file_paths_polarization, titles_polarization)):
    df = pd.read_csv(file_path, delimiter=",", encoding="utf-8-sig").drop_duplicates(subset=["Wavelength"])

    resolution_points = []
    for _, row in df.iterrows():
        wavelength = row["Wavelength"]
        for j, col in enumerate(df.columns[1:]):  
            if row[col] < 0.2:
                resolution_points.append((wavelength, angular_resolution_polarization[j]))
                break

    resolution_df = pd.DataFrame(resolution_points, columns=["Wavelength", "Angular Resolution"])
    color = soft_colors_polarization.get(title, "gray")

    line, = ax2.plot(resolution_df["Wavelength"], resolution_df["Angular Resolution"],
                      marker='o', linestyle='-', color=color, markersize=4, linewidth=1.5, label=title)

    all_handles.append(line)
    all_labels.append(title)

#ax2.set_xlabel("Wavelength (nm)", fontsize=12)
#ax2.set_ylabel("Angular Resolution (Degrees)", fontsize=12)
ax2.set_yticks(angular_resolution_polarization)
ax2.set_yticklabels(["" if tick == 0.19 else str(tick) for tick in angular_resolution_polarization])
ax2.grid(True, linestyle="--", alpha=0.5)

# ---------------------------
# Remove Duplicate "Ground Truth" Label from Legend
# ---------------------------
seen_labels = set()
unique_handles = []
unique_labels = []

for handle, label in zip(all_handles, all_labels):
    if label == "Ground Truth" and label in seen_labels:
        continue  # Skip duplicate "Ground Truth"
    seen_labels.add(label)
    unique_handles.append(handle)
    unique_labels.append(label)

# ---------------------------
# Combined Legend to the Right
# ---------------------------
fig.subplots_adjust(right=0.85)  # Make space for the legend
fig.legend(handles=unique_handles, labels=["","","","","","","",""], loc="center right", fontsize=10, frameon=False)

# ---------------------------
# Show the Final Plot
# ---------------------------
plt.tight_layout(rect=[0, 0, 0.85, 1])  # Prevent overlap with legend
plt.savefig("angular_resolution_plot.svg", format="svg", dpi=300)
plt.show()
