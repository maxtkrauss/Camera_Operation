import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Simulate directory containing multiple CSV files
directory = r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral"

# List all CSV files in the directory
file_paths = [os.path.join(directory, f) for f in sorted(os.listdir(directory)) if f.endswith(".csv")]

# Corresponding titles for each plot (assuming the number of files matches these titles)
titles = [
    "Blue",
    "Green",
    "Magenta",
    "Red",
    "Magenta & Green Striped",
    "White (Reference)"
]

# Define angular resolution labels as numeric values for plotting
angular_resolution = [0.19, 0.18, 0.17, 0.15, 0.13, 0.11, 0.09, 0.07, 0.06]

import matplotlib.colors as mcolors

# Define softer color palette for better visualization
soft_colors = {
    "Blue": mcolors.to_rgba("steelblue", alpha=0.8),
    "Green": mcolors.to_rgba("mediumseagreen", alpha=0.8),
    "Magenta": mcolors.to_rgba("mediumpurple", alpha=0.8),
    "Red": mcolors.to_rgba("indianred", alpha=0.8),
    "Magenta & Green Striped": mcolors.to_rgba("peru", alpha=0.8),
    "White (Reference)": "black"
}

# Set up the figure with a minimalistic design
plt.figure(figsize=(10, 6))
plt.style.use("seaborn-v0_8-muted")  # Compatible version


# Loop through all CSV files and plot their data with soft colors
for i, file_path in enumerate(file_paths):
    df = pd.read_csv(file_path, delimiter=",", encoding="utf-8-sig")
    df = df.drop_duplicates(subset=["Wavelength"])

    # Identify the angular resolution where contrast drops below 0.2
    threshold = 0.2
    resolution_points = []

    for _, row in df.iterrows():
        wavelength = row["Wavelength"]

        for j, col in enumerate(df.columns[1:]):  # Skip "Wavelength" column
            if row[col] < threshold:
                resolution_points.append((wavelength, angular_resolution[j]))
                break

    resolution_df = pd.DataFrame(resolution_points, columns=["Wavelength", "Angular Resolution"])

    label = titles[i] if i < len(titles) else f"Dataset {i+1}"
    color = soft_colors.get(label, "gray")  # Default to gray if not mapped

    plt.plot(resolution_df["Wavelength"], resolution_df["Angular Resolution"],
             marker='o', linestyle='-', color=color, markersize=4, linewidth=1.5, label=label)

# Ensure all angular resolution values are shown on the Y-axis
yticks_labels = ["" if tick == 0.19 else str(tick) for tick in angular_resolution]
plt.yticks(angular_resolution, yticks_labels)
plt.xlabel("Wavelength (nm)", fontsize=12)
plt.ylabel("Angular Resolution (Degrees)", fontsize=12)
#plt.title("Peak Angular Resolution for Each Wavelength Before Contrast Falls Below 0.2", fontsize=14)
plt.legend(frameon=True, loc="upper center", fontsize=8, ncol=len(titles))
plt.grid(True, linestyle="--", alpha=0.6)
plt.show()

