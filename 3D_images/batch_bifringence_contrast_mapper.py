# Import necessary libraries
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

# Define the directory containing CSV files
directory = r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\polarimetric_mapping"  # Modify this path as needed

# Dynamically list all CSV files in the directory
file_paths = [os.path.join(directory, f) for f in sorted(os.listdir(directory)) if f.endswith(".csv")]

# Titles for each subplot (Reference on top, Cellophane-Induced Birefringence on bottom)
titles = [
    "0° Cellophane-Induced Birefringence", "45° Cellophane-Induced Birefringence", "90° Cellophane-Induced Birefringence",
    "0° Reference (No Birefringence)", "45° Reference (No Birefringence)", "90° Reference (No Birefringence)"
]

# Define angular resolution labels
angular_resolution = ['0.33', '0.18', '0.17', '0.15', '0.13', '0.11', '0.09', '0.07', '0.06']

# Create figure with subplots
fig, axes = plt.subplots(2, 3, figsize=(15, 10))  # 2 rows, 3 columns
fig.suptitle("Generated Polarimetric Contrast Maps with Contours", fontsize=14, fontweight="bold")

# Flatten axes array for easy iteration
axes = axes.flatten()

# Store AUC values for comparison
auc_values = []

# Loop through file paths and plot contrast maps
for i, file_path in enumerate(file_paths):
    df = pd.read_csv(file_path, delimiter=",", encoding="utf-8-sig")

    # Convert DataFrame to NumPy array
    data_array = df.to_numpy()

    # Extract wavelengths (first column)
    wavelengths = data_array[:, 0]

    # Extract contrast values (remaining columns)
    contrast_values = data_array[:, 1:]
    num_groups = contrast_values.shape[1]  # Determine number of columns

    # Apply Gaussian smoothing to reduce artifacts
    smoothed_contrast_values = gaussian_filter(contrast_values, sigma=1)

    # Plot the contrast map
    im = axes[i].imshow(
        contrast_values, aspect="auto", cmap="RdBu",
        extent=[1, num_groups + 1, wavelengths[-1], wavelengths[0]]
    )

    # Set title and axis labels
    axes[i].set_xlabel("Angular Resolution (Degrees)")
    axes[i].set_ylabel("Wavelength (nm)")

    # Ensure that xticks align **exactly** with each group
    tick_positions = np.arange(1, num_groups + 1)  # Ensures tick positions are integers (1-based)
    axes[i].set_xticks(tick_positions)
    axes[i].set_xticklabels(angular_resolution[:num_groups], rotation=45, ha="right")

    # Add smoothed contour overlay at contrast = 0.1
    axes[i].contourf(
        contrast_values, levels=[0, 0.1], colors="black", alpha=0.4,
        extent=[1, num_groups + 1, wavelengths[0], wavelengths[-1]]
    )

    # Calculate the area under the contour (region where contrast < 0.1)
    low_contrast_region = contrast_values < 0.1  # Boolean mask
    num_low_contrast_pixels = np.sum(low_contrast_region)  # Count pixels in low-contrast region

    
    # Count the number of pixels where contrast < 0.1
    auc = np.sum(contrast_values < 0.1)


    # Store AUC value for comparison
    auc_values.append(auc)
    print(f"ALCC for {titles[i]}: {auc}")

    # Update subplot title with AUC value
    axes[i].set_title(f"{titles[i]}\nLow Contrast Count: {auc:}", fontsize=12)

    # Add a colorbar for each subplot
    fig.colorbar(im, ax=axes[i], label="Contrast")

# Adjust layout for better visibility
plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust layout to prevent title overlap
plt.show()


plt.show()
