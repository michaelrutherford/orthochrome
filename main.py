import sys
from PySide6.QtWidgets import (
    QApplication,
)
from ui import ImageEditorUI
from image_processor import ImageProcessor


class ImageProcessorApp:
    """
    Main application class that initializes and runs the image processor application.
    """
    def __init__(self):
        """
        Initializes the ImageProcessorApp with an image processor and UI.
        """
        self.image_processor = ImageProcessor()
        self.ui = ImageEditorUI(self.image_processor)

    def run(self):
        """
        Starts and shows the user interface of the application.
        """
        self.ui.show()


if __name__ == "__main__":
    """
    Entry point of the application that initializes the app and runs it.
    """
    app = QApplication(sys.argv)
    window = ImageProcessorApp() 
    window.run()
    sys.exit(app.exec())
