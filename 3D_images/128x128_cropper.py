import numpy as np
import tifffile as tiff
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import matplotlib as mpl

#file_path = r"images/example_images/cubert/res_cubert_raw.tif"
file_path = r"C:\Users\menon\Documents\Camera_Operation\images\bifringence\cubert\raw_cubert.tif"
file_path = r"C:\Users\menon\Documents\Camera_Operation\chunk_171_109.tif"
file_path = r"C:\Users\menon\Documents\Camera_Operation\images\spectro\ground_truth\cubert\chunk_171_109_image_1_cubert.tif"
file_path = r"C:\Users\menon\Documents\Camera_Operation\images\spectro_pol\128\cubert\chunk_171_109_raw_cubert.tif"
file_path = r"C:\Users\menon\Documents\Camera_Operation\images\spectro_pol\0\thorlabs\chunk_1392_604_raw_thorlabs.tif"
file_path = r"C:\Users\menon\Documents\Camera_Operation\images\spectro\run_2\cubert_cropped\chunk_171_111_(255,255,0)_cubert.tif"
file_path = r"C:\Users\menon\Documents\Camera_Operation\images\spectro\run_2\batch_res\(255,255,255)_cubert.tif"
# Constants
WAVELENGTH_START = 450  # in nm
WAVELENGTH_END = 850  # in nm
NUM_BANDS = 106
BAND_WIDTH = (WAVELENGTH_END - WAVELENGTH_START) / (NUM_BANDS - 1)
CHUNK_SIZE = 120

# Load the hyperspectral image
def load_hyperspectral_image(file_path):
    try:
        image = tiff.imread(file_path).astype(np.float32)
        print(image.shape)
        image -= image.min()
        image /= image.max()
        return image
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

# Save the selected chunk
def save_chunk(image, center_x, center_y, save_path="chunk.tif"):
    z, h, w = image.shape
    half_size = CHUNK_SIZE // 2
    start_x = max(center_x - half_size, 0)
    end_x = min(center_x + half_size, w)
    start_y = max(center_y - half_size, 0)
    end_y = min(center_y + half_size, h)

    # Ensure the chunk is in the spatial dimensions
    chunk = image[:, start_y:end_y, start_x:end_x]
    if chunk.shape[1] != CHUNK_SIZE or chunk.shape[2] != CHUNK_SIZE:
        print("Error: Selected chunk is not 128x128 in spatial dimensions.")
        return

    # Save the chunk as a new TIFF file
    tiff.imwrite(save_path, chunk)
    print(f"Chunk saved to {save_path}")

def main():
    # Load the image
    hyperspectral_image = load_hyperspectral_image(file_path)
    
    if hyperspectral_image is None:
        return

    # Get dimensions of the image (Channels, Height, Width)
    channels, height, width = hyperspectral_image.shape

    # Set up the figure and axis
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)  # Make room for the slider

    # Display the first channel initially
    img_display = ax.imshow(hyperspectral_image[0, :, :], cmap='gray', norm=mpl.colors.Normalize(vmin=0, vmax=1))
    wavelength = WAVELENGTH_START
    ax.set_title(f"Cubert HSI | Wavelength: {wavelength:.2f} nm")

    # Add a slider for scrolling through channels
    ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03])
    slider = Slider(ax_slider, 'Channel', 0, channels - 1, valinit=0, valstep=1)

    # Update function for the slider
    def update(val):
        channel = int(slider.val)
        img_display.set_data(hyperspectral_image[channel, :, :])
        wavelength = WAVELENGTH_START + channel * BAND_WIDTH
        ax.set_title(f"Cubert HSI | Wavelength: {wavelength:.2f} nm")
        fig.canvas.draw_idle()

    slider.on_changed(update)

    # Add click functionality to save chunks
    def on_click(event):
        if event.inaxes == ax:
            center_x = int(event.xdata)
            center_y = int(event.ydata)
            print(f"Clicked at (x, y): ({center_x}, {center_y})")
            save_chunk(hyperspectral_image, center_x, center_y, save_path=f"chunk_{center_x}_{center_y}.tif")

    fig.canvas.mpl_connect('button_press_event', on_click)

    # Show the plot
    plt.show()

if __name__ == "__main__":
    main()
