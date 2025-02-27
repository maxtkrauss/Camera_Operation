import os
import numpy as np
import tifffile as tiff

# Constants
CHUNK_SIZE = 120 # cubert
#CHUNK_SIZE = 660 # thorlabs
CLICK_X, CLICK_Y = 171, 111  # Coordinates where the image was clicked (cubert)
#CLICK_X, CLICK_Y = 1392, 604 # thorlabs
INPUT_FOLDER = r"C:\Users\menon\Documents\Camera_Operation\generation_folder\tape\cubert"
OUTPUT_FOLDER = r"C:\Users\menon\Documents\Camera_Operation\generation_folder\tape\cubert"

# Ensure the output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to load a hyperspectral image
def load_hyperspectral_image(file_path):
    try:
        image = tiff.imread(file_path).astype(np.float32)
        return image
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

# Function to save the cropped chunk
def save_chunk(image, center_x, center_y, save_path):
    z, h, w = image.shape
    half_size = CHUNK_SIZE // 2
    start_x = max(center_x - half_size, 0)
    end_x = min(center_x + half_size, w)
    start_y = max(center_y - half_size, 0)
    end_y = min(center_y + half_size, h)

    # Ensure the chunk is 120x120 in spatial dimensions
    chunk = image[:, start_y:end_y, start_x:end_x]
    if chunk.shape[1] != CHUNK_SIZE or chunk.shape[2] != CHUNK_SIZE:
        print(f"Error: Selected chunk from {save_path} is not 120x120.")
        return

    # Save the chunk as a new TIFF file
    tiff.imwrite(save_path, chunk)
    print(f"Chunk saved to {save_path}")

# Main function to process all images
def process_images(input_folder, output_folder, click_x, click_y):
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".tif"):
            file_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, f"crop_{file_name}")

            # Load the image
            image = load_hyperspectral_image(file_path)
            if image is not None:
                # Save the cropped chunk
                save_chunk(image, click_x, click_y, output_path)

if __name__ == "__main__":
    process_images(INPUT_FOLDER, OUTPUT_FOLDER, CLICK_X, CLICK_Y)
