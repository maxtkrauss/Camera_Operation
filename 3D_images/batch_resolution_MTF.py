import numpy as np
import matplotlib.pyplot as plt
import cv2
from scipy.fftpack import fft, fftfreq
from skimage.draw import line

def compute_contrast(cross_section):
    """Compute Michelson contrast of a line profile."""
    max_val = np.max(cross_section)
    min_val = np.min(cross_section)
    return (max_val - min_val) / (max_val + min_val)

def compute_mtf(cross_section, pixel_size):
    """Compute Modulation Transfer Function (MTF) from a cross-section."""
    # Compute FFT of the intensity profile
    fft_vals = np.abs(fft(cross_section))
    freqs = fftfreq(len(cross_section), pixel_size)  # Convert to spatial frequencies

    # Keep only positive frequencies
    freqs = freqs[:len(freqs)//2]
    fft_vals = fft_vals[:len(fft_vals)//2]

    # Normalize MTF (set max to 1)
    fft_vals /= np.max(fft_vals)
    
    # Find MTF10 (spatial frequency where contrast drops to 10%)
    try:
        mtf10_idx = np.where(fft_vals <= 0.1)[0][0]
        mtf10_freq = freqs[mtf10_idx]
    except IndexError:
        mtf10_freq = None  # No clear MTF10 threshold found

    return freqs, fft_vals, mtf10_freq

def get_intensity_profile(image):
    """Allows user to draw a line on an image and extracts intensity values along the line."""
    plt.imshow(image, cmap='gray')
    plt.title("Click Two Points to Draw a Line")
    points = plt.ginput(2)  # Get two points from user
    plt.close()
    
    # Convert points to integer pixel coordinates
    x0, y0 = int(points[0][0]), int(points[0][1])
    x1, y1 = int(points[1][0]), int(points[1][1])

    # Get pixel indices along the line
    rr, cc = line(y0, x0, y1, x1)
    
    # Extract intensity values along the line
    cross_section = image[rr, cc]

    return cross_section, (x0, y0, x1, y1)

# Load an example image (grayscale)
image_path = r"C:\Users\menon\Documents\Camera_Operation\resolution_charts\USAF_Res_Chart_240.jpg"
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  

# Extract intensity profile
cross_section, line_coords = get_intensity_profile(image)

# Compute contrast
contrast = compute_contrast(cross_section)

# Compute MTF and find MTF10 threshold
pixel_size = 1.0  # Adjust based on actual pixel spacing
freqs, mtf_vals, mtf10 = compute_mtf(cross_section, pixel_size)

# Print results
print(f"Michelson Contrast: {contrast:.3f}")
if mtf10:
    print(f"MTF10 Resolution Cutoff: {mtf10:.3f} cycles/pixel")
else:
    print("MTF10 threshold not reached within data range.")

# Plot Intensity Profile
plt.figure(figsize=(10, 4))
plt.plot(cross_section, label="Intensity Profile")
plt.xlabel("Pixel Position")
plt.ylabel("Intensity")
plt.title("Cross-Section Intensity Profile")
plt.legend()
plt.grid()
plt.show()

# Plot MTF Curve
plt.figure(figsize=(10, 4))
plt.plot(freqs, mtf_vals, label="MTF Curve")
plt.axhline(0.1, linestyle="--", color="red", label="MTF10 Threshold (10%)")
if mtf10:
    plt.axvline(mtf10, linestyle="--", color="green", label=f"MTF10: {mtf10:.3f} cycles/pixel")
plt.xlabel("Spatial Frequency (cycles/pixel)")
plt.ylabel("Modulation (MTF)")
plt.title("Modulation Transfer Function (MTF)")
plt.legend()
plt.grid()
plt.show()
