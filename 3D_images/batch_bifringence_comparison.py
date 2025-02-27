import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

# List of CSV file paths (No Tape first, Tape second for each angle)
file_paths = [
    (r"C:\Users\menon\Documents\Camera_Operation\csv_data\bifringence\green\0_gt.csv",
     r"C:\Users\menon\Documents\Camera_Operation\csv_data\bifringence\green\0_tape.csv"),
    (r"C:\Users\menon\Documents\Camera_Operation\csv_data\bifringence\green\45_gt.csv",
     r"C:\Users\menon\Documents\Camera_Operation\csv_data\bifringence\green\45_tape.csv"),
    (r"C:\Users\menon\Documents\Camera_Operation\csv_data\bifringence\green\90_gt.csv",
     r"C:\Users\menon\Documents\Camera_Operation\csv_data\bifringence\green\90_tape.csv")
]

angles = ["0°", "45°", "90°"]
pearson_values = []

fig, axes = plt.subplots(1, 3, figsize=(15, 5))  # 1 row, 3 columns
fig.suptitle("Birefringence Contrast Difference Maps", fontsize=16, fontweight="bold")

# Loop through each angle and generate heat maps
for i, (no_tape_file, tape_file) in enumerate(file_paths):
    # Read CSV files
    df_no_tape = pd.read_csv(no_tape_file, delimiter=",", encoding="utf-8-sig").to_numpy()
    df_tape = pd.read_csv(tape_file, delimiter=",", encoding="utf-8-sig").to_numpy()

    # Extract contrast values (only the first 7 columns after Wavelength)
    contrast_no_tape = df_no_tape[:, 1:8]
    contrast_tape = df_tape[:, 1:8]

    # Compute difference map (absolute difference)
    diff_map = np.abs(contrast_no_tape - contrast_tape)

    # Compute Pearson Correlation between No Tape and Tape (flattened arrays)
    pearson_r, _ = pearsonr(contrast_no_tape.flatten(), contrast_tape.flatten())
    pearson_values.append(pearson_r)

    # Plot Difference Map
    im = axes[i].imshow(diff_map, aspect="auto", cmap="magma",
                        extent=[1, 7, df_no_tape[:, 0][-1], df_no_tape[:, 0][0]])
    axes[i].set_title(f"{angles[i]} Difference Map", fontsize=12)
    axes[i].set_xlabel("Angular Resolution (Degrees)")
    axes[i].set_ylabel("Wavelength (nm)")

    # Add a colorbar for each subplot
    fig.colorbar(im, ax=axes[i], label="Absolute Difference")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()

# Print Pearson Correlation Results
for i, angle in enumerate(angles):
    print(f"Pearson Correlation ({angle}): {pearson_values[i]:.2f}")
