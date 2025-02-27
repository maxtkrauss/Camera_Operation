import numpy as np
import matplotlib.pyplot as plt
import tifffile as tiff
import os
import re
from tkinter import Tk, filedialog
from matplotlib.widgets import Cursor
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr

# Define directory containing images
directory = r"C:\Users\menon\Documents\Camera_Operation\images\spectro\run_2\cubert_cropped"

# Define wavelength range for bands 0-64
wavelengths = np.linspace(450, 706, 65)

# Function to load and normalize images
def load_images(directory):
    images = {}
    pattern = re.compile(r"\((\d+),(\d+),(\d+)\)_cubert.tif")
    
    for file in sorted(os.listdir(directory)):  # Ensure consistent file order
        match = pattern.match(file)
        if match:
            rgb = tuple(map(int, match.groups()))
            img_path = os.path.join(directory, file)
            img = tiff.imread(img_path)
            img = img[:65]  # Only take bands 0-64
            img = img / np.max(img)  # Normalize
            images[rgb] = img.astype(np.float32)  # Ensure consistent data type
    
    return images

# Function to analyze spectra at selected pixel
def analyze_pixel_spectrum(x, y):
    plt.figure(figsize=(8, 6))
    
    for rgb, img in images.items():
        spectrum = img[:, y, x]  # Extract spectral data
        color = 'blue' if rgb == (255, 255, 255) else tuple(c / 255 for c in rgb)  # Ensure (255,255,255) is blue
        plt.plot(wavelengths, spectrum, label=f"{rgb}", color=color)
    
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Normalized Intensity")
    plt.title(f"Spectral Response at Pixel ({x}, {y})")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # Second figure with individual comparisons and MSE values
    fig, axes = plt.subplots(4, 2, figsize=(12, 10))
    axes = axes.flatten()
    ref_spectrum = images[ref_rgb][:, y, x]
    
    comparison_metrics = {}
    other_rgbs = list(images.keys())
    for i, rgb in enumerate(other_rgbs[:8]):
        ax = axes[i]
        test_spectrum = images[rgb][:, y, x]
        mse = mean_squared_error(ref_spectrum, test_spectrum)
        pearson_corr, _ = pearsonr(ref_spectrum, test_spectrum)
        comparison_metrics[rgb] = (mse, pearson_corr)
        
        ax.plot(wavelengths, ref_spectrum, label=f"{ref_rgb}", linestyle='dashed', color='blue')
        ax.plot(wavelengths, test_spectrum, label=f"{rgb}", color=tuple(c / 255 for c in rgb))
        ax.set_title(f"Comparison: {ref_rgb} vs {rgb}\nMSE = {mse:.5f}, r = {pearson_corr:.3f}")
        ax.set_xlabel("Wavelength (nm)")
        ax.set_ylabel("Normalized Intensity")
        ax.legend()
        ax.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # Identify least similar color to (255,255,255) using a combined ranking
    final_ranking = sorted(comparison_metrics.items(), key=lambda x: (x[1][0], -abs(x[1][1])), reverse=True)
    least_similar_rgb = final_ranking[0][0]
    print(f"The least similar spectrum to {ref_rgb} is {least_similar_rgb} with MSE = {comparison_metrics[least_similar_rgb][0]:.5f}, Pearson r = {comparison_metrics[least_similar_rgb][1]:.3f}")
    
    # Compute MSE and Pearson Correlation between all pairs of spectra
    all_metrics = {}
    for rgb1 in images.keys():
        for rgb2 in images.keys():
            if rgb1 != rgb2:
                key = tuple(sorted([rgb1, rgb2]))  # Ensure consistent ordering of keys
                mse = mean_squared_error(images[rgb1][:, y, x], images[rgb2][:, y, x])
                pearson_corr, _ = pearsonr(images[rgb1][:, y, x], images[rgb2][:, y, x])
                all_metrics[key] = (mse, pearson_corr)
    
    # Identify the most dissimilar spectra overall using the same ranking approach
    most_dissimilar_pair = sorted(all_metrics.items(), key=lambda x: (x[1][0], -abs(x[1][1])), reverse=True)[0]
    print(f"The most dissimilar spectra overall are {most_dissimilar_pair[0][0]} and {most_dissimilar_pair[0][1]} with MSE = {all_metrics[most_dissimilar_pair[0]][0]:.5f}, Pearson r = {all_metrics[most_dissimilar_pair[0]][1]:.3f}")

# Load images
images = load_images(directory)

# Select reference image for pixel selection
ref_rgb = (255, 255, 255)
ref_image = images[ref_rgb][0]  # First channel

# Plot and allow pixel selection
def onclick(event):
    if event.xdata is None or event.ydata is None:
        return
    
    x, y = int(event.xdata), int(event.ydata)
    plt.close()
    analyze_pixel_spectrum(x, y)

fig, ax = plt.subplots()
cursor = Cursor(ax, useblit=True, color='red', linewidth=1)
ax.imshow(ref_image, cmap='gray')
ax.set_title("Click to Select a Pixel for Spectral Analysis")
fig.canvas.mpl_connect('button_press_event', onclick)
plt.show()
