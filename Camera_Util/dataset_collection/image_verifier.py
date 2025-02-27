import os
import numpy as np
import tifffile
import matplotlib.pyplot as plt

# Folder paths
cubert_folder = r"C:\Users\menon\Documents\Camera_Operation\images\exposure_testing\cubert"
thorlabs_folder = r"C:\Users\menon\Documents\Camera_Operation\images\exposure_testing\thorlabs"
output_folder = r"C:\Users\menon\Documents\Camera_Operation\images\exposure_testing\cropped"

# Create output folder if not exists
os.makedirs(output_folder, exist_ok=True)

# Define crop coordinates
cubert_crop = (75, 195, 116, 236)  # (y1, y2, x1, x2)
thorlabs_crop = (399, 1059, 1177, 1837)  # (y1, y2, x1, x2)

# Initialize stats
thorlabs_max_pixel_values = []
thorlabs_avg_pixel_values = []
thorlabs_snr_values = []

cubert_max_pixel_values = []
cubert_avg_pixel_values = []
cubert_snr_values = []

def compute_snr(image):
    """Compute SNR (Mean / Std Dev)"""
    mean_val = np.mean(image)
    std_dev = np.std(image)
    return mean_val / std_dev if std_dev != 0 else 0

def crop_and_analyze_image(path, tl_flag=True):
    """Crop image, compute statistics, and return processed image."""
    img = tifffile.imread(path)
    y1, y2, x1, x2 = thorlabs_crop if tl_flag else cubert_crop
    img_cropped = img[:, y1:y2, x1:x2]

    if tl_flag:
        # Only analyze Channel 3 of Thorlabs
        channel_3 = img_cropped[3]
        max_value = np.max(channel_3)
        avg_value = np.mean(channel_3)
        snr_value = compute_snr(channel_3)

        thorlabs_max_pixel_values.append(max_value)
        thorlabs_avg_pixel_values.append(avg_value)
        thorlabs_snr_values.append(snr_value)
    
    else:
        # Analyze the entire Cubert image
        max_value = np.max(img_cropped)
        avg_value = np.mean(img_cropped)
        snr_value = compute_snr(img_cropped)

        cubert_max_pixel_values.append(max_value)
        cubert_avg_pixel_values.append(avg_value)
        cubert_snr_values.append(snr_value)

    return img_cropped

# Process Cubert Images
cubert_images = sorted([f for f in os.listdir(cubert_folder) if f.endswith('.tif')])
thorlabs_images = sorted([f for f in os.listdir(thorlabs_folder) if f.endswith('.tif')])

cubert_crops = []
thorlabs_crops = []

for filename in cubert_images:
    path = os.path.join(cubert_folder, filename)
    cropped = crop_and_analyze_image(path, tl_flag=False)
    cubert_crops.append(cropped)
    tifffile.imwrite(os.path.join(output_folder, f"cropped_{filename}"), cropped)

for filename in thorlabs_images:
    path = os.path.join(thorlabs_folder, filename)
    cropped = crop_and_analyze_image(path, tl_flag=True)
    thorlabs_crops.append(cropped)
    tifffile.imwrite(os.path.join(output_folder, f"cropped_{filename}"), cropped)

# Compute final statistics
final_thorlabs_max_pixel_avg = np.mean(thorlabs_max_pixel_values)
final_thorlabs_avg_pixel_avg = np.mean(thorlabs_avg_pixel_values)
final_thorlabs_snr_avg = np.mean(thorlabs_snr_values)

final_cubert_max_pixel_avg = np.mean(cubert_max_pixel_values)
final_cubert_avg_pixel_avg = np.mean(cubert_avg_pixel_values)
final_cubert_snr_avg = np.mean(cubert_snr_values)

# Print final results
print("=== Thorlabs Channel 3 Statistics ===")
print(f"Max Pixel Value Average: {final_thorlabs_max_pixel_avg}")
print(f"Average Pixel Value: {final_thorlabs_avg_pixel_avg}")
print(f"SNR Average: {final_thorlabs_snr_avg}")

print("\n=== Cubert Whole Image Statistics ===")
print(f"Max Pixel Value Average: {final_cubert_max_pixel_avg}")
print(f"Average Pixel Value: {final_cubert_avg_pixel_avg}")
print(f"SNR Average: {final_cubert_snr_avg}")

# Display Thorlabs Channel 3 and Cubert Channel 1 side by side
fig, axes = plt.subplots(1, 2, figsize=(10, 5))

# Ensure we have at least one image in both lists
if cubert_crops and thorlabs_crops:
    axes[0].imshow(cubert_crops[0][0], cmap='gray')  # Channel 1 of Cubert
    axes[0].set_title("Cubert Channel 1")

    axes[1].imshow(thorlabs_crops[0][3], cmap='gray')  # Channel 3 of Thorlabs
    axes[1].set_title("Thorlabs Channel 3")

plt.tight_layout()
plt.show()
