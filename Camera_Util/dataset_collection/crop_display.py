import tifffile
import numpy as np
import matplotlib.pyplot as plt



# File paths
thorlabs_tif = r"C:\Users\menon\Documents\Camera_Operation\images\video_testing\thorlabs\100207720.jpg_thorlabs.tif"
cubert_tif = r"C:\Users\menon\Documents\Camera_Operation\images\video_testing\cubert\100207720.jpg_cubert.tif"

import os

import os

print(f"Thorlabs file size: {os.path.getsize(thorlabs_tif)} bytes")
print(f"Cubert file size: {os.path.getsize(cubert_tif)} bytes")



# Define crop function
def crop_image(img, tl_flag):
    """ Crop image based on Thorlabs or Cubert camera. """
    crop_coords = ((1250, 1910), (510, 1170)) if tl_flag else ((136, 256), (89, 209))
    
    if img.ndim > 2:  # If image has multiple channels
        cropped_img = img[:, crop_coords[1][0]:crop_coords[1][1], crop_coords[0][0]:crop_coords[0][1]]
    else:
        cropped_img = img[crop_coords[1][0]:crop_coords[1][1], crop_coords[0][0]:crop_coords[0][1]]
    
    return cropped_img

# Load images
tl_img = tifffile.imread(thorlabs_tif)
cb_img = tifffile.imread(cubert_tif)

# Crop images
tl_img_cropped = crop_image(tl_img, tl_flag=True)
cb_img_cropped = crop_image(cb_img, tl_flag=False)

# Plot images before and after cropping
fig, axs = plt.subplots(2, 2, figsize=(10, 8))

# Display Thorlabs Image
axs[0, 0].imshow(tl_img[0], cmap='gray') if tl_img.ndim > 2 else axs[0, 0].imshow(tl_img, cmap='gray')
axs[0, 0].set_title("Thorlabs - Original")
axs[0, 0].axis("off")

axs[0, 1].imshow(tl_img_cropped[0], cmap='gray') if tl_img_cropped.ndim > 2 else axs[0, 1].imshow(tl_img_cropped, cmap='gray')
axs[0, 1].set_title("Thorlabs - Cropped")
axs[0, 1].axis("off")

# Display Cubert Image
axs[1, 0].imshow(cb_img[0], cmap='gray') if cb_img.ndim > 2 else axs[1, 0].imshow(cb_img, cmap='gray')
axs[1, 0].set_title("Cubert - Original")
axs[1, 0].axis("off")

axs[1, 1].imshow(cb_img_cropped[0], cmap='gray') if cb_img_cropped.ndim > 2 else axs[1, 1].imshow(cb_img_cropped, cmap='gray')
axs[1, 1].set_title("Cubert - Cropped")
axs[1, 1].axis("off")

plt.tight_layout()
plt.show()
