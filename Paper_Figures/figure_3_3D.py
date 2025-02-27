import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ---------------------------
# File Paths for Each Polarization Angle
# ---------------------------
data_files = {
    "0": {
        "Ground Truth": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\0_degree\a_white_gen.csv",
        "Blue": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\0_degree\0_blue_gen.csv",
        "Green": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\0_degree\0_green_gen.csv",
        "Magenta": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\0_degree\0_magenta_gen.csv",
        "Red": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\0_degree\0_red_gen.csv",
    },
    "45": {
        "Ground Truth": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\45_degree\a_white_gen.csv",
        "Blue": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\45_degree\45_blue_gen.csv",
        "Green": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\45_degree\45_green_gen.csv",
        "Magenta": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\45_degree\45_magenta_gen.csv",
        "Red": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\45_degree\45_red_gen.csv",
    },
    "90": {
        "Ground Truth": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\90_degree\a_white_gen.csv",
        "Blue": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\90_degree\90_blue_gen.csv",
        "Green": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\90_degree\90_green_gen.csv",
        "Magenta": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\90_degree\90_magenta_gen.csv",
        "Red": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\90_degree\90_red_gen.csv",
    }
}

# ---------------------------
# Fixed Angular Resolution Levels
# ---------------------------
angular_resolution = [0.19, 0.18, 0.17, 0.15, 0.13, 0.11, 0.09, 0.07, 0.06]

# ---------------------------
# Colors for Different Spectral Components
# ---------------------------
color_map = {
    "Blue": "steelblue",
    "Green": "mediumseagreen",
    "Magenta": "mediumpurple",
    "Red": "indianred",
    "Ground Truth": "black"
}

# ---------------------------
# Create 3D Plot
# ---------------------------
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# ---------------------------
# Generate 3D Plots for Each Polarization Angle
# ---------------------------
for z_pos, files in data_files.items():
    for label, file_path in files.items():
        # Load CSV data
        if not os.path.exists(file_path):
            continue

        df = pd.read_csv(file_path, delimiter=",", encoding="utf-8-sig").drop_duplicates(subset=["Wavelength"])

        # Extract wavelength and contrast limits
        resolution_points = []
        for _, row in df.iterrows():
            wavelength = row["Wavelength"]
            for j, col in enumerate(df.columns[1:]):
                if row[col] < 0.2:
                    resolution_points.append((wavelength, angular_resolution[j]))
                    break

        resolution_df = pd.DataFrame(resolution_points, columns=["Wavelength", "Angular Resolution"])
        color = color_map.get(label, "gray")

        # Plot spectral component in 3D
        ax.plot(resolution_df["Wavelength"], resolution_df["Angular Resolution"], zs=z_pos, zdir='z',
                marker='o', linestyle='-', color=color, markersize=4, linewidth=1.5, label=f"{label} ({z_pos}°)")

# ---------------------------
# Axis Labels and Title
# ---------------------------
ax.set_xlabel("Wavelength (nm)", fontsize=12)
ax.set_ylabel("Angular Resolution (Degrees)", fontsize=12)
ax.set_zlabel("Polarization Angle (Degrees)", fontsize=12)
ax.set_yticks(angular_resolution)

# Rotate for better visibility
ax.view_init(elev=25, azim=45)

# ---------------------------
# Show Plot
# ---------------------------
plt.title("Spectro-Polarimetric Angular Resolution", fontsize=14)
plt.show()
