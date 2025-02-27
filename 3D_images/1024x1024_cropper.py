import numpy as np
import tifffile as tiff
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import matplotlib as mpl

file_path = r"images//example_images/thorlabs/res_tl_raw.tif"
file_path = r"C:\Users\menon\Documents\Camera_Operation\images\bifringence\thorlabs\raw_thorlabs.tif"
file_path = r"Z:\Documents\NASA_HSI\raw_0_thorlabs.tif"
file_path = r"C:\Users\menon\Documents\Camera_Operation\images\spectro_pol\250\thorlabs\raw_thorlabs.tif"
file_path = r"C:\Users\menon\Documents\Camera_Operation\images\spectro\ground_truth\thorlabs\chunk_1392_604_image_1_thorlabs.tif"
file_path = r"C:\Users\menon\Documents\Camera_Operation\generation_folder\tape\thorlabs\crop_red_tl.tif"



# Constants
CROP_SIZE = 660

# Load the multichannel image
def load_multichannel_image(file_path):
    try:
        image = tiff.imread(file_path).astype(np.float32)
        # Normalize the image to [0, 1] range
        image -= image.min()
        image /= image.max()
        return image
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

# Save the cropped area
def save_cropped_area(image, center_x, center_y, save_path="cropped_area.tif"):
    channels, height, width = image.shape
    half_size = CROP_SIZE // 2
    start_x = max(center_x - half_size, 0)
    end_x = min(center_x + half_size, width)
    start_y = max(center_y - half_size, 0)
    end_y = min(center_y + half_size, height)

    # Ensure the crop is 1024x1024 in spatial dimensions
    cropped = image[:, start_y:end_y, start_x:end_x]
    if cropped.shape[1] != CROP_SIZE or cropped.shape[2] != CROP_SIZE:
        print("Error: Cropped area is not 1024x1024 in spatial dimensions.")
        return

    # Save the cropped area as a new TIFF file
    tiff.imwrite(save_path, cropped)
    print(f"Cropped area saved to {save_path}")

def main():
    # Load the image
    multichannel_image = load_multichannel_image(file_path)
    
    if multichannel_image is None:
        return

    # Get dimensions of the image (Channels, Height, Width)
    channels, height, width = multichannel_image.shape

    # Set up the figure and axis
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)  # Make room for the slider

    # Display the first channel initially
    img_display = ax.imshow(multichannel_image[1, :, :], cmap='gray', norm=mpl.colors.Normalize(vmin=0, vmax=1))
    ax.set_title(f"Diffractogram")

    # Add a slider for scrolling through channels
    ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03])
    slider = Slider(ax_slider, 'Channel', 0, channels - 1, valinit=0, valstep=1)

    # Update function for the slider
    def update(val):
        channel = int(slider.val)
        img_display.set_data(multichannel_image[channel, :, :])
        ax.set_title(f"Channel: {channel}")
        fig.canvas.draw_idle()

    slider.on_changed(update)

    # Add click functionality to crop the image
    def on_click(event):
        if event.inaxes == ax:
            center_x = int(event.xdata)
            center_y = int(event.ydata)
            print(f"Clicked at (x, y): ({center_x}, {center_y})")
            save_cropped_area(multichannel_image, center_x, center_y, save_path=f"cropped_{center_x}_{center_y}.tif")

    fig.canvas.mpl_connect('button_press_event', on_click)

    # Show the plot
    plt.show()

if __name__ == "__main__":
    main()
