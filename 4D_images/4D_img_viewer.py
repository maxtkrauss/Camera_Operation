import numpy as np
import tifffile as tiff
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import matplotlib as mpl

# Constants
FILE_PATH = r"Z:\Documents\NASA_HSI\hyperspectral_pix2pix_W-NET\hyperspectral_pix2pix\resolution_tests\bifringence_test\4D_generated_cubert.tif"
POLARIZATION_LABELS = ["0°", "45°", "90°", "Raw"]
WAVELENGTH_START = 450  # in nm
WAVELENGTH_END = 706  # in nm
NUM_BANDS = 64
BAND_WIDTH = (WAVELENGTH_END - WAVELENGTH_START) / (NUM_BANDS - 1)

# Load the combined HSI
def load_combined_hsi(file_path):
    try:
        image = tiff.imread(file_path).astype(np.float32)
        image -= image.min()
        image /= image.max()
        return image
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def main():
    # Load the image
    combined_hsi = load_combined_hsi(FILE_PATH)

    if combined_hsi is None:
        return

    # Get dimensions (Polarization, Channels, Height, Width)
    pols, channels, height, width = combined_hsi.shape

    # Set up the figure and axes
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.3)  # Make room for sliders

    # Display the first polarization and wavelength initially
    img_display = ax.imshow(combined_hsi[0, 0, :, :], cmap='gray', norm=mpl.colors.Normalize(vmin=0, vmax=1))
    ax.set_title(f"Polarization: {POLARIZATION_LABELS[0]} | Wavelength: {WAVELENGTH_START:.2f} nm")

    # Create sliders
    ax_slider_pol = plt.axes([0.2, 0.15, 0.65, 0.03])
    ax_slider_wl = plt.axes([0.2, 0.1, 0.65, 0.03])

    slider_pol = Slider(ax_slider_pol, 'Polarization', 0, pols - 1, valinit=0, valstep=1)
    slider_wl = Slider(ax_slider_wl, 'Wavelength', 0, channels - 1, valinit=0, valstep=1)

    # Update function for the sliders
    def update(val):
        pol_idx = int(slider_pol.val)
        wl_idx = int(slider_wl.val)
        wavelength = WAVELENGTH_START + wl_idx * BAND_WIDTH

        img_display.set_data(combined_hsi[pol_idx, wl_idx, :, :])
        ax.set_title(f"Polarization: {POLARIZATION_LABELS[pol_idx]} | Wavelength: {wavelength:.2f} nm")
        fig.canvas.draw_idle()

    slider_pol.on_changed(update)
    slider_wl.on_changed(update)

    # Show the plot
    plt.show()

if __name__ == "__main__":
    main()
