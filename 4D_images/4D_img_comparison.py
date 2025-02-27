import os
import numpy as np
import tifffile as tiff
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from skimage.metrics import structural_similarity as ssim

# File paths for the generated and ground truth 4D images
FILE_PATH_GEN = r"Z:\Documents\NASA_HSI\hyperspectral_pix2pix_W-NET\hyperspectral_pix2pix\resolution_tests\bifringence_test\4D_generated_cubert.tif"
FILE_PATH_GT = r"Z:\Documents\NASA_HSI\hyperspectral_pix2pix_W-NET\hyperspectral_pix2pix\resolution_tests\bifringence_test\4D_ground_truth_cubert.tif"

POLARIZATION_LABELS = ["0°", "45°", "90°", "Raw"]
WAVELENGTH_START = 450  # in nm
WAVELENGTH_END = 706  # in nm
NUM_BANDS = 64
BAND_WIDTH = (WAVELENGTH_END - WAVELENGTH_START) / (NUM_BANDS - 1)

# Load the 4D image
def load_combined_hsi(file_path, norm):
    try:
        image = tiff.imread(file_path).astype(np.float32)
        if norm:
            image -= image.min()
            image /= image.max()
        return image
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

# Crop generated image to 120x120
def crop_generated_image(image):
    _, _, height, width = image.shape
    crop_height, crop_width = 120, 120
    start_h = (height - crop_height) // 2
    start_w = (width - crop_width) // 2
    return image[:, :, start_h:start_h + crop_height, start_w:start_w + crop_width]

# Limit ground truth to the first 64 bands
def limit_ground_truth_bands(image):
    return image[:, :NUM_BANDS, :, :]

# Calculate metrics
def calculate_metrics(ground_truth, generated):
    data_range = ground_truth.max() - ground_truth.min()
    
    # SSIM
    ssim_3d = ssim(ground_truth, generated, data_range=data_range, multichannel=True)
    ssim_2d = ssim(ground_truth[0], generated[0], data_range=data_range)
    
    # MSE
    mse = np.mean((ground_truth - generated) ** 2)
    
    # MAE
    mae = np.mean(np.abs(ground_truth - generated))
    
    return ssim_3d, ssim_2d, mse, mae

# Plot spectra for a selected pixel
def plot_pixel_spectra(x, y, gen_hsi, gt_hsi):
    wavelengths = np.linspace(WAVELENGTH_START, WAVELENGTH_END, NUM_BANDS)

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    axes = axes.flatten()

    for pol_idx, ax in enumerate(axes):
        gen_spectrum = gen_hsi[pol_idx, :, y, x]
        gt_spectrum = gt_hsi[pol_idx, :, y, x]

        ax.plot(wavelengths, gt_spectrum, label='Ground Truth', linestyle='-', marker='o')
        ax.plot(wavelengths, gen_spectrum, label='Generated', linestyle='--', marker='x')

        ax.set_title(f"Polarization: {POLARIZATION_LABELS[pol_idx]}")
        ax.set_xlabel("Wavelength (nm)")
        ax.set_ylabel("Intensity")
        ax.legend()

    plt.tight_layout()
    plt.show()

# Main function
def main():
    # Load images
    gen_hsi = load_combined_hsi(FILE_PATH_GEN, False)
    gt_hsi = load_combined_hsi(FILE_PATH_GT, True)
    if gen_hsi is None or gt_hsi is None:
        return

    # Crop and prepare images
    gen_hsi = crop_generated_image(gen_hsi)  # Crop the generated image
    gt_hsi = limit_ground_truth_bands(gt_hsi)  # Limit ground truth bands

    # Ensure both images have the same dimensions for visualization
    assert gen_hsi.shape == gt_hsi.shape, "Generated and ground truth images have mismatched dimensions!"

    # Get dimensions (Polarization, Channels, Height, Width)
    pols, channels, height, width = gen_hsi.shape

    # Set up the figure and axes
    fig, (ax_gen, ax_gt) = plt.subplots(1, 2, figsize=(12, 6))
    plt.subplots_adjust(bottom=0.25)  # Make room for sliders

    # Display the first polarization and wavelength initially
    img_gen = ax_gen.imshow(gen_hsi[0, 0, :, :], cmap='gray', vmin=0, vmax=1)
    img_gt = ax_gt.imshow(gt_hsi[0, 0, :, :], cmap='gray', vmin=0, vmax=1)

    ax_gen.set_title("Generated Image")
    ax_gt.set_title("Ground Truth Image")

    # Create sliders
    ax_slider_pol = plt.axes([0.2, 0.1, 0.65, 0.03])
    ax_slider_wl = plt.axes([0.2, 0.05, 0.65, 0.03])

    slider_pol = Slider(ax_slider_pol, 'Polarization', 0, pols - 1, valinit=0, valstep=1)
    slider_wl = Slider(ax_slider_wl, 'Wavelength', 0, channels - 1, valinit=0, valstep=1)

    # Metric display
    metric_text = fig.text(0.5, 0.01, "", ha='center', fontsize=10)

    # Markers for clicked points
    gen_marker, = ax_gen.plot([], [], 'ro', markersize=5)
    gt_marker, = ax_gt.plot([], [], 'ro', markersize=5)

    # Update function for the sliders
    def update(val):
        pol_idx = int(slider_pol.val)
        wl_idx = int(slider_wl.val)
        wavelength = WAVELENGTH_START + wl_idx * BAND_WIDTH

        img_gen.set_data(gen_hsi[pol_idx, wl_idx, :, :])
        img_gt.set_data(gt_hsi[pol_idx, wl_idx, :, :])

        # Update titles
        ax_gen.set_title(f"Generated Image | Polarization: {POLARIZATION_LABELS[pol_idx]} | Wavelength: {wavelength:.2f} nm")
        ax_gt.set_title(f"Ground Truth Image | Polarization: {POLARIZATION_LABELS[pol_idx]} | Wavelength: {wavelength:.2f} nm")

        # Calculate and display metrics
        ssim_3d, ssim_2d, mse, mae = calculate_metrics(gt_hsi[pol_idx], gen_hsi[pol_idx])
        metric_text.set_text(f"SSIM (3D): {ssim_3d:.4f} | SSIM (2D): {ssim_2d:.4f} | MSE: {mse:.4f} | MAE: {mae:.4f}")

        fig.canvas.draw_idle()

    slider_pol.on_changed(update)
    slider_wl.on_changed(update)

    # Click event to plot spectra for a selected pixel
    def on_click(event):
        if event.inaxes in [ax_gen, ax_gt]:
            x = int(event.xdata)
            y = int(event.ydata)

            # Update markers
            gen_marker.set_data([x], [y])
            gt_marker.set_data([x], [y])

            fig.canvas.draw_idle()

            # Plot spectra
            plot_pixel_spectra(x, y, gen_hsi, gt_hsi)

    fig.canvas.mpl_connect('button_press_event', on_click)

    # Show the plot
    plt.show()

if __name__ == "__main__":
    main()
