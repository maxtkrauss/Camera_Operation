import os
os.add_dll_directory(r"C:\\Users\\menon\\Documents\\FTDI_drivers\\amd64")
os.add_dll_directory(r"C:\\Program Files\\Cuvis\\bin")
os.add_dll_directory(r"C:\\Users\\menon\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\cuvis_il")
os.environ["CUVIS"] = r"C:\\Program Files\\Cuvis"

import pylablib as pll
from pylablib.devices import Thorlabs as tl
import cuvis
import time
import platform
from datetime import timedelta
import tifffile
import numpy as np
import polanalyser as pa
import pygame

## Parameters
thorlabs_image_folder = 'example_images//thorlabs'
cubert_image_folder = 'example_images//cubert'
display_image_folder = r"E:\NASA_HSI\image_datasets\flickr_dataset\flickr30k_images\flickr30k_images"


display_x = 1920
display_y = 1080
img_size_x = 426*2.5
img_size_y = 240*2.5
img_offset_x = 0
img_offset_y = 0

exposure_time_tl = 450 # in ms
exposure_time_cb = 4500 # in ms

# Additional parameters for Thorlabs cam
do_dark_subtract_tl = True
path_dark_tl = "C:\\Users\\menon\\Documents\\Camera_Operation\\images\\dark_frame\\thorlabs\\thorlabs_masterdark.npy"  
roi_tl = (0, 2448, 0, 2048)

# Additional parameters for Cubert cam
do_dark_subtract_cb = True
path_dark_cb = "C:\\Users\\menon\\Documents\\Camera_Operation\\images\\dark_frame\\cubert\\cubert_masterdark.npy"
distance_cb = 800  # in mm

## Main function
def main():
    # Setup the Thorlabs cam
    cam_tl = setup_thorlabs_cam()
    print("TL setup done.")

    # Get Thorlabs masterdark calibration frame
    dark_calibration_tl = np.load(path_dark_tl) if do_dark_subtract_tl else None
    print(dark_calibration_tl.shape)

    # Setup the Cubert cam
    acquisitionContext, processingContext, cubeExporter = setup_cubert_cam()
    print("CB setup done.")

    # Calibrate the Cubert cam
    dark_calibration_cb = np.load(path_dark_cb) if do_dark_subtract_cb else None

    # Set up the pygame display and images
    scrn, images_disp = setup_pygame_display(display_x, display_y, img_size_x, img_size_y, display_image_folder)
    print("Pygame setup done.")

    # Wait a few seconds so the monitor can update
    pygame.time.wait(1000)

    img_num = 1

    # Loop over all loaded display images
    for img_disp in images_disp:

        # Display image
        print(f"Image #{img_num}")
        img_name = display_image(img_disp=img_disp, scrn=scrn)

        # Taking and saving photo with Thorlabs cam
        tl_success, cam_tl = take_and_save_thorlabs_image(img_name=img_name, dark_cal=dark_calibration_tl, cam_tl=cam_tl)

        # Taking and saving photo with Cubert cam
        if tl_success:
            take_and_save_cubert_image(img_name=img_name, dark_cal=dark_calibration_cb, acquContext=acquisitionContext, procContext=processingContext)
        else:
            print("Skipping CB image because TL imaging was unsuccessful.")

        # wait a second
        pygame.time.wait(1000)

        img_num += 1

                # test if pygame should stop
        for e in pygame.event.get():
            if e.type == pygame.QUIT or e.type == pygame.KEYDOWN:
                print("Quitting.")
                pygame.quit()

    print("\nDataset creation finished. Quitting.")
    cam_tl.close()
    pygame.quit()


    # Wait for user input to capture images
    while True:
        input("Press Enter to capture images...")
        img_name = str(img_num)

        # Capture and save Thorlabs image
        tl_success, cam_tl = take_and_save_thorlabs_image(
            img_name=img_name, dark_cal=dark_calibration_tl, cam_tl=cam_tl
        )

        # Capture and save Cubert image if Thorlabs image was successful
        if tl_success:
            take_and_save_cubert_image(
                img_name=img_name, dark_cal=dark_calibration_cb,
                acquContext=acquisitionContext, procContext=processingContext
            )
        else:
            print("Skipping CB image because TL imaging was unsuccessful.")

        print("\nImage capture complete. Press Ctrl+C to quit.")
        img_num += 1

    cam_tl.close()


