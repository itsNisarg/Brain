"""Tool to take screenshots of the current screen and
save them to a specific location."""

import os
from datetime import datetime, timezone

from PIL import Image, ImageDraw
import pyautogui


def take_screenshot(filename: str) -> tuple[str, Image.Image, tuple[int, int]]:
    """Take a screenshot of the current screen and
      save it to the specified path with timestamp.

    Args:
        filename (str): The filename to save the screenshot to.
        The timestamp will be prepended to the filename.

    Returns:
        str: The path of the saved screenshot file.
        Image.Image: The captured image.
        tuple: A tuple containing the x and y coordinates of the mouse cursor
          at the time of the screenshot.

    Example:
        take_screenshot("screenshot")
    """
    screenshot = pyautogui.screenshot()
    mouse_x, mouse_y = pyautogui.position()

    # Draw a visible crosshair/dot at cursor position
    draw = ImageDraw.Draw(screenshot)
    r = 15
    # draw.ellipse([max(mouse_x - r, 0), max(mouse_y - r, 0),
    #               min(mouse_x + r, screenshot.width),
    #               min(mouse_y + r, screenshot.height)],
    #              outline="black", fill="white", width=5)

    draw.ellipse(
        [
            max(mouse_x - r, 0),
            max(mouse_y - r, 0),
            min(mouse_x + r, screenshot.width),
            min(mouse_y + r, screenshot.height),
        ],
        outline="white",
        fill="black",
        width=7,
    )

    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")

    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

    file_path = f"screenshots/{timestamp}_{filename}.png"
    print(f"Taking screenshot and saving to {file_path}")

    # Save the screenshot to the specified path
    screenshot.save(file_path)
    print(f"Screenshot saved to {file_path}")

    return file_path, screenshot, (mouse_x, mouse_y)


def draw_grid(image_path: "str | Image.Image", cell_size: int = 100) -> Image.Image:
    """Draw a grid on the given image."""
    if isinstance(image_path, str):
        image = Image.open(image_path)
    else:
        image = image_path
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # Vertical lines
    for x in range(0, width + 1, cell_size):
        draw.line([(x, 0), (x, height)], fill="red", width=1)

    # Horizontal lines
    for y in range(0, height + 1, cell_size):
        draw.line([(0, y), (width, y)], fill="red", width=1)

    return image

