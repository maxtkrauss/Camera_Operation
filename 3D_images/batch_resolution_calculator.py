import numpy as np
import tifffile as tiff
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import Button
import matplotlib as mpl
import os
import re

# Define directory containing images
directory = r"C:\Users\menon\Documents\Camera_Operation\images\bifringence_1-22\green"

# Define list of hyperspectral images to process
file_paths = [
    os.path.join(directory, file) for file in sorted(os.listdir(directory))
    if file.endswith(".tif")
]

# Extract RGB colors from filenames
def extract_rgb_from_filename(filename):
    """Extracts RGB values from filenames formatted as (R,G,B) or (R,G,B)-(R,G,B)_cubert.tif."""
    matches = re.findall(r"\((\d+),(\d+),(\d+)\)", filename)
    return [tuple(map(int, match)) for match in matches] if matches else filename

# Load multiple hyperspectral images
def load_hyperspectral_images(file_paths):
    images = []
    color_labels = []
    for file_path in file_paths:
        try:
            print("Normalized")
            image = tiff.imread(file_path).astype(np.float32)
            image -= image.min()
            image /= image.max()
            images.append(image)

            # Extract RGB colors from filename
            color_labels.append(extract_rgb_from_filename(os.path.basename(file_path)))

        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    return images, color_labels

# Compute contrast for a given cross-section
def compute_contrast(cross_section):
    max_val = np.max(cross_section)
    min_val = np.min(cross_section)
    return (max_val - min_val) / (max_val + min_val)

def main():
    # Load all hyperspectral images and their respective RGB labels
    hyperspectral_images, color_labels = load_hyperspectral_images(file_paths)
    if not hyperspectral_images:
        print("No images loaded.")
        return

    first_image = hyperspectral_images[-1]
    total_channels, height, width = first_image.shape

    # Define spectral range
    start_wavelength = 450
    end_wavelength = 706
    selected_bands = 64  # Using 64 bands from 450 nm to 706 nm
    wavelengths = np.linspace(start_wavelength, end_wavelength, selected_bands)

    # Set up figure for image and line selection
    fig, ax_image = plt.subplots(figsize=(6, 6))
    img_display = ax_image.imshow(first_image[0, :, :], cmap='viridis', norm=mpl.colors.Normalize(vmin=0, vmax=1))
    ax_image.set_title("Select Line for Contrast Calculation")
    ax_image.set_xlabel("X (pixels)")
    ax_image.set_ylabel("Y (pixels)")

    line_coords = []
    lines = []

    def clear_selection(event):
        """Clear all drawn lines and reset selections."""
        nonlocal line_coords, lines
        for line in lines:
            line.remove()
        lines.clear()
        line_coords = []
        fig.canvas.draw()

    def on_click(event):
        """Handles mouse clicks to select a line for contrast calculation."""
        if event.inaxes == ax_image:
            x, y = int(event.xdata), int(event.ydata)
            if len(line_coords) == 0:
                line_coords.append((x, y))
            elif len(line_coords) == 1:
                x1, y1 = line_coords[0]
                if abs(x - x1) > abs(y - y1):
                    y = y1
                else:
                    x = x1
                line_coords.append((x, y))

                # Draw the selected line
                line = Line2D([x1, x], [y1, y], color='red', alpha=0.8, linewidth=2)
                ax_image.add_line(line)
                lines.append(line)
                fig.canvas.draw()

                # Process the line selection
                process_line()

    def process_line():
        """Processes the selected line and computes contrast over wavelength for all images."""
        if len(line_coords) < 2:
            return

        x1, y1 = line_coords[0]
        x2, y2 = line_coords[1]

        length = int(np.hypot(x2 - x1, y2 - y1))
        x_vals = np.linspace(x1, x2, length).astype(int)
        y_vals = np.linspace(y1, y2, length).astype(int)

        offsets = [-2, -1, 0, 1, 2]  # Averaging over five parallel lines

        for img_idx, (image, rgbs) in enumerate(zip(hyperspectral_images, color_labels)):
            contrasts = []

            for channel in range(selected_bands):
                band = channel
                combined_profile = np.zeros(length)

                for o in offsets:
                    if abs(x2 - x1) > abs(y2 - y1):
                        y_vals_offset = np.clip(y_vals + o, 0, height - 1)
                        line_profile = image[band, y_vals_offset, x_vals]
                    else:
                        x_vals_offset = np.clip(x_vals + o, 0, width - 1)
                        line_profile = image[band, y_vals, x_vals_offset]

                    combined_profile += line_profile

                combined_profile /= len(offsets)
                contrast = compute_contrast(combined_profile)
                contrasts.append(contrast)

            # Format and print results neatly
            print("\n" + "=" * 60)
            print(f"Contrast Data for Image: {rgbs}")
            print("=" * 60)
            print(f"{'Contrast':<20}")
            print("-" * 60)
            for wl, contrast in zip(wavelengths, contrasts):
                print(f"{contrast:<20.4f}")
            print("=" * 60)
            print(f"{np.average(contrasts):.2f}")
            

    # Add a "Clear" button
    clear_ax = plt.axes([0.8, 0.02, 0.1, 0.05])
    clear_button = Button(clear_ax, "Clear")
    clear_button.on_clicked(clear_selection)

    fig.canvas.mpl_connect('button_press_event', on_click)
    plt.show()

if __name__ == "__main__":
    main()
