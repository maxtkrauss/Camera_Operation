import numpy as np
import tifffile as tiff
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import TextBox, Button
import matplotlib as mpl

# File path to your hyperspectral image
file_path = r"Z:\Documents\NASA_HSI\hyperspectral_pix2pix_W-NET\hyperspectral_pix2pix\resolution_tests\bifringence_test\4D_generated_cubert.tif"

# Polarization labels
POLARIZATION_LABELS = ["0°", "45°", "90°", "Raw"]

# Load the hyperspectral image
def load_hyperspectral_image(file_path):
    try:
        image = tiff.imread(file_path).astype(np.float32)
        image -= image.min()
        image /= image.max()
        return image
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

# Compute contrast for a line cross-section
def compute_contrast(cross_section):
    max_val = np.max(cross_section)
    min_val = np.min(cross_section)
    contrast = (max_val - min_val) / (max_val + min_val)
    return contrast

def main():
    # Load the hyperspectral image
    hyperspectral_image = load_hyperspectral_image(file_path)
    if hyperspectral_image is None:
        return

    # Get dimensions (Polarization, Channels, Height, Width)
    num_polarizations, total_channels, height, width = hyperspectral_image.shape
    cutoff_channels = total_channels  # Default cutoff

    # Set up the main figure for image display
    fig, ax_image = plt.subplots(figsize=(6, 6))

    # Display the first polarization's first wavelength initially
    img_display = ax_image.imshow(hyperspectral_image[0, 0, :, :], cmap='gray', norm=mpl.colors.Normalize(vmin=0, vmax=1))
    ax_image.set_title("First Channel | Wavelength: 450.00 nm | Polarization: 0°")
    ax_image.set_xlabel("X (pixels)")
    ax_image.set_ylabel("Y (pixels)")

    # Add text box for cutoff channels
    ax_textbox = plt.axes([0.1, 0.01, 0.3, 0.05])
    textbox = TextBox(ax_textbox, 'Cutoff Bands', initial=str(total_channels))

    # Add clear button
    ax_clear_button = plt.axes([0.5, 0.01, 0.1, 0.05])
    clear_button = Button(ax_clear_button, 'Clear')

    # List to store the line coordinates
    line_coords = []

    # Handle mouse clicks for drawing a line
    def on_click(event):
        if event.inaxes == ax_image:
            x, y = int(event.xdata), int(event.ydata)
            if len(line_coords) == 0:
                line_coords.append((x, y))
            elif len(line_coords) == 1:
                x1, y1 = line_coords[0]
                if abs(x - x1) > abs(y - y1):
                    y = y1  # Horizontal line
                else:
                    x = x1  # Vertical line
                line_coords.append((x, y))

                offsets = [-2, -1, 0, 1, 2]
                for o in offsets:
                    if abs(x - x1) > abs(y - y1):
                        y_offset = y + o
                        line = Line2D([x1, x], [y_offset, y_offset], color='red', alpha=0.7)
                    else:
                        x_offset = x + o
                        line = Line2D([x_offset, x_offset], [y1, y], color='red', alpha=0.7)
                    ax_image.add_line(line)

                fig.canvas.draw()
                process_line()

    fig.canvas.mpl_connect('button_press_event', on_click)

    # Clear function
    def clear(event):
        nonlocal line_coords
        line_coords = []
        for line in list(ax_image.lines):
            line.remove()
        fig.canvas.draw()

    clear_button.on_clicked(clear)

    # Update the cutoff channels when the text box changes
    def update_cutoff(text):
        nonlocal cutoff_channels
        try:
            cutoff_channels = min(int(text), total_channels)
            print(f"Cutoff channels updated to: {cutoff_channels}")
            process_line()
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    textbox.on_submit(update_cutoff)

    # Process the line
    def process_line():
        if len(line_coords) < 2:
            return

        x1, y1 = line_coords[0]
        x2, y2 = line_coords[1]
        length = int(np.hypot(x2 - x1, y2 - y1))
        x_vals = np.linspace(x1, x2, length).astype(int)
        y_vals = np.linspace(y1, y2, length).astype(int)
        offsets = [-4, -2, 0, 2, 4]

        fig_contrast, axs_contrast = plt.subplots(2, 2, figsize=(12, 10))
        axs_contrast = axs_contrast.flatten()

        all_polarization_avg_contrasts = []
        first_polarization_contrasts = []

        for pol in range(num_polarizations):
            contrasts = []

            for channel in range(cutoff_channels):
                combined_profile = np.zeros(length)
                for o in offsets:
                    if abs(x2 - x1) > abs(y2 - y1):
                        y_vals_offset = np.clip(y_vals + o, 0, height - 1)
                        line_profile = hyperspectral_image[pol, channel, y_vals_offset, x_vals]
                    else:
                        x_vals_offset = np.clip(x_vals + o, 0, width - 1)
                        line_profile = hyperspectral_image[pol, channel, y_vals, x_vals_offset]
                    combined_profile += line_profile

                combined_profile /= len(offsets)
                contrast_value = compute_contrast(combined_profile)
                contrasts.append(contrast_value)

            avg_contrast = np.mean(contrasts)
            all_polarization_avg_contrasts.append(avg_contrast)

            wavelengths = np.linspace(450, 850 - (450 - (total_channels * 4)), total_channels)

            axs_contrast[pol].plot(wavelengths[:cutoff_channels], contrasts, label=f'Contrast per Wavelength ({POLARIZATION_LABELS[pol]})', color='blue')
            axs_contrast[pol].set_title(f"Polarization: {POLARIZATION_LABELS[pol]} (Avg: {avg_contrast:.4f})")
            axs_contrast[pol].set_xlabel("Wavelength (nm)")
            axs_contrast[pol].set_ylabel("Contrast")

            if pol == 0:
                first_polarization_contrasts = contrasts  # Store first polarization data for main plot

        total_avg_contrast = np.mean(all_polarization_avg_contrasts)
        fig_contrast.suptitle(f"Total Average Contrast: {total_avg_contrast:.4f}", fontsize=14)

        fig_contrast.tight_layout()
        plt.show()

        # Display the first polarization contrast in the main figure
        fig_main_contrast, ax_main_contrast = plt.subplots(figsize=(6, 4))
        ax_main_contrast.plot(wavelengths[:cutoff_channels], first_polarization_contrasts, label=f'0° Contrast', color='blue')
        ax_main_contrast.set_title(f"0° Contrast Over Wavelength")
        ax_main_contrast.set_xlabel("Wavelength (nm)")
        ax_main_contrast.set_ylabel("Contrast")
        ax_main_contrast.legend()
        plt.show()

    plt.show()

if __name__ == "__main__":
    main()
