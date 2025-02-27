from PIL import Image

# Load the image
image_path = r"C:\Users\menon\Documents\Camera_Operation\resolution_charts\Res_Charts_3\(255,255,255).jpg"
image = Image.open(image_path)

# Define the number of pixels to add at the top
extra_height = 175 # Adjust as needed

# Create a new blank image with extra space at the top
new_size = (image.width, image.height + extra_height)
new_image = Image.new("RGB", new_size, (0, 0, 0))  # Assuming black background

# Paste the original image into the new image
new_image.paste(image, (0, extra_height))

# Save the modified image
edited_image_path = r"C:\Users\menon\Documents\Camera_Operation\resolution_charts\Res_Charts_4\(255,255,255).jpg"
new_image.save(edited_image_path)

# Provide the download link
edited_image_path
