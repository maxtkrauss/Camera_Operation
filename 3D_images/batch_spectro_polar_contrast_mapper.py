import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

# Define parent directory
base_directory = r"C:\Users\menon\Documents\Camera_Operation\csv_data\gen\spectral_bifringence\evening_total(spectro-polarimetric-notapewhites)\spectro_polarimetric_mapping"

# Subdirectories for each polarization
polarization_folders = {
    "0°": os.path.join(base_directory, "0_degree"),
    "45°": os.path.join(base_directory, "45_degree"),
    "90°": os.path.join(base_directory, "90_degree")
}

# Expected color names (column headers)
color_names = ["Blue", "Green", "Magenta", "Red", "Striped", "White"]
file_suffixes = ["blue", "green", "magenta", "red", "striped", "white"]

# Define angular resolution labels
angular_resolution = ['0.33', '0.18', '0.17', '0.15', '0.13', '0.11', '0.09', '0.07', '0.06']

# Create figure with subplots (3 rows, 6 columns)
fig, axes = plt.subplots(3, 6, figsize=(18, 12))  
fig.suptitle("Generated Spectral-Polarimetric Contrast Maps with Contours (Smoothed via Gaussian Convolution)", fontsize=16, fontweight="bold")

# Flatten axes array for easy iteration
axes = axes.flatten()

# Track subplot index
plot_index = 0

# Prepare output for the command line neatly
print("\n" + "="*50)
print("Low Contrast Count (LCC) for Each Polarization & Color")
print("="*50)

# Loop through each polarization folder
for pol_label, pol_folder in polarization_folders.items():
    for color_index, color in enumerate(file_suffixes):
        file_name = f"{pol_label.split('°')[0]}_{color}_gen.csv"
        file_path = os.path.join(pol_folder, file_name)

        # Check if file exists before proceeding
        if not os.path.exists(file_path):
            print(f"⚠ Missing file: {file_path}, skipping...")
            continue

        # Load the CSV file
        df = pd.read_csv(file_path, delimiter=",", encoding="utf-8-sig")

        # Convert DataFrame to NumPy array
        data_array = df.to_numpy()

        # Extract wavelengths (first column)
        wavelengths = data_array[:, 0]

        # Extract contrast values (remaining columns)
        contrast_values = data_array[:, 1:]
        num_groups = contrast_values.shape[1]  # Number of angular resolution groups

        # Apply Gaussian smoothing to reduce artifacts
        smoothed_contrast_values = gaussian_filter(contrast_values, sigma=1)

        # Plot the contrast map
        im = axes[plot_index].imshow(
            smoothed_contrast_values, aspect="auto", cmap="RdBu",
            extent=[1, num_groups + 1, wavelengths[-1], wavelengths[0]]
        )

        # Set axis labels
        axes[plot_index].set_xlabel("Angular Resolution (Degrees)", fontsize=10)
        axes[plot_index].set_ylabel("Wavelength (nm)", fontsize=10)

        # Align xticks with angular resolution groups
        tick_positions = np.arange(1, num_groups + 1)
        axes[plot_index].set_xticks(tick_positions)
        axes[plot_index].set_xticklabels(angular_resolution[:num_groups], rotation=45, ha="right")

        # Add contour overlay at contrast < 0.1
        axes[plot_index].contourf(
            smoothed_contrast_values, levels=[0, 0.1], colors="black", alpha=0.4,
            extent=[1, num_groups + 1, wavelengths[0], wavelengths[-1]]
        )

        # Compute the count of low-contrast pixels
        low_contrast_region = contrast_values < 0.1  
        num_low_contrast_pixels = np.sum(low_contrast_region)  

        # Format title with proper spacing
        axes[plot_index].set_title(
            f"{pol_label} {color_names[color_index]}\nLCC: {num_low_contrast_pixels}",
            fontsize=10, pad=12
        )

        # Print neatly formatted output in CMD
        print(f"{pol_label} {color_names[color_index]:<10} | LCC: {num_low_contrast_pixels}")

        # Add a colorbar for each subplot
        fig.colorbar(im, ax=axes[plot_index], label="Contrast")

        # Increment subplot index
        plot_index += 1

# Adjust layout for better visualization
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()
