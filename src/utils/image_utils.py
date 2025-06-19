# src/utils/image_utils.py

from PIL import Image, ImageTk, ImageDraw # Import necessary PIL modules

# No need to import config here unless a function uses a config value directly without it being passed in.
# The create_circular_image function takes the path as an argument, which comes from config in gui.app.


def create_circular_image(image_path: str, size: tuple[int, int]) -> Image.Image:
    """
    Opens an image, resizes it, and applies a circular mask.

    Args:
        image_path: The file path to the image.
        size: A tuple (width, height) for the desired output size.

    Returns:
        A PIL Image object with the circular mask applied.

    Raises:
        FileNotFoundError: If the image_path does not exist.
        IOError: If the image cannot be opened or read.
        Exception: For other potential issues during processing.
    """
    # Image.open can raise FileNotFoundError or IOError
    image = Image.open(image_path).resize(size)

    # Create a mask image (grayscale) with the same size as the target
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)

    # Draw a white ellipse (circle in this case) on the mask
    # The ellipse covers the entire image area (0,0 to size[0], size[1])
    draw.ellipse((0, 0, size[0], size[1]), fill=255)

    # Create a new RGBA image where the original image will be pasted with the mask
    circular_image = Image.new("RGBA", size)

    # Paste the original image onto the new RGBA image, using the mask
    # The mask determines the transparency (where the mask is 255, the image is opaque; where 0, it's transparent)
    circular_image.paste(image, (0, 0), mask=mask)

    return circular_image

# You could add other image-related utility functions here in the future.
# For example:
# def resize_image(image_path, size): ...
# def apply_grayscale_filter(image): ...