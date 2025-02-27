import numpy as np
import matplotlib.pyplot as plt
import tifffile as tiff

# ---------------------------
# Load Hyperspectral Image (First Band)
# ---------------------------
file_path = r"C:\Users\menon\Documents\Camera_Operation\generation_folder\spectral\notape\notape_cropped\generated_cropped\red_gen.tif"

def load_first_band(file_path):
    """Loads a hyperspectral image and extracts the first band."""
    img = tiff.imread(file_path)
    return img[0]  # Extract first band

# Load and normalize image
hyperspectral_image = load_first_band(file_path)
hyperspectral_image = (hyperspectral_image - np.min(hyperspectral_image)) / (np.max(hyperspectral_image) - np.min(hyperspectral_image))

# ---------------------------
# Create Stacked Hyperspectral Effect (Reversed Order)
# ---------------------------
fig, ax = plt.subplots(figsize=(6, 6))

num_layers = 5  # More layers for smoother stacking
shift_x = 4  # Slightly more separation
shift_y = 4
alpha_decay = 0.6  # More transparency in the back

# Define colormaps
colormap_spectral = plt.get_cmap("viridis")  # Stronger color transitions
colormap_top = plt.get_cmap("viridis")  # Viridis for the top image

# ---- Reverse Plot Order for Back-to-Front Stacking ----
for i in range(num_layers, 0, -1):  # Start from furthest back layer
    alpha = max(0.2, 1 - (i / num_layers) * alpha_decay)

    # Apply color tint with stronger effect
    color_tint = colormap_spectral(i / num_layers)  # Reverse order
    colorized_image = np.dstack((hyperspectral_image * color_tint[0] * 1.5,  
                                 hyperspectral_image * color_tint[1] * 1.5,  
                                 hyperspectral_image * color_tint[2] * 1.5))  
    colorized_image = np.clip(colorized_image, 0, 1)  # Ensure valid RGB range

    ax.imshow(colorized_image, extent=[-i * shift_x, -i * shift_x + hyperspectral_image.shape[1],
                                       -i * shift_y, -i * shift_y + hyperspectral_image.shape[0]],
              alpha=alpha)

# ---- Last Step: Place the Viridis Image on Top ----
colorized_image = colormap_top(hyperspectral_image)[:, :, :3]  # Convert grayscale to RGB
ax.imshow(colorized_image, extent=[0, hyperspectral_image.shape[1],
                                   0, hyperspectral_image.shape[0]],
          alpha=1)  # Ensure fully visible

# ---------------------------
# Formatting the Display
# ---------------------------
ax.set_xlim(-num_layers * shift_x, hyperspectral_image.shape[1])
ax.set_ylim(-num_layers * shift_y, hyperspectral_image.shape[0])
ax.set_xticks([])
ax.set_yticks([])
ax.set_frame_on(False)

# Save the visualization
plt.savefig("hyperspectral_stack_enhanced_red.svg", format="svg", dpi=300)
plt.show()
