import os
import numpy as np
import tifffile

def create_master_dark(input_folder, output_path):
    """
    Averages all TIFF images in the input folder to create a master dark frame and saves it as a NumPy array.
    
    Parameters:
        input_folder (str): Path to the folder containing dark frame TIFF images.
        output_path (str): Path to save the resulting master dark frame as a .npy file.
    """
    # List all TIFF files in the folder
    dark_files = [f for f in os.listdir(input_folder) if f.endswith('.tif')]
    if not dark_files:
        print(f"No TIFF files found in {input_folder}")
        return

    print(f"Found {len(dark_files)} dark frame files in {input_folder}. Averaging...")

    # Read all dark frame images
    dark_frames = []
    for file in dark_files:
        filepath = os.path.join(input_folder, file)
        img = tifffile.imread(filepath)
        dark_frames.append(img)

    # Compute the average dark frame
    master_dark = np.mean(dark_frames, axis=0)

    # Save the master dark frame as a NumPy array
    np.save(output_path, master_dark)
    print(f"Master dark frame saved to {output_path}.npy")

# Paths for Thorlabs and Cubert dark frames
thorlabs_dark_folder = r"C:\Users\menon\Documents\Camera_Operation\images\new_dark_frames\thorlabs"
cubert_dark_folder = r"C:\Users\menon\Documents\Camera_Operation\images\new_dark_frames\cubert"
thorlabs_master_dark_path = r"C:\Users\menon\Documents\Camera_Operation\images\new_dark_frames\thorlabsthorlabs_display_masterdark"
cubert_master_dark_path = r"C:\Users\menon\Documents\Camera_Operation\images\new_dark_frames\cubertcubert_display_masterdark"

# Create master dark frames
create_master_dark(thorlabs_dark_folder, thorlabs_master_dark_path)
create_master_dark(cubert_dark_folder, cubert_master_dark_path)

