import sys
from PySide6.QtWidgets import (
    QApplication,
)
from app import ImageProcessorApp


if __name__ == "__main__":
    """
    Entry point of the application that initializes the app and runs it.
    """
    app = QApplication(sys.argv)
    window = ImageProcessorApp()
    window.run()
    sys.exit(app.exec())
