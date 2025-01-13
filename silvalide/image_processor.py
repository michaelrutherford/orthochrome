import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


class ImageProcessor:
    """
    A class to handle various image processing operations.
    """

    def __init__(self):
        """
        Initializes the image processor with default values for image attributes and processing parameters.
        """
        self.image = None
        self.original_image = None
        self.brightness_factor = 1.0
        self.contrast_factor = 1.0
        self.grain_intensity = 10
        self.vignette_strength = 0.8

    def load_image(self, file_path):
        """
        Loads an image from the specified file path, and resizes it to fit within the maximum size.
        """
        self.image = Image.open(file_path)
        self.original_image = self.image.copy()
        self.image = self.resize_image(self.image)

    def reset_image(self):
        """
        Resets the current image to the original image that was loaded.
        """
        self.image = self.original_image.copy()

    def resize_image(self, image, max_size=(800, 600)):
        """
        Resizes the given image to fit within the specified maximum size while maintaining aspect ratio.
        """
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image

    def adjust_brightness(self, image):
        """
        Adjusts the brightness of the given image based on the current brightness factor.
        """
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(self.brightness_factor)

    def adjust_contrast(self, image):
        """
        Adjusts the contrast of the given image based on the current contrast factor.
        """
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(self.contrast_factor)

    def add_film_grain(self, image):
        """
        Adds film grain noise to the image and applies a slight blur.
        """
        img_resized = self.resize_image(image)
        img_array = np.array(img_resized)
        noise = np.random.normal(
            scale=self.grain_intensity, size=img_array.shape[:2]
        ).astype(np.float32)
        noisy_image = img_array + np.stack([noise] * 3, axis=-1)
        noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
        noisy_image = Image.fromarray(noisy_image)
        return noisy_image.filter(ImageFilter.GaussianBlur(radius=0.5)).resize(
            image.size
        )

    def apply_vignette(self, image):
        """
        Applies a vignette effect to the image, darkening the edges and focusing the center.
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
        pixels[:, :, :3] = (
            pixels[:, :, :3] * vignette_factor[:, :, np.newaxis]
        ).astype(np.uint8)
        return Image.fromarray(pixels)

    def apply_preset(self, preset):
        """
        Applies a preset effect to the image.
        """
        self.reset_image()
        if preset == "Film":
            self.apply_film_effect()
        elif preset == "Orthochromatic":
            self.apply_orthochromatic()
        elif preset == "Sepia":
            self.apply_sepia()
        elif preset == "Infrared":
            self.apply_infrared()

    def apply_film_effect(self):
        """
        Applies a film-like effect to the image, enhancing color and contrast.
        """
        if self.image:
            img = self.image.convert("RGB")
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(0.9)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.1)
            r, g, b = img.split()
            r = r.point(lambda p: min(p + 20, 255))
            g = g.point(lambda p: min(p + 10, 255))
            b = b.point(lambda p: max(p - 10, 0))
            img = Image.merge("RGB", (r, g, b))
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(0.9)
            self.image = img

    def apply_orthochromatic(self):
        """
        Applies an orthochromatic effect to the image, which adds a cyan filter before subtracting color.
        """
        if self.image:
            img = np.array(self.image.convert("RGB"))
            fixed_shift = np.array([-90, 0, 20])
            img = np.clip(img + fixed_shift, 0, 255).astype(np.uint8)
            self.image = Image.fromarray(img).convert("L").convert("RGB")

    def apply_sepia(self):
        """
        Applies a sepia tone effect to the image, giving it a warm, vintage appearance.
        """
        if self.image:
            img = np.array(self.image.convert("RGB"))
            sepia_filter = np.array(
                [[0.393, 0.769, 0.189], [0.349, 0.686, 0.168], [0.272, 0.534, 0.131]]
            )
            sepia_img = img @ sepia_filter.T
            self.image = Image.fromarray(np.clip(sepia_img, 0, 255).astype(np.uint8))

    def apply_infrared(self):
        """
        Applies an infrared-like effect to the image, adding a magenta tint to the greens.
        """
        if self.image:
            img = np.array(self.image.convert("RGB")).astype(float)

            r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
            total = r + g + b
            total = np.where(total == 0, 1, total)

            g_ratio = g / total
            r_ratio = r / total
            b_ratio = b / total

            green_mask = (g_ratio > 0.25) & (g_ratio > r_ratio) & (g_ratio > b_ratio)

            strength = np.clip((g_ratio - 0.3) * 4, 0, 1)
            strength = strength[:, :, np.newaxis]

            magenta_version = img.copy()
            magenta_version[:, :, 0] = np.clip(img[:, :, 1] * 1.5, 0, 255)
            magenta_version[:, :, 1] = np.clip(img[:, :, 1] * 0.4, 0, 255)
            magenta_version[:, :, 2] = np.clip(img[:, :, 1] * 1.3, 0, 255)

            result = img * (1 - strength) + magenta_version * strength

            tint = np.zeros_like(img)
            tint[green_mask] = [50, 0, 30]
            result = np.clip(result + tint * strength, 0, 255)
            result = np.clip(result * 1.1, 0, 255)

            self.image = Image.fromarray(result.astype(np.uint8))

    def get_processed_image(self):
        """
        Returns the processed image after applying effects.
        """
        if self.image:
            image = self.adjust_brightness(self.image)
            image = self.adjust_contrast(image)
            image = self.add_film_grain(image)
            image = self.apply_vignette(image)
            return image
        return None
