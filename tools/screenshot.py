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
    r = 10
    draw.ellipse([mouse_x - r, mouse_y - r, mouse_x + r, mouse_y + r],
                 outline="red", fill="red", width=3)
    draw.line([mouse_x - r, mouse_y, mouse_x + r, mouse_y],
              fill="white", width=2)
    draw.line([mouse_x, mouse_y - r, mouse_x, mouse_y + r],
              fill="white", width=2)

    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")

    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

    file_path = f"screenshots/{timestamp}_{filename}.png"
    print(f"Taking screenshot and saving to {file_path}")

    # Save the screenshot to the specified path
    screenshot.save(file_path)
    print(f"Screenshot saved to {file_path}")

    return file_path, screenshot, (mouse_x, mouse_y)


screenshot_tool = {
    "type": "function",
    "functions": {
        "name": "take_screenshot",
        "description": "Take a screenshot of the current screen and\
         save it to a specific location.",
    },
}
