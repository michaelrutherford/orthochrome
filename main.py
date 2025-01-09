import sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QSlider,
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QSize


class ImageProcessorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Orthochrome")
        self.setGeometry(100, 100, 1000, 700)

        # Initialize UI elements
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(800, 600)
        self.image_label.setStyleSheet("padding: 20px;")

        self.upload_button = QPushButton("Upload Image", self)
        self.upload_button.setStyleSheet(
            "background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;"
        )
        self.upload_button.clicked.connect(self.upload_image)
        self.upload_button.setToolTip("Click to upload an image")

        self.download_button = QPushButton("Download Image", self)
        self.download_button.setStyleSheet(
            "background-color: #008CBA; color: white; padding: 10px; border-radius: 5px;"
        )
        self.download_button.clicked.connect(self.download_image)
        self.download_button.setEnabled(False)
        self.download_button.setToolTip("Click to download the processed image")

        # Status label for feedback
        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #555555; font-size: 14px;")

        # Layout for buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.upload_button)
        self.button_layout.addWidget(self.download_button)

        # Sliders for image adjustments
        self.brightness_slider = QSlider(Qt.Horizontal, self)
        self.brightness_slider.setRange(0, 200)
        self.brightness_slider.setValue(100)
        self.brightness_slider.setTickInterval(4)
        self.brightness_slider.setTickPosition(QSlider.TicksAbove)
        self.brightness_slider.valueChanged.connect(self.update_image)

        self.grain_slider = QSlider(Qt.Horizontal, self)
        self.grain_slider.setRange(0, 50)
        self.grain_slider.setValue(10)
        self.grain_slider.setTickInterval(1)
        self.grain_slider.setTickPosition(QSlider.TicksAbove)
        self.grain_slider.valueChanged.connect(self.update_image)

        self.vignette_slider = QSlider(Qt.Horizontal, self)
        self.vignette_slider.setRange(0, 200)
        self.vignette_slider.setValue(80)
        self.vignette_slider.setTickInterval(4)
        self.vignette_slider.setTickPosition(QSlider.TicksAbove)
        self.vignette_slider.valueChanged.connect(self.update_image)

        # Layout for sliders
        self.slider_layout = QVBoxLayout()
        self.slider_layout.addWidget(QLabel("Brightness"))
        self.slider_layout.addWidget(self.brightness_slider)
        self.slider_layout.addWidget(QLabel("Grain Intensity"))
        self.slider_layout.addWidget(self.grain_slider)
        self.slider_layout.addWidget(QLabel("Vignette Strength"))
        self.slider_layout.addWidget(self.vignette_slider)

        # Main layout configuration
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.addLayout(self.button_layout)
        self.layout.addSpacing(20)  # Add space between button and image label
        self.layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.status_label)
        self.layout.addLayout(self.slider_layout)

        self.setLayout(self.layout)

        self.image = None
        self.grain_image = None
        self.vignette_image = None
        self.grain_intensity = 10
        self.vignette_strength = 0.8
        self.brightness_factor = 1.0

    def resize_image(self, image, max_size=(800, 600)):
        """
        Resizes the image to fit within the specified max_size while maintaining aspect ratio.

        Args:
            image (PIL.Image): The image to resize.
            max_size (tuple): The maximum width and height.

        Returns:
            PIL.Image: The resized image.
        """
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image

    def upload_image(self):
        """
        Opens a file dialog to select and upload an image for processing.
        """
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.xpm *.jpg *.jpeg *.bmp *.gif)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.process_image(file_path)

    def process_image(self, file_path):
        """
        Processes the uploaded image by applying the cyan filter and preparing it for preview.

        Args:
            file_path (str): The path of the uploaded image.
        """
        self.status_label.setText("Processing Image...")
        self.image = Image.open(file_path)
        self.original_size = self.image.size
        self.image = self.resize_image(self.image)
        self.image = self.apply_cyan_filter(self.image)
        self.update_image()
        self.download_button.setEnabled(True)
        self.status_label.setText("")

    def apply_cyan_filter(self, image):
        """
        Applies a cyan filter by reducing the red channel.

        Args:
            image (PIL.Image): The image to process.

        Returns:
            PIL.Image: The cyan-filtered image.
        """
        img = image.convert("RGBA")
        r, g, b, a = img.split()
        r = r.point(lambda p: max(p - 90, 0))  # Decrease red channel
        return Image.merge("RGBA", (r, g, b, a))

    def adjust_brightness(self, image):
        """
        Adjusts the brightness of the image using the current brightness factor.

        Args:
            image (PIL.Image): The image to adjust.

        Returns:
            PIL.Image: The brightness-adjusted image.
        """
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(self.brightness_factor)

    def add_film_grain(self, image):
        """
        Adds a film grain effect to the image by generating random noise.

        Args:
            image (PIL.Image): The image to which grain is added.

        Returns:
            PIL.Image: The noisy image with film grain applied.
        """
        img_resized = self.resize_image(image)  # Resize for faster processing
        img_array = np.array(img_resized)
        noise = np.random.normal(
            scale=self.grain_intensity, size=img_array.shape
        ).astype(np.float32)
        noisy_image = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        noisy_image = Image.fromarray(noisy_image)
        noisy_image = noisy_image.filter(
            ImageFilter.GaussianBlur(radius=0.5)
        )  # Slight blur for smoothness
        return noisy_image.resize(image.size)

    def apply_vignette(self, image):
        """
        Applies a vignette effect by darkening the edges of the image.

        Args:
            image (PIL.Image): The image to apply the vignette effect on.

        Returns:
            PIL.Image: The image with the vignette applied.
        """
        img = image.convert("RGBA")
        width, height = img.size
        pixels = np.array(img)
        center_x, center_y = width // 2, height // 2
        x_indices, y_indices = np.meshgrid(np.arange(width), np.arange(height))
        dx = x_indices - center_x
        dy = y_indices - center_y
        distances = np.sqrt(dx**2 + dy**2)
        max_distance = np.sqrt(center_x**2 + center_y**2)
        vignette_factor = (
            1 - np.power(distances / max_distance, 2) * self.vignette_strength
        )
        vignette_factor = np.clip(vignette_factor, 0, 1)

        # Apply vignette effect to RGB channels, convert array to image, and return
        pixels[:, :, :3] = (
            pixels[:, :, :3] * vignette_factor[:, :, np.newaxis]
        ).astype(np.uint8)
        return Image.fromarray(pixels)

    def display_image(self, image):
        """
        Displays the processed image in the QLabel widget.

        Args:
            image (PIL.Image): The image to display.
        """
        image = image.convert("RGBA")
        img_data = image.tobytes("raw", "RGBA")
        qimg = QImage(img_data, image.width, image.height, QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimg)

        # Scale the image to fit within the label's size
        scaled_pixmap = pixmap.scaled(
            self.image_label.size() - QSize(40, 40), Qt.KeepAspectRatio
        )
        self.image_label.setPixmap(scaled_pixmap)

    def update_image(self):
        """
        Updates the image preview based on the current slider values (brightness, grain, vignette).
        """
        self.brightness_factor = (
            self.brightness_slider.value() / 100
        )  # Normalize brightness
        self.grain_intensity = self.grain_slider.value()
        self.vignette_strength = (
            self.vignette_slider.value() / 100
        )  # Normalize vignette strength

        if self.image:
            bright_image = self.adjust_brightness(self.image)
            self.grain_image = self.add_film_grain(bright_image.convert("L"))
            self.vignette_image = self.apply_vignette(self.grain_image)
            self.display_image(self.vignette_image)

    def download_image(self):
        """
        Opens a save file dialog to allow the user to save the processed image.
        The image is saved at the same resolution as the original.
        """
        if self.vignette_image:
            # Open the save file dialog
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Image",
                "",
                "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*)",
            )

            # Check if empty path
            if save_path:
                if not save_path.lower().endswith((".png", ".jpg", ".jpeg")):
                    save_path += ".png"  # Default to .png

                # Resize the processed image back to the original size before saving
                image_to_save = self.vignette_image.resize(
                    self.original_size, Image.Resampling.LANCZOS
                )

                image_to_save.save(save_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessorApp()
    window.show()
    sys.exit(app.exec())
