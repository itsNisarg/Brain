"""Tool to take screenshots of the current screen and
save them."""

import logging
import os
from datetime import datetime, timezone
from io import BytesIO

import pyautogui
from agent_framework import tool
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)


def convert_image_to_bytes(image: Image.Image) -> bytes:
    """Convert a PIL Image to bytes.

    Args:
        image (Image.Image): The PIL Image to convert.

    Returns:
        bytes: The image data in bytes format.
    """
    logger.info("Converting image to bytes...")
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()


@tool
def take_screenshot(
    folder: str, grid_size: int = 100
) -> tuple[bytes, bytes, tuple[int, int], str]:
    """Take a screenshot of the current screen, draw a crosshair at the mouse position,
    overlay a grid, and save the screenshot to a specified folder.

    Args:
        folder (str): The name of the folder to save the screenshot in.
        grid_size (int, optional): The size of the grid squares in pixels. Defaults to 100.

    Returns:
        tuple[bytes, bytes, tuple[int, int], str]: A tuple containing the screenshot bytes, grid screenshot bytes,
        mouse position as (x, y), and the file path of the saved screenshot.

    Example:
        screenshot_bytes, grid_screenshot_bytes, mouse_position, file_path = take_screenshot("session_20240601_120000")
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

    # Create a grid overlay on the screenshot
    grid_screenshot = screenshot.copy()
    width, height = grid_screenshot.size
    grid_draw = ImageDraw.Draw(grid_screenshot)
    # Vertical lines
    for x in range(0, width + 1, grid_size):
        grid_draw.line([(x, 0), (x, height)], fill="red", width=1)

    # Horizontal lines
    for y in range(0, height + 1, grid_size):
        grid_draw.line([(0, y), (width, y)], fill="red", width=1)

    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")

    if not os.path.exists(f"interactions/sessions/{folder}/screenshots"):
        os.makedirs(f"interactions/sessions/{folder}/screenshots")

    file_path = f"interactions/sessions/{folder}/screenshots/{timestamp}.png"
    # Save the screenshot to the specified path
    logger.info(f"Taking screenshot and saving to {file_path}")
    screenshot.save(file_path)

    logger.info(
        f"Returning screenshot path: {file_path}, mouse position: ({mouse_x}, {mouse_y})"
    )

    return (
        convert_image_to_bytes(screenshot),
        convert_image_to_bytes(grid_screenshot),
        (mouse_x, mouse_y),
        file_path,
    )


if __name__ == "__main__":
    screenshot_bytes, grid_screenshot_bytes, mouse_position, file_path = (
        take_screenshot("session_20240601_120000")
    )
    print(f"Screenshot saved to: {file_path}, Mouse position: {mouse_position}")
    print(
        f"Screenshot bytes length: {len(screenshot_bytes)}, Grid screenshot bytes length: {len(grid_screenshot_bytes)}"
    )
