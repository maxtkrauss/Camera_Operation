import os
import numpy as np
import matplotlib.pyplot as plt
import tifffile as tiff
import cv2
from scipy.ndimage import gaussian_filter

# ---------------------------
# File Paths
# ---------------------------

# Resolution Chart Images (Top Row, Display in RGB)
chart_files = {
    "White (Chart)": r"C:\Users\menon\Documents\Camera_Operation\resolution_charts\Res_Charts_3\(255,255,255).jpg",
    "Blue (Chart)": r"C:\Users\menon\Documents\Camera_Operation\resolution_charts\Res_Charts_3\(0,0,255).jpg",
    "Green (Chart)": r"C:\Users\menon\Documents\Camera_Operation\resolution_charts\Res_Charts_3\(0,255,0).jpg",
    "Red (Chart)": r"C:\Users\menon\Documents\Camera_Operation\resolution_charts\Res_Charts_3\(255,0,0).jpg",
    "Magenta (Chart)": r"C:\Users\menon\Documents\Camera_Operation\resolution_charts\Res_Charts_3\(255,0,255).jpg"
}

# Generated Images (Bottom Row, 64, 128, 128)
generated_files = {
    "White (Gen)": r"C:\Users\menon\Documents\Camera_Operation\generation_folder\spectral\notape\generated_raw\white_gen.tif",
    "Blue (Gen)": r"C:\Users\menon\Documents\Camera_Operation\generation_folder\spectral\notape\generated_raw\blue_gen.tif",
    "Green (Gen)": r"C:\Users\menon\Documents\Camera_Operation\generation_folder\spectral\notape\generated_raw\green_gen.tif",
    "Magenta (Gen)": r"C:\Users\menon\Documents\Camera_Operation\generation_folder\spectral\notape\generated_raw\magenta_gen.tif",
    "Red (Gen)": r"C:\Users\menon\Documents\Camera_Operation\generation_folder\spectral\notape\generated_raw\red_gen.tif"
}

# Original Measurements (Middle Row - Thorlabs, 5, 660, 660)
original_files = {
    "White (TL)": r"C:\Users\menon\Documents\Camera_Operation\generation_folder\spectral\notape\thorlabs\white_tl.tif",
    "Blue (TL)": r"C:\Users\menon\Documents\Camera_Operation\generation_folder\spectral\notape\thorlabs\blue_tl.tif",
    "Green (TL)": r"C:\Users\menon\Documents\Camera_Operation\generation_folder\spectral\notape\thorlabs\green_tl.tif",
    "Magenta (TL)": r"C:\Users\menon\Documents\Camera_Operation\generation_folder\spectral\notape\thorlabs\magenta_tl.tif",
    "Red (TL)": r"C:\Users\menon\Documents\Camera_Operation\generation_folder\spectral\notape\thorlabs\red_tl.tif"
}

# ---------------------------
# Load and Process Images
# ---------------------------

def load_first_channel(file_path):
    """Loads a TIFF image and extracts the first channel."""
    if os.path.exists(file_path):
        img = tiff.imread(file_path)
        return img[0]  # First channel
    else:
        print(f"Warning: {file_path} not found.")
        return np.zeros((128, 128))  # Placeholder if missing

def load_image_cv2_rgb(file_path, target_size=(128, 128)):
    """Loads an image using OpenCV and resizes it while keeping it in RGB."""
    if os.path.exists(file_path):
        img = cv2.imread(file_path, cv2.IMREAD_COLOR)  # Load as RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
        img = cv2.resize(img, target_size)
        return img
    else:
        print(f"Warning: {file_path} not found.")
        return np.zeros((*target_size, 3), dtype=np.uint8)  # Black placeholder if missing

def sharpen_image(image, alpha=1.5, sigma=1.0):
    """Applies an unsharp mask to sharpen the image."""
    blurred = gaussian_filter(image, sigma=sigma)
    sharpened = image + alpha * (image - blurred)
    return np.clip(sharpened, 0, 255)  # Ensure values are within range

# Load images
chart_images = {label: load_image_cv2_rgb(path) for label, path in chart_files.items()}
generated_images = {label: load_first_channel(path) for label, path in generated_files.items()}
original_images = {label: load_first_channel(path) for label, path in original_files.items()}

# Apply sharpening to generated images
sharpened_generated = {label: sharpen_image(img) for label, img in generated_images.items()}

# ---------------------------
# Plot Images
# ---------------------------

fig, axes = plt.subplots(2, 5, figsize=(15, 9))

# Top Row: Resolution Charts (RGB)
for ax, (label, img) in zip(axes[0], chart_images.items()):
    ax.imshow(img)  # No colormap, keep full RGB
    ax.axis("off")

# Middle Row: Original Measurements (Thorlabs, Viridis)
for ax, (label, img) in zip(axes[1], original_images.items()):
    ax.imshow(img, cmap="viridis")
    ax.axis("off")

# # Bottom Row: Generated Images (Sharpened, Viridis)
# for ax, (label, img) in zip(axes[2], sharpened_generated.items()):
#     ax.imshow(img, cmap="viridis")
#     ax.axis("off")


# Adjust layout
plt.tight_layout()
plt.subplots_adjust(top=0.88)  # Give space for title

# Save and Show the Plot
plt.savefig("comparison_plot.svg", format="svg", dpi=300)
plt.show()
