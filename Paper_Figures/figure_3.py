import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ---------------------------
# File Paths for Each Polarization Angle
# ---------------------------
data_files = {
    "0° Polarized": {
        "Ground Truth": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\0_degree\a_white_gen.csv",
        "Blue": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\0_degree\0_blue_gen.csv",
        "Green": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\0_degree\0_green_gen.csv",
        "Magenta": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\0_degree\0_magenta_gen.csv",
        "Red": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\0_degree\0_red_gen.csv",
    },
    "45° Polarized": {
        "Ground Truth": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\45_degree\a_white_gen.csv",
        "Blue": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\45_degree\45_blue_gen.csv",
        "Green": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\45_degree\45_green_gen.csv",
        "Magenta": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\45_degree\45_magenta_gen.csv",
        "Red": r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping\45_degree\45_red_gen.csv",
    },
    "90° Polarized": {
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
# Set Up Figure with Three Subplots
# ---------------------------
fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
plt.style.use("seaborn-v0_8-muted")

all_handles = []
all_labels = []

# ---------------------------
# Generate Three Plots (0°, 45°, 90° Polarization)
# ---------------------------
for ax, (polarization, files) in zip(axes, data_files.items()):
    for label, file_path in files.items():
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} not found.")
            continue
        
        # Load CSV data
        df = pd.read_csv(file_path, delimiter=",", encoding="utf-8-sig").drop_duplicates(subset=["Wavelength"])
        
        # Extract wavelength and contrast limits
        resolution_points = []
        for _, row in df.iterrows():
            wavelength = row["Wavelength"]
            for j, col in enumerate(df.columns[1:]):  
                if row[col] < 0.2:
                    resolution_points.append((wavelength, angular_resolution[j]))  # Fixed resolution levels
                    break
        
        resolution_df = pd.DataFrame(resolution_points, columns=["Wavelength", "Angular Resolution"])
        color = color_map.get(label, "gray")
        
        # Plot spectral component
        line, = ax.plot(resolution_df["Wavelength"], resolution_df["Angular Resolution"],
                         marker='o', linestyle='-', color=color, markersize=4, linewidth=1.5, label=label)
        
        # Collect handles for legend
        if label not in all_labels:
            all_handles.append(line)
            all_labels.append(label)
    
    # Set labels
    #ax.set_title(polarization, fontsize=14)
    #ax.set_xlabel("Wavelength (nm)", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.5)

#axes[0].set_ylabel("Angular Resolution (Degrees)", fontsize=12)

# ---------------------------
# Combined Legend
##fig.subplots_adjust(right=1.5)  # Adjust space for the legend
fig.legend(handles=all_handles, labels=["","","","","","","",""], loc="center right", fontsize=10, frameon=False)

# ---------------------------
# Show the Final Plot
# ---------------------------
plt.tight_layout(rect=[0, 0, 0.85, 1])  # Prevent overlap with legend
plt.savefig("spectral_polarimetric_comparison.svg", format="svg", dpi=300)
plt.show()
