import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Simulate directory containing multiple CSV files
directory = r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\bifringence_1-29"

# List all CSV files in the directory
file_paths = [os.path.join(directory, f) for f in sorted(os.listdir(directory)) if f.endswith(".csv")]

# Corresponding titles for each plot (assuming the number of files matches these titles)
titles = [
    "0° Polarization",
    "45° Polarization",
    "90° Polarization",
    "Unpolarized (Reference)"
]

# Define angular resolution labels as numeric values for plotting
angular_resolution = [0.19, 0.18, 0.17, 0.15, 0.13, 0.11]

import matplotlib.colors as mcolors

# Define updated color map with more visually distinct yet refined colors
distinct_colors = {
    "0° Polarization": "darkkhaki",
    "45° Polarization": "lightsalmon",
    "90° Polarization": "cadetblue",
    "Unpolarized (Reference)": "black"
}

# Remove the unused 0.33 data point from angular resolution
filtered_angular_resolution = [0.19, 0.18, 0.17, 0.15, 0.13, 0.11]

# Set up the updated figure
plt.figure(figsize=(10, 6))
plt.style.use("seaborn-v0_8-muted")


# Loop through all CSV files and plot their data with updated colors
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
    color = distinct_colors.get(label, "gray")  # Default to gray if not mapped

    plt.plot(resolution_df["Wavelength"], resolution_df["Angular Resolution"],
             marker='o', linestyle='-', color=color, markersize=4, linewidth=1.5, label=label)

# Ensure the updated angular resolution values are shown on the Y-axis
yticks_labels = ["" if tick == 0.19 else str(tick) for tick in angular_resolution]
plt.yticks(angular_resolution, yticks_labels)


# Labels, title, and legend
plt.xlabel("Wavelength (nm)", fontsize=12)
plt.ylabel("Angular Resolution (Degrees)", fontsize=12)
#plt.title("Peak Angular Resolution for Each Wavelength Before Contrast Falls Below 0.2", fontsize=14)
plt.legend(frameon=True, loc="upper center", fontsize=8, ncol=len(titles))
plt.grid(True, linestyle="--", alpha=0.6)

# Show the refined plot
plt.show()


