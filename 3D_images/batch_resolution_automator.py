import numpy as np
import tifffile as tiff
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import Button, TextBox
import matplotlib as mpl
import os
import pandas as pd

# Define directory containing images
directory = r"C:\Users\menon\Documents\Camera_Operation\generation_folder\bifringence_white\cropped"

# Define list of hyperspectral images to process
file_paths = [
    os.path.join(directory, file) for file in sorted(os.listdir(directory))
    if file.endswith(".tif")
]

# Extract filenames (without directory path)
def extract_filename(file_path):
    return os.path.basename(file_path)

# Load multiple hyperspectral images
def load_hyperspectral_images(file_paths):
    images = []
    filenames = []
    for file_path in file_paths:
        try:
            image = tiff.imread(file_path).astype(np.float32)
            image -= image.min()
            image /= image.max()
            images.append(image)
            filenames.append(extract_filename(file_path))
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    return images, filenames

# Compute contrast for a given cross-section
def compute_contrast(cross_section):
    max_val = np.max(cross_section)
    min_val = np.min(cross_section)
    return (max_val - min_val) / (max_val + min_val)

def process_all_images(hyperspectral_images, filenames):
    """Handles the user interaction for selecting a line once and applying it to all images."""
    
    # Define spectral range
    start_wavelength = 450
    end_wavelength = 706
    selected_bands = 64  # Using 64 bands from 450 nm to 706 nm
    wavelengths = np.linspace(start_wavelength, end_wavelength, selected_bands)

    # Dictionary to hold contrast data for each image
    contrast_data = {fname: {"Wavelength": wavelengths} for fname in filenames}

    # Use the first image as the reference for line selection
    reference_image = hyperspectral_images[-1]
    total_channels, height, width = reference_image.shape

    # Display the reference image
    fig, ax_image = plt.subplots(figsize=(6, 6))
    img_display = ax_image.imshow(reference_image[0, :, :], cmap='viridis', norm=mpl.colors.Normalize(vmin=0, vmax=1))
    ax_image.set_title("Draw a Line (Applies to All Images)")
    ax_image.set_xlabel("X (pixels)")
    ax_image.set_ylabel("Y (pixels)")

    # User input for resolution group number
    resolution_group = [None]

    def on_text_submit(text):
        """Stores the entered resolution group number."""
        resolution_group[0] = text.strip()

    text_ax = plt.axes([0.1, 0.02, 0.3, 0.05])
    text_box = TextBox(text_ax, "Resolution Group:", initial="Group 1")
    text_box.on_submit(on_text_submit)

    # Handling line selection
    line_coords = []
    lines = []
    resolution_group = [1]  # Placeholder for resolution group input

    def clear_selection(event):
        """Clears drawn lines."""
        nonlocal line_coords, lines
        for line in lines:
            line.remove()
        lines.clear()
        line_coords = []
        fig.canvas.draw()

        # User input for number of offsets
    offset_ax = plt.axes([0.5, 0.02, 0.3, 0.05])
    offset_box = TextBox(offset_ax, "Offsets:", initial="5")

    # Default number of offsets
    num_offsets = [5]  # Store in a mutable list

    def on_offset_submit(text):
        """Updates the number of offsets dynamically."""
        try:
            value = int(text.strip())
            if value >= 1:
                num_offsets[0] = value
            else:
                print("Enter a valid positive integer for offsets.")
        except ValueError:
            print("Invalid input. Enter an integer.")

    offset_box.on_submit(on_offset_submit)

    def on_click(event):
        """Handles mouse clicks to select a line for contrast calculation."""
        if resolution_group[0] is None:
            print("Please enter a resolution group number before drawing.")
            return

        if event.inaxes == ax_image:
            x, y = int(event.xdata), int(event.ydata)

            if len(line_coords) == 0:
                line_coords.append((x, y))
            elif len(line_coords) == 1:
                x1, y1 = line_coords[0]

                # Snap to either horizontal or vertical alignment
                if abs(x - x1) > abs(y - y1):
                    y = y1  # Lock y for horizontal line
                else:
                    x = x1  # Lock x for vertical line
                line_coords.append((x, y))

                # Define offset values (parallel lines around the main one)
                offsets = list(range(-num_offsets[0]//2, num_offsets[0]//2 + 1))


                # Check line orientation
                is_horizontal = abs(x - x1) > abs(y - y1)

                for offset in offsets:
                    if is_horizontal:
                        # Offset in the Y-direction
                        x_start, y_start = x1, y1 + offset
                        x_end, y_end = x, y + offset
                    else:
                        # Offset in the X-direction
                        x_start, y_start = x1 + offset, y1
                        x_end, y_end = x + offset, y

                    # Draw the offset line
                    line = Line2D([x_start, x_end], [y_start, y_end], color='red', alpha=0.8, linewidth=2)
                    ax_image.add_line(line)
                    lines.append(line)

                # Refresh the plot
                fig.canvas.draw()

                # Process this line for all images (unchanged from your code)
                process_line_for_all_images(line_coords, resolution_group[0])

    def process_line_for_all_images(line_coords, group_name):
        """Processes the selected line and computes contrast over wavelength for all images."""
        if len(line_coords) < 2:
            return

        x1, y1 = line_coords[0]
        x2, y2 = line_coords[1]

        length = int(np.hypot(x2 - x1, y2 - y1))
        x_vals = np.linspace(x1, x2, length).astype(int)
        y_vals = np.linspace(y1, y2, length).astype(int)

        offsets = list(range(-num_offsets[0]//2, num_offsets[0]//2 + 1))

        print(f"\nResolution Group: {group_name}")
        print("-" * 52)
        print("Average Contrast for each Image:")

        for img, fname in zip(hyperspectral_images, filenames):
            contrasts = []

            for channel in range(selected_bands):
                band = channel
                combined_profile = np.zeros(length)

                for o in offsets:
                    if abs(x2 - x1) > abs(y2 - y1):
                        y_vals_offset = np.clip(y_vals + o, 0, height - 1)
                        line_profile = img[band, y_vals_offset, x_vals]
                    else:
                        x_vals_offset = np.clip(x_vals + o, 0, width - 1)
                        line_profile = img[band, y_vals, x_vals_offset]

                    combined_profile += line_profile

                combined_profile /= len(offsets)
                contrast = compute_contrast(combined_profile)
                contrasts.append(contrast)

            # Save contrast data into dictionary
            contrast_data[fname][group_name] = contrasts

            # Compute and print average contrast
            avg_contrast = np.mean(contrasts)
            print(f"{fname}:  {avg_contrast:.4f}")

        print("-" * 52)

    # Add a "Clear" button
    clear_ax = plt.axes([0.8, 0.02, 0.1, 0.05])
    clear_button = Button(clear_ax, "Clear")
    clear_button.on_clicked(clear_selection)

    fig.canvas.mpl_connect('button_press_event', on_click)
    plt.show()

    # Save each image's contrast data as a CSV file
    for fname in filenames:
        df = pd.DataFrame(contrast_data[fname])
        df.to_csv(f"{fname.replace('.tif', '.csv')}", index=False)
        print(f"Saved: {fname.replace('.tif', '.csv')}")

def main():
    hyperspectral_images, filenames = load_hyperspectral_images(file_paths)
    if not hyperspectral_images:
        print("No images loaded.")
        return
    process_all_images(hyperspectral_images, filenames)

if __name__ == "__main__":
    main()
