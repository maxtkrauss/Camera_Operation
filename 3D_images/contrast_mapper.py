import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the CSV file into a DataFrame
file_path = r"C:\Users\menon\Documents\Camera_Operation\csv_data\(255,255,0)_cubert.csv"
df = pd.read_csv(file_path, delimiter=",", encoding="utf-8-sig")

# Convert DataFrame to NumPy array
data_array = df.to_numpy()

# Extract wavelengths (first column)
wavelengths = data_array[:, 0]

# Extract contrast values (remaining columns)
contrast_values = data_array[:, 1:]

# Define group labels
group_labels = ["Group 2-1", "Group 2-6", "Group 3-1", "Group 3-2", 
                "Group 3-3", "Group 3-4", "Group 3-5", "Group 3-6"]

# Plot with corrected axes
plt.figure(figsize=(8, 6))
plt.imshow(contrast_values, aspect="auto", cmap="RdBu", 
           extent=[1, 8, wavelengths[-1], wavelengths[0]])  # Switch x and y

plt.colorbar(label="Contrast")
plt.xlabel("Group Number")
plt.ylabel("Wavelength (nm)")
plt.title("Contrast Variation Across Groups for Red (255,255,0)")

# Correct x-axis labels
plt.xticks(ticks=np.arange(1, 9), labels=group_labels, rotation=45)

plt.show()
