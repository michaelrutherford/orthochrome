from PIL import Image
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QFileDialog,
    QSlider,
    QMenu,
    QComboBox,
    QWidgetAction,
)
from PySide6.QtGui import QPixmap, QImage, QAction
from PySide6.QtCore import Qt, QSize


class ImageEditorUI(QMainWindow):
    """
    A class representing the UI of the program.
    """

    def __init__(self, image_processor):
        """
        Initializes the ImageEditorUI with the given image processor.
        """
        super().__init__()
        self.image_processor = image_processor
        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the user interface with elements and layouts.
        """
        self.setWindowTitle("Silvalide")
        self.setGeometry(100, 100, 1000, 700)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(800, 600)
        self.image_label.setStyleSheet("padding: 20px;")

        self.brightness_slider = self.create_slider(0, 200, 100)
        self.contrast_slider = self.create_slider(0, 200, 100)
        self.grain_slider = self.create_slider(0, 50, 10)
        self.vignette_slider = self.create_slider(0, 200, 40)

        self.slider_layout = self.create_slider_layout()

        self.central_widget = QWidget(self)
        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.setContentsMargins(10, 10, 10, 10)
        self.central_layout.addSpacing(20)
        self.central_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        self.central_layout.addLayout(self.slider_layout)
        self.setCentralWidget(self.central_widget)

        self.create_menu_bar()

    def create_slider(self, min_value, max_value, initial_value):
        """
        Creates a slider with the specified range and initial value, and connects it to the image update function.
        """
        slider = QSlider(Qt.Horizontal, self)
        slider.setRange(min_value, max_value)
        slider.setValue(initial_value)
        slider.valueChanged.connect(self.update_image)
        return slider

    def create_slider_layout(self):
        """
        Creates the layout to display sliders for adjusting values.
        """
        layout = QGridLayout()
        layout.addWidget(QLabel("Brightness"), 0, 0)
        layout.addWidget(self.brightness_slider, 0, 1)
        layout.addWidget(QLabel("Contrast"), 0, 2)
        layout.addWidget(self.contrast_slider, 0, 3)
        layout.addWidget(QLabel("Grain Intensity"), 1, 0)
        layout.addWidget(self.grain_slider, 1, 1)
        layout.addWidget(QLabel("Vignette Strength"), 1, 2)
        layout.addWidget(self.vignette_slider, 1, 3)
        return layout

    def create_menu_bar(self):
        """
        Creates and sets up the menu bar.
        """
        menu_bar = self.menuBar()

        file_menu = QMenu("File", self)
        file_menu.addAction(self.create_action("Open Image", self.upload_image))
        file_menu.addAction(self.create_action("Save Image", self.download_image))
        menu_bar.addMenu(file_menu)

        preset_menu = QMenu("Presets", self)
        self.preset_combo = QComboBox(self)
        self.preset_combo.addItems(["Film", "Orthochromatic", "Sepia", "Infrared"])
        self.preset_combo.currentIndexChanged.connect(self.apply_preset)
        preset_action = QWidgetAction(self)
        preset_action.setDefaultWidget(self.preset_combo)
        preset_menu.addAction(preset_action)
        menu_bar.addMenu(preset_menu)

        help_menu = QMenu("Help", self)
        help_menu.addAction(self.create_action("Help", lambda: None))
        help_menu.addAction(self.create_action("About", lambda: None))
        menu_bar.addMenu(help_menu)

    def create_action(self, name, slot):
        """
        Creates an action for the menu with the given name and connects it to a function.
        """
        action = QAction(name, self)
        action.triggered.connect(slot)
        return action

    def upload_image(self):
        """
        Opens a file dialog to allow the user to select an image, and loads it into the image processor.
        """
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.xpm *.jpg *.jpeg *.bmp *.gif)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.image_processor.load_image(file_path)
            self.apply_preset()

    def apply_preset(self):
        """
        Applies the selected preset effect to the image.
        """
        preset = self.preset_combo.currentText()
        self.image_processor.apply_preset(preset)

        if preset == "Film":
            self.reset_sliders()
        elif preset == "Orthochromatic":
            self.brightness_slider.setValue(100)
            self.contrast_slider.setValue(100)
            self.grain_slider.setValue(15)
            self.vignette_slider.setValue(60)
        elif preset == "Sepia":
            self.brightness_slider.setValue(100)
            self.contrast_slider.setValue(100)
            self.grain_slider.setValue(10)
            self.vignette_slider.setValue(30)
        elif preset == "Infrared":
            self.brightness_slider.setValue(100)
            self.contrast_slider.setValue(100)
            self.grain_slider.setValue(8)
            self.vignette_slider.setValue(20)

        self.update_image()

    def reset_sliders(self):
        """
        Resets all sliders to their default values.
        """
        self.brightness_slider.setValue(100)
        self.contrast_slider.setValue(100)
        self.grain_slider.setValue(10)
        self.vignette_slider.setValue(40)

    def update_image(self):
        """
        Updates the image by applying the current values from the sliders.
        """
        self.image_processor.brightness_factor = self.brightness_slider.value() / 100
        self.image_processor.contrast_factor = self.contrast_slider.value() / 100
        self.image_processor.grain_intensity = self.grain_slider.value()
        self.image_processor.vignette_strength = self.vignette_slider.value() / 100

        if self.image_processor.image:
            image = self.image_processor.adjust_brightness(self.image_processor.image)
            image = self.image_processor.adjust_contrast(image)
            image = self.image_processor.add_film_grain(image)
            image = self.image_processor.apply_vignette(image)
            self.display_image(image)

    def display_image(self, image):
        """
        Displays the processed image on the label in the UI.
        """
        image = image.convert("RGBA")
        img_data = image.tobytes("raw", "RGBA")
        qimg = QImage(img_data, image.width, image.height, QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimg)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size() - QSize(40, 40), Qt.KeepAspectRatio
        )
        self.image_label.setPixmap(scaled_pixmap)

    def download_image(self):
        """
        Opens a file dialog to allow the user to save the processed image to a selected file path.
        """
        processed_image = self.image_processor.get_processed_image()
        if processed_image:
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Image",
                "",
                "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*)",
            )
            if save_path:
                if not save_path.lower().endswith((".png", ".jpg", ".jpeg")):
                    save_path += ".png"
                processed_image = processed_image.resize(
                    self.image_processor.original_image.size, Image.Resampling.LANCZOS
                )
                processed_image.save(save_path)
