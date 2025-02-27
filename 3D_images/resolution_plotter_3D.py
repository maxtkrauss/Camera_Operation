import numpy as np
import tifffile as tiff
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import TextBox, Button
import matplotlib as mpl

# File path to your hyperspectral image
file_path = r"C:\Users\menon\Documents\Camera_Operation\images\spectro\GEN_images\tl_gen_3.tif"

# Load the hyperspectral image
def load_hyperspectral_image(file_path):
    try:
        image = tiff.imread(file_path).astype(np.float32)
        # Normalize the image to [0, 1] range
        image -= image.min()
        image /= image.max()
        return image
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

# Compute the contrast for a line cross-section
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

    # Get dimensions of the image (Channels, Height, Width)
    total_channels, height, width = hyperspectral_image.shape

    # Default cutoff channels
    cutoff_channels = total_channels

    # Set up the figure and axis for drawing
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    plt.subplots_adjust(hspace=0.4, wspace=0.3)  # Adjust spacing between plots

    ax_image = axs[0, 0]
    ax_cross_section = axs[0, 1]
    ax_contrast = axs[1, 0]
    ax_all_cross_sections = axs[1, 1]

    # Display the first channel initially
    img_display = ax_image.imshow(hyperspectral_image[0, :, :], cmap='gray', norm=mpl.colors.Normalize(vmin=0, vmax=1))
    ax_image.set_title("First Channel | Wavelength: 450.00 nm")
    ax_image.set_xlabel("X (pixels)")
    ax_image.set_ylabel("Y (pixels)")

    # Add a text box for cutoff channels
    ax_textbox = plt.axes([0.1, 0.01, 0.3, 0.05])  # Place textbox below the plots
    textbox = TextBox(ax_textbox, 'Cutoff Bands', initial=str(total_channels))

    # Add a clear button
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
                # Force a straight line by averaging x or y coordinates
                if abs(x - x1) > abs(y - y1):
                    y = y1  # Horizontal line
                else:
                    x = x1  # Vertical line
                line_coords.append((x, y))

                # Draw the main line and parallel lines
                offsets = [-2, -1, 0, 1, 2]  # Parallel lines offsets
                for o in offsets:
                    if abs(x - x1) > abs(y - y1):  # Horizontal orientation
                        y_offset = y + o
                        line = Line2D([x1, x], [y_offset, y_offset], color='red', alpha=0.7)
                    else:  # Vertical orientation
                        x_offset = x + o
                        line = Line2D([x_offset, x_offset], [y1, y], color='red', alpha=0.7)
                    ax_image.add_line(line)

                fig.canvas.draw()
                process_line()

    fig.canvas.mpl_connect('button_press_event', on_click)

    # Clear all lines and reset
    def clear(event):
        nonlocal line_coords
        line_coords = []
        for line in list(ax_image.lines):
            line.remove()
        ax_cross_section.clear()
        ax_contrast.clear()
        ax_all_cross_sections.clear()
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

    # Process the line: Compute average cross-section and contrast
    def process_line():
        if len(line_coords) < 2:
            return

        x1, y1 = line_coords[0]
        x2, y2 = line_coords[1]

        length = int(np.hypot(x2 - x1, y2 - y1))
        x_vals = np.linspace(x1, x2, length).astype(int)
        y_vals = np.linspace(y1, y2, length).astype(int)

        # Generate parallel lines
        offset = 2  # Distance between parallel lines
        offsets = [-2 * offset, -offset, 0, offset, 2 * offset]

        contrasts = []
        ax_cross_section.clear()
        ax_contrast.clear()
        ax_all_cross_sections.clear()

        avg_line_profile = np.zeros(length)
        for channel in range(cutoff_channels):
            combined_profile = np.zeros(length)
            for o in offsets:
                # Calculate parallel lines
                if abs(x2 - x1) > abs(y2 - y1):  # Horizontal orientation
                    y_vals_offset = np.clip(y_vals + o, 0, height - 1)
                    line_profile = hyperspectral_image[channel, y_vals_offset, x_vals]
                else:  # Vertical orientation
                    x_vals_offset = np.clip(x_vals + o, 0, width - 1)
                    line_profile = hyperspectral_image[channel, y_vals, x_vals_offset]
                combined_profile += line_profile
                ax_all_cross_sections.plot(line_profile, alpha=0.3)

            combined_profile /= len(offsets)
            avg_line_profile += combined_profile
            contrasts.append(compute_contrast(combined_profile))

        avg_line_profile /= cutoff_channels

        # Plot the averaged line cross-section
        ax_cross_section.plot(avg_line_profile, label="Average Cross-Section", color="blue")
        ax_cross_section.set_title("Average Line Cross-Section")
        ax_cross_section.set_xlabel("Line Profile Index")
        ax_cross_section.set_ylabel("Normalized Intensity")
        ax_cross_section.legend()

        # Compute max, min, and average contrast
        max_contrast = max(contrasts)
        min_contrast = min(contrasts)
        avg_contrast = sum(contrasts) / len(contrasts)

        # Define the wavelength range and calculate the corresponding wavelengths for each channel
        wavelengths = np.linspace(450, 850-(450-(total_channels*4)), total_channels)  # Linearly spaced wavelengths from 450 nm to 730 nm

        # Calculate the peak contrast value
        peak_contrast_index = np.argmax(contrasts)
        peak_contrast = wavelengths[peak_contrast_index]

        # Plot contrast across all selected channels with wavelengths as x-axis
        ax_contrast.plot(wavelengths[:cutoff_channels], contrasts, label='Contrast per Wavelength', color='blue')
        ax_contrast.legend(
            [f'Max: {max_contrast:.3f}, Min: {min_contrast:.3f}, Avg: {avg_contrast:f}'],
            loc='lower left')

        # Set the title with the peak contrast value
        ax_contrast.set_title(f"Contrast Across Wavelengths (Peak Contrast {max(contrasts):.2f} @ {peak_contrast:.2f})")
        ax_contrast.set_xlabel("Wavelength (nm)")
        ax_contrast.set_ylabel("Contrast")


        # Add titles and labels to all cross-sections plot
        ax_all_cross_sections.set_title("Line Cross-Sections for Selected Channels")
        ax_all_cross_sections.set_xlabel("Line Profile Index")
        ax_all_cross_sections.set_ylabel("Normalized Intensity")

        fig.canvas.draw_idle()

    # Show the plot
    plt.show()

if __name__ == "__main__":
    main()
