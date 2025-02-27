import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QHBoxLayout, QLineEdit
)
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas
)
from matplotlib.figure import Figure
import numpy as np
import tifffile
from scene_imager import setup_thorlabs_cam, take_and_save_thorlabs_image, setup_cubert_cam, take_and_save_cubert_image
import scene_imager as si
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QFont, QPalette

class CameraGUI(QWidget):   
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Camera GUI")
        self.folder_path = ""
        self.cam_tl = None
        self.acquisitionContext = None
        self.processingContext = None
        self.image_counter = 1
        self.auto_timer = QTimer()  # Timer for auto mode
        self.auto_timer.timeout.connect(self.capture_images)
        self.countdown_timer = QTimer()  # Timer for countdown display
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.remaining_seconds = 0
        self.auto_mode_active = False  # Track if auto mode is active

        # Variables to store dark calibration file paths
        self.dark_cal_tl = None
        self.dark_cal_cb = None

        self.initUI()
        self.initCameras()

    def initUI(self):
        main_layout = QHBoxLayout()

        # Image display areas
        image_layout = QVBoxLayout()
        tl_label_text = QLabel("Thorlabs Image")
        tl_label_text.setAlignment(Qt.AlignCenter)
        self.tl_label = QLabel()
        self.tl_label.setAlignment(Qt.AlignCenter)
        image_layout.addWidget(tl_label_text)
        image_layout.addWidget(self.tl_label)

        cb_label_text = QLabel("Cubert Image")
        cb_label_text.setAlignment(Qt.AlignCenter)
        self.cb_label = QLabel()
        self.cb_label.setAlignment(Qt.AlignCenter)
        image_layout.addWidget(cb_label_text)
        image_layout.addWidget(self.cb_label)
        main_layout.addLayout(image_layout)

        # Countdown display and controls
        countdown_layout = QVBoxLayout()

        # Countdown label
        self.countdown_label = QLabel("Countdown: N/A")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.countdown_label.setFixedSize(200, 100)
        self.countdown_label.setAutoFillBackground(True)
        countdown_layout.addWidget(self.countdown_label)

        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        folder_button = QPushButton("Choose Folder")
        folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(folder_button)
        countdown_layout.addLayout(folder_layout)

        # Dark calibration file selection
        dark_cal_layout = QVBoxLayout()

        # Thorlabs dark cal file
        dark_cal_tl_button = QPushButton("Choose Thorlabs Dark Cal File")
        dark_cal_tl_button.clicked.connect(self.select_dark_cal_tl)
        self.dark_cal_tl_label = QLabel("Thorlabs Dark Cal: None")
        dark_cal_layout.addWidget(self.dark_cal_tl_label)
        dark_cal_layout.addWidget(dark_cal_tl_button)

        # Cubert dark cal file
        dark_cal_cb_button = QPushButton("Choose Cubert Dark Cal File")
        dark_cal_cb_button.clicked.connect(self.select_dark_cal_cb)
        self.dark_cal_cb_label = QLabel("Cubert Dark Cal: None")
        dark_cal_layout.addWidget(self.dark_cal_cb_label)
        dark_cal_layout.addWidget(dark_cal_cb_button)

        countdown_layout.addLayout(dark_cal_layout)

        # Auto mode
        auto_layout = QHBoxLayout()
        self.interval_input = QLineEdit()
        self.interval_input.setPlaceholderText("Enter seconds (e.g., 10)")
        auto_button = QPushButton("Auto")
        auto_button.clicked.connect(self.toggle_auto_mode)
        auto_layout.addWidget(self.interval_input)
        auto_layout.addWidget(auto_button)
        countdown_layout.addLayout(auto_layout)

        main_layout.addLayout(countdown_layout)
        self.setLayout(main_layout)

        # Now safely update countdown color
        self.update_countdown_color(remaining_seconds=0)

    def initCameras(self):
        self.cam_tl = setup_thorlabs_cam()
        self.acquisitionContext, self.processingContext, _ = setup_cubert_cam()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_path = folder
            si.thorlabs_image_folder = os.path.join(folder, "thorlabs")
            si.cubert_image_folder = os.path.join(folder, "cubert")
            os.makedirs(si.thorlabs_image_folder, exist_ok=True)
            os.makedirs(si.cubert_image_folder, exist_ok=True)
            self.folder_input.setText(folder)

    def select_dark_cal_tl(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Thorlabs Dark Cal File", "", "All Files (*.*)")
        if file:
            self.dark_cal_tl = np.load(file)
            self.dark_cal_tl_label.setText(f"Thorlabs Dark Cal: {os.path.basename(file)}")
        else:
            self.dark_cal_tl = None

    def select_dark_cal_cb(self):
        
        file, _ = QFileDialog.getOpenFileName(self, "Select Cubert Dark Cal File", "", "All Files (*.*)")
        if file:
            self.dark_cal_cb = np.load(file)
            self.dark_cal_cb_label.setText(f"Cubert Dark Cal: {os.path.basename(file)}")
        else:
            self.dark_cal_cb = None

    def capture_images(self):
        if not self.folder_path:
            print("Please select a folder to save images.")
            return

        if self.auto_mode_active:
            self.countdown_label.setText("Imaging")
            self.update_countdown_color(imaging=True)
            self.countdown_timer.stop()

        img_name = f"image_{self.image_counter}"

        # Capture Thorlabs image
        tl_success, self.cam_tl = take_and_save_thorlabs_image(
            img_name=img_name, dark_cal=self.dark_cal_tl, cam_tl=self.cam_tl
        )

        # Capture Cubert image
        if tl_success:
            take_and_save_cubert_image(
                img_name=img_name, dark_cal=self.dark_cal_cb,
                acquContext=self.acquisitionContext, procContext=self.processingContext
            )

        tl_path = os.path.join(self.folder_path, f"thorlabs/{img_name}_thorlabs.tif")
        cb_path = os.path.join(self.folder_path, f"cubert/{img_name}_cubert.tif")

        if os.path.exists(tl_path):
            self.display_image(tl_path, self.tl_label, channel=0, max_size=(500, 500), tl_flag = True)
        if os.path.exists(cb_path):
            self.display_image(cb_path, self.cb_label, channel=0, max_size=(500, 500), tl_flag = False)

        self.image_counter += 1

        if self.auto_mode_active:
            interval = int(self.interval_input.text())
            self.remaining_seconds = interval
            self.countdown_timer.start(1000)

    def display_image(self, path, label, channel=0, max_size=(500, 500), tl_flag=True):
        img = tifffile.imread(path)

        # Define crop coordinates
        if tl_flag:
            crop_coords = ((1250, 1910), (510, 1170))  # Thorlabs crop
        else:
            crop_coords = ((136, 256), (89, 209))  # Cubert crop

        # Crop the image
        img = img[:, crop_coords[1][0]:crop_coords[1][1], crop_coords[0][0]:crop_coords[0][1]] if img.ndim > 2 else img[crop_coords[1][0]:crop_coords[1][1], crop_coords[0][0]:crop_coords[0][1]]
        print(img.shape)
        print(np.max(img))
        print(np.average(img))
        # Select channel if multi-channel image
        if img.ndim > 2:
            img = img[channel] if channel < img.shape[0] else img[0]  # Ensure valid channel selection

        # Normalize image to 8-bit grayscale
        if img.dtype == np.uint16 and np.max(img) <= 4095:
            img_normalized = ((img / 4095) * 255).astype(np.uint8)
        else:
            img_normalized = ((img - np.min(img)) / (np.max(img) - np.min(img)) * 255).astype(np.uint8)

        # Convert to QImage
        height, width = img_normalized.shape
        bytes_per_line = width
        qimg = QImage(img_normalized.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg)

        # Compute dynamic scaling factor
        max_width, max_height = max_size
        scale_factor = min(max_width / width, max_height / height)  # Scale both images to `max_size`

        # Scale the pixmap
        scaled_pixmap = pixmap.scaled(int(width * scale_factor), int(height * scale_factor), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Set to label
        label.setPixmap(scaled_pixmap)
        label.setFixedSize(scaled_pixmap.size())


    def toggle_auto_mode(self):
        if self.auto_mode_active:
            self.auto_mode_active = False
            self.auto_timer.stop()
            self.countdown_timer.stop()
            self.countdown_label.setText("Countdown")
            self.update_countdown_color(remaining_seconds=0)
        else:
            try:
                interval = int(self.interval_input.text())
                if interval <= 0:
                    raise ValueError
                self.auto_mode_active = True
                self.remaining_seconds = interval
                self.countdown_timer.start(1000)
            except ValueError:
                print("Invalid interval. Please enter a positive integer.")

    def update_countdown(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.countdown_label.setText(f"{self.remaining_seconds} seconds")
            self.update_countdown_color(remaining_seconds=self.remaining_seconds)
        else:
            self.countdown_timer.stop()
            self.countdown_label.setText("Imaging")
            self.update_countdown_color(imaging=True)
            self.capture_images()
            self.remaining_seconds = int(self.interval_input.text())
            self.countdown_timer.start(1000)

    def update_countdown_color(self, remaining_seconds=0, imaging=False):
        palette = self.countdown_label.palette()
        if imaging:
            palette.setColor(QPalette.Window, QColor(0, 255, 0))
        else:
            try:
                interval = int(self.interval_input.text()) if self.interval_input.text() else 1
            except ValueError:
                interval = 1
            intensity = min(255, max(0, int(255 * (1 - remaining_seconds / interval))))
            palette.setColor(QPalette.Window, QColor(255, intensity, intensity))
        self.countdown_label.setPalette(palette)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = CameraGUI()
    gui.show()
    sys.exit(app.exec_())
