import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import tifffile as tiff

class SingleHSIVisualizer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.hsi_image = tiff.imread(image_path)  # Load the image (106, 120, 120)
        print(self.hsi_image.shape)
        self.wavelengths = np.linspace(450, 850, self.hsi_image.shape[0])  # 450-850 nm, 4 nm steps

        # Initialize plot
        self.current_band = 0  # Start at the first band
        self.selected_points = []
        self.colors = ['red', 'blue', 'green', 'purple', 'orange']
        self.color_index = 0

        self.setup_plot()

    def setup_plot(self):
        # Create figure and axes
        self.fig, self.ax = plt.subplots(1, 2, figsize=(12, 6))
        plt.subplots_adjust(bottom=0.2)

        # Band display
        self.ax[0].imshow(self.hsi_image[self.current_band], cmap='viridis')
        self.ax[0].set_title(f"Band: {self.wavelengths[self.current_band]:.0f} nm")
        self.ax[0].axis('off')

        # Spectrum plot
        self.ax[1].set_title("Pixel Spectrum")
        self.ax[1].set_xlabel("Wavelength (nm)")
        self.ax[1].set_ylabel("Intensity")

        # Slider for band selection
        ax_slider = plt.axes([0.25, 0.05, 0.5, 0.03])
        self.slider = Slider(ax_slider, "Band", 0, self.hsi_image.shape[0] - 1, valinit=0, valstep=1)
        self.slider.on_changed(self.update_band)

        # Connect click event
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)

        plt.show()

    def update_band(self, val):
        self.current_band = int(self.slider.val)
        self.ax[0].imshow(self.hsi_image[self.current_band], cmap='viridis')
        self.ax[0].set_title(f"Band: {self.wavelengths[self.current_band]:.0f} nm")
        self.fig.canvas.draw_idle()

    def on_click(self, event):
        if event.inaxes == self.ax[0]:  # Ensure click is on the image
            x, y = int(event.xdata), int(event.ydata)
            color = self.colors[self.color_index % len(self.colors)]
            self.color_index += 1

            # Mark the selected point
            self.ax[0].plot(x, y, "o", color=color, markersize=8)

            # Extract and plot the spectrum
            spectrum = self.hsi_image[:, y, x]
                    # Calculate the peak contrast value
            peak_index = np.argmax(spectrum)
            peak_contrast = self.wavelengths[peak_index]
            max_val = np.max(spectrum)  # Find the maximum value of the spectrum
            self.ax[1].plot(self.wavelengths, spectrum, color=color, 
                            label=f"Max: {max_val:.2f} @ {peak_contrast:.1f}nm")
            self.ax[1].legend()
            self.fig.canvas.draw_idle()

# Usage
image_path = r"C:\Users\menon\Documents\Camera_Operation\generation_folder\spectral_bifringence\45_white_gen.tif"
SingleHSIVisualizer(image_path)
