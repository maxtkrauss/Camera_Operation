import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

# List of CSV file paths (excluding White, which is the ground truth)
file_paths = [
    r"C:\Users\menon\Documents\Camera_Operation\csv_data\spectral\Blue_cubert.csv",
    r"C:\Users\menon\Documents\Camera_Operation\csv_data\spectral\Green_cubert.csv",
    r"C:\Users\menon\Documents\Camera_Operation\csv_data\spectral\Magenta_cubert.csv",
    r"C:\Users\menon\Documents\Camera_Operation\csv_data\spectral\Red_cubert.csv",
    r"C:\Users\menon\Documents\Camera_Operation\csv_data\spectral\Striped_cubert.csv"
]

# Ground truth (White Cubert) file
ground_truth_file = r"C:\Users\menon\Documents\Camera_Operation\csv_data\spectral\White_cubert.csv"

# Titles for each plot
titles = [
    "Difference Map: Blue vs White",
    "Difference Map: Green vs White",
    "Difference Map: Magenta vs White",
    "Difference Map: Red vs White",
    "Difference Map: Striped vs White"
]

# Define angular resolution labels (keeping only first 7 values)
angular_resolution = ['0.33', '0.18', '0.17', '0.15', '0.13', '0.11', '0.09']

# Set number of groups manually (7 groups only)
num_groups = len(angular_resolution)

# Read the ground truth (White Cubert)
df_white = pd.read_csv(ground_truth_file, delimiter=",", encoding="utf-8-sig").to_numpy()
contrast_white = df_white[:, 1:8]  # Extract only first 7 contrast columns

# Create figure with subplots (2 rows, 3 columns)
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Set figure title
fig.suptitle("Spectral Contrast Difference Maps (vs. White Cubert)", fontsize=16, fontweight="bold")

# Flatten axes array for easy iteration
axes = axes.flatten()

# Store Pearson correlation values
pearson_values = []

# Loop through file paths and compute difference maps
for i, file_path in enumerate(file_paths):
    df_color = pd.read_csv(file_path, delimiter=",", encoding="utf-8-sig").to_numpy()
    
    # Extract contrast values (keeping only first 7 columns after Wavelength)
    contrast_color = df_color[:, 1:8]

    # Compute difference map (absolute difference)
    diff_map = np.abs(contrast_color - contrast_white)

    # Compute Pearson Correlation between color and white reference
    pearson_r, _ = pearsonr(contrast_color.flatten(), contrast_white.flatten())
    pearson_values.append(pearson_r)

    # Plot Difference Map
    im = axes[i].imshow(diff_map, aspect="auto", cmap="magma",
                        extent=[1, num_groups, df_color[:, 0][-1], df_color[:, 0][0]])
    axes[i].set_title(titles[i], fontsize=12)
    axes[i].set_xlabel("Angular Resolution (Degrees)")
    axes[i].set_ylabel("Wavelength (nm)")

    # Ensure that xticks align to the **center** of each group
    tick_positions = np.linspace(1 + 0.5, num_groups - 0.5, num_groups)
    axes[i].set_xticks(tick_positions)
    axes[i].set_xticklabels(angular_resolution, rotation=45, ha="right")

    # Add a colorbar for each subplot
    fig.colorbar(im, ax=axes[i], label="Absolute Difference")

# Adjust layout for better visibility
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()

# Print Pearson Correlation Results
for i, title in enumerate(titles):
    print(f"{title}: Pearson Correlation = {pearson_values[i]:.2f}")
