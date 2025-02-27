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


## Parameters
thorlabs_image_folder = 'example_images//thorlabs'
cubert_image_folder = 'example_images//cubert'

exposure_time_tl = 400 # in ms
exposure_time_cb = 550 # in ms

# Additional parameters for Thorlabs cam
do_dark_subtract_tl = True
path_dark_tl = "C:\\Users\\menon\\Documents\\Camera_Operation\\images\\dark_frame\\thorlabs\\thorlabs_masterdark.npy"  
roi_tl = (0, 2448, 0, 2048)

# Additional parameters for Cubert cam
do_dark_subtract_cb = True
path_dark_cb = "C:\\Users\\menon\\Documents\\Camera_Operation\\images\\dark_frame\\cubert\\cubert_masterdark.npy"
distance_cb = 1100  # in mm

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

    # Start counter
    img_num = 1

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

## Take Thorlabs image, apply dark calibration, and save as TIFF
def take_and_save_thorlabs_image(img_name, dark_cal, cam_tl):
    imaging_failed_counter = 0
    success = False

    while imaging_failed_counter < 15:
        print(f"TL: Taking {exposure_time_tl}ms exposure with TL cam...")
        try:
            img_tl = cam_tl.snap() - dark_cal[0] if do_dark_subtract_tl and dark_cal is not None else cam_tl.snap()
            print("Shape")
            print(img_tl.shape)
            img_tl = np.maximum(img_tl, 0)
            success = True
            break
        except:
            imaging_failed_counter += 1
            print(f"TL: Imaging failed. Restarting cam. Counter {imaging_failed_counter}")
            cam_tl.close()
            cam_tl = setup_thorlabs_cam()

    if success:
        img_tl_pol = pa.demosaicing(img_raw=img_tl, code=pa.COLOR_PolarMono)
        img_tl_pol = np.append(img_tl_pol, [img_tl], axis=0)
        path = os.path.join(thorlabs_image_folder, f"{img_name}_thorlabs.tif")
        tifffile.imwrite(path, img_tl_pol, photometric='minisblack')
        print(f"TL: Saved image as TIFF. Shape: {img_tl_pol.shape}, Max: {np.max(img_tl_pol)}, Min: {np.min(img_tl_pol)}, Avg: {np.average(img_tl_pol)}, SNR: {snr(img_tl_pol)}")
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
            mesu, res = am.get(timedelta(milliseconds=2500))
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
                tifffile.imwrite(path, data_array, photometric='minisblack')
                print(f"CB: Saved image as TIFF. Shape: {data_array.shape}, Max: {np.max(data_array)}, Min: {np.min(data_array)}, Avg: {np.average(data_array)}, SNR: {snr(data_array)}")
                saved = True
                break
            else:
                imaging_failed_counter += 1
                print(f"CB: Image saving failed. Counter: {imaging_failed_counter}")
        else:
            imaging_failed_counter += 1
            print(f"CB: Image saving failed. Counter: {imaging_failed_counter}")

    return saved

## Calculate SNR
def snr(img, axis=None, ddof=0):
    img = np.asanyarray(img)
    m = img.mean(axis)
    sd = img.std(axis=axis, ddof=ddof)
    return np.where(sd == 0, 0, m/sd)

## Run main
if __name__ == "__main__":
    main()
