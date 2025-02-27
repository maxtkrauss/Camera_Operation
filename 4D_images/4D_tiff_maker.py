import os
import numpy as np
import tifffile as tiff

# Constants
INPUT_FOLDER = r""
OUTPUT_FILE = r"C:\Users\menon\Documents\Camera_Operation\images\spectro_pol\250\cubert\4D_ground_truth.tif"

# Expected file order
EXPECTED_FILES = [
    r"C:\Users\menon\Documents\Camera_Operation\images\spectro_pol\250\cubert\chunk_171_109_0_degree_cubert.tif",
    r"C:\Users\menon\Documents\Camera_Operation\images\spectro_pol\250\cubert\chunk_171_109_45_degree_cubert.tif",
    r"C:\Users\menon\Documents\Camera_Operation\images\spectro_pol\250\cubert\chunk_171_109_90_degree_cubert.tif",
    r"C:\Users\menon\Documents\Camera_Operation\images\spectro_pol\250\cubert\chunk_171_109_raw_cubert.tif"
]

def combine_hsis(input_folder, output_file, expected_files):
    combined_hsi = []
    combined_paths = []

    for file_name in expected_files:
        file_path = os.path.join(input_folder, file_name)

        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist.")
            return

        # Load the HSI
        hsi = tiff.imread(file_path).astype(np.float32)

        combined_hsi.append(hsi)
        combined_paths.append(file_path)
        

    # Stack along a new dimension (polarization axis)
    combined_hsi = np.stack(combined_hsi, axis=0)

    # Save the combined HSI
    tiff.imwrite(output_file, combined_hsi)
    print(f"Combined HSI {combined_hsi.shape} saved to {output_file}")

if __name__ == "__main__":
    combine_hsis(INPUT_FOLDER, OUTPUT_FILE, EXPECTED_FILES)