## Setup Thorlabs camera
def setup_thorlabs_cam():
    tl.list_cameras_tlcam()
    cam = tl.ThorlabsTLCamera()
    cam.set_exposure(exposure_time_tl * 1e-3)
    cam.set_roi(*roi_tl, hbin=1, vbin=1)
    return cam

## Take Thorlabs image, auto-adjust exposure, apply dark calibration, and save as TIFF
def take_and_save_thorlabs_image(img_name, dark_cal, cam_tl, max_target=4050, tolerance=100):
    imaging_failed_counter = 0
    success = False
    global exposure_time_tl

    while imaging_failed_counter < 15:
        print(f"TL: Taking {exposure_time_tl}ms exposure with TL cam...")

        try:
            # Capture Image
            img_tl = cam_tl.snap() - dark_cal[0] if do_dark_subtract_tl and dark_cal is not None else cam_tl.snap()
            img_tl = np.maximum(img_tl, 0)

            # Convert to multi-channel polarized image
            img_tl_pol = pa.demosaicing(img_raw=img_tl, code=pa.COLOR_PolarMono)
            img_tl_pol = np.append(img_tl_pol, [img_tl], axis=0)

            # Crop region (from Camera_GUI.py)
            y1, y2, x1, x2 = 399, 1059, 1177, 1837
            img_tl_pol_cropped = img_tl_pol[:, y1:y2, x1:x2]

            # Get max pixel value for Channel 3
            max_pixel = np.max(img_tl_pol_cropped[0])
            print(f"Exposure: {exposure_time_tl}ms, Channel 0 Max: {max_pixel}")

            # Adjust step size dynamically
            step_size = max(1, abs(max_pixel - max_target) // 10)

            # Adjust exposure dynamically
            if max_target - tolerance <= max_pixel <= max_target:
                print(f"✅ Optimal exposure found: {exposure_time_tl}ms")
                success = True
                break  # Exit loop if within target range
            elif max_pixel > max_target:
                exposure_time_tl = max(1, exposure_time_tl - step_size)  # Reduce exposure
            else:
                exposure_time_tl = exposure_time_tl + step_size  # Increase exposure

            # Apply new exposure
            cam_tl.set_exposure(exposure_time_tl * 1e-3)

        except:
            imaging_failed_counter += 1
            print(f"TL: Imaging failed. Restarting cam. Counter {imaging_failed_counter}")
            cam_tl.close()
            cam_tl = setup_thorlabs_cam()

    if success:
        path = os.path.join(thorlabs_image_folder, f"{img_name}_thorlabs.tif")
        tifffile.imwrite(path, img_tl_pol_cropped, photometric='minisblack')
        exposure_time_tl = 255
        print(f"TL: Saved image as TIFF. Shape: {img_tl_pol_cropped.shape}, Max: {np.max(img_tl_pol_cropped[0])}, Min: {np.min(img_tl_pol_cropped[0])}, Avg: {np.average(img_tl_pol_cropped[3])}, SNR: {snr(img_tl_pol_cropped)}")
    else:
        print("TL: No image to save.")

    return success, cam_tl



## Setup Cubert camera
def setup_cubert_cam():
    data_dir = os.getenv("CUVIS") if platform.system() == "Windows" else os.getenv("CUVIS_DATA")
    factory_dir = os.path.join(data_dir, "factory")
    userSettingsDir = os.path.join(data_dir, os.pardir, "settings")

    settings = cuvis.General(userSettingsDir)
    settings.set_log_level("info")

    calibration = cuvis.Calibration(factory_dir)
    processingContext = cuvis.ProcessingContext(calibration)
    acquisitionContext = cuvis.AcquisitionContext(calibration)

    saveArgs = cuvis.SaveArgs(export_dir=cubert_image_folder, allow_overwrite=True, allow_session_file=True)
    cubeExporter = cuvis.CubeExporter(saveArgs)

    while acquisitionContext.state == cuvis.HardwareState.Offline:
        print(".", end="")
        time.sleep(1)
    print("\nCubert camera is online.")

    acquisitionContext.operation_mode = cuvis.OperationMode.Software
    acquisitionContext.integration_time = exposure_time_cb
    processingContext.calc_distance(distance_cb)

    return acquisitionContext, processingContext, cubeExporter

## Take Cubert image, apply dark calibration, and save as TIFF
def take_and_save_cubert_image(img_name, dark_cal, acquContext, procContext):
    imaging_failed_counter = 0
    saved = False

    while imaging_failed_counter < 15:
        time.sleep(0.5)
        print(f"CB: Taking {exposure_time_cb}ms exposure with CB cam...")
        try:
            am = acquContext.capture()
            mesu, res = am.get(timedelta(milliseconds=3000))
        except:
            mesu = None
            imaging_failed_counter += 1
            print(f"CB: Imaging failed. Counter: {imaging_failed_counter}")

        if mesu is not None:
            mesu.set_name(f"{img_name}_cubert")
            procContext.apply(mesu)
            data_array = np.array(mesu.data['cube'].array)
            data_array = data_array.transpose(2, 0, 1)
            if do_dark_subtract_cb and dark_cal is not None:
                data_array = np.maximum(data_array.astype(float) - dark_cal.astype(float), 0)
            if snr(data_array) > 0.05:
                path = os.path.join(cubert_image_folder, f"{img_name}_cubert.tif")
                # Crop region for Cubert image
                y1, y2 = 75, 195
                x1, x2 = 116, 236
                data_array_cropped = data_array[:, y1:y2, x1:x2]  # Crop spatial dimensions
                tifffile.imwrite(path, data_array_cropped, photometric='minisblack')
                print(f"CB: Saved image as TIFF. Shape: {data_array_cropped.shape}, Max: {np.max(data_array_cropped)}, Min: {np.min(data_array_cropped)}, Avg: {np.average(data_array_cropped)}, SNR: {snr(data_array_cropped)}")
                saved = True
                break
            else:
                imaging_failed_counter += 1
                print(f"CB: Image saving failed. Counter: {imaging_failed_counter}")
        else:
            imaging_failed_counter += 1
            print(f"CB: Image saving failed. Counter: {imaging_failed_counter}")

    return saved

def setup_pygame_display(X, Y, img_size_x, img_size_y, img_path):
    # Pygame and display setup
    pygame.init()
    try:
        scrn = pygame.display.set_mode((X, Y), pygame.FULLSCREEN, display=1) # show on second monitor
    except:
        print("No second monitor available, using main monitor.")
        scrn = pygame.display.set_mode((X, Y), pygame.FULLSCREEN)

    def transformScaleKeepRatio(image, size):
        iwidth, iheight = image.get_size()
        scale = min(size[0] / iwidth, size[1] / iheight)
        new_size = (round(iwidth * scale), round(iheight * scale))
        scaled_image = pygame.transform.scale(image, new_size)
        image_rect = scaled_image.get_rect(center = (size[0] // 2, size[1] // 2))
        return scaled_image, image_rect

    # Load images
    images = []
    filenames = sorted([f for f in os.listdir(img_path) if f.endswith('.jpg') | f.endswith('.png')], reverse=False)
    print("Filenames:", filenames)
    for name in filenames:
        img = pygame.image.load(os.path.join(img_path, name))
        images.append((*transformScaleKeepRatio(img, (img_size_x, img_size_y)), name))

    return scrn, images

## display image on screen with pygame
def display_image(img_disp, scrn):
    img_data, img_center, img_name = img_disp
    img_center.center = (display_x//2 + img_offset_x, display_y//2 + img_offset_y)
    scrn.blit(img_data, img_center) # image data, image center
    pygame.display.flip()
    pygame.display.set_caption(img_name) # image name
    print(f"\nShowing image {img_name} on display.")
    return img_name

## Calculate SNR
def snr(img, axis=None, ddof=0):
    img = np.asanyarray(img)
    m = img.mean(axis)
    sd = img.std(axis=axis, ddof=ddof)
    return np.where(sd == 0, 0, m/sd)

## Run main
if __name__ == "__main__":
    main()
