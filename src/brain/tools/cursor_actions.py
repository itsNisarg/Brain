"""This module provides functions to perform various cursor actions
such as clicking, hovering, dragging, and scrolling
using the pyautogui library.
"""

import pyautogui
from agent_framework import tool

__all__ = [
    "mouse_position",
    "left_click",
    "right_click",
    "double_click",
    "move_hover",
    "drag_and_drop",
    "scroll_up",
    "scroll_down",
    "pause_mouse",
]


@tool
def mouse_position() -> tuple[int, int]:
    """Returns the current position of the mouse cursor as (x, y) coordinates.
    Returns:
        tuple: A tuple containing the x and y coordinates of the mouse cursor.
    """
    return pyautogui.position()


@tool
def left_click(x: int, y: int) -> None:
    """Performs a left click at the specified (x, y) coordinates.
    Args:
        x (int): The x-coordinate where the click should occur.
        y (int): The y-coordinate where the click should occur.
    Returns:
        None
    """
    pyautogui.click(x, y)


@tool
def right_click(x: int, y: int) -> None:
    """Performs a right click at the specified (x, y) coordinates.
    Args:
        x (int): The x-coordinate where the click should occur.
        y (int): The y-coordinate where the click should occur.
    Returns:
        None
    """
    pyautogui.rightClick(x, y)


@tool
def double_click(x: int, y: int) -> None:
    """Performs a double click at the specified (x, y) coordinates.
    Args:
        x (int): The x-coordinate where the click should occur.
        y (int): The y-coordinate where the click should occur.
    Returns:
        None
    """
    pyautogui.doubleClick(x, y)


@tool
def move_hover(x: int, y: int) -> None:
    """Moves the cursor to the specified (x, y) coordinates
    without clicking.
    Args:
        x (int): The x-coordinate where the cursor should move.
        y (int): The y-coordinate where the cursor should move.
    Returns:
        None
    """
    pyautogui.moveTo(x, y, duration=1)


@tool
def drag_and_drop(start_x: int, start_y: int, end_x: int, end_y: int) -> None:
    """Drags the cursor from the starting (x, y) coordinates
    to the ending (x, y) coordinates.
    Args:
        start_x (int): The starting x-coordinate.
        start_y (int): The starting y-coordinate.
        end_x (int): The ending x-coordinate.
        end_y (int): The ending y-coordinate.
    Returns:
        None
    """
    pyautogui.moveTo(start_x, start_y, 1)
    pyautogui.dragTo(end_x, end_y, duration=2)


@tool
def scroll_up(amount: int) -> None:
    """Scrolls up by the specified amount.
    Args:
        amount (int): The amount to scroll up.
    Returns:
        None
    """
    pyautogui.scroll(amount)


@tool
def scroll_down(amount: int) -> None:
    """Scrolls down by the specified amount.
    Args:
        amount (int): The amount to scroll down.
    Returns:
        None
    """
    pyautogui.scroll(-amount)


@tool
def pause_mouse(duration: int) -> None:
    """Pauses the mouse movement for the specified duration in seconds.
    Args:
        duration (int): The duration to pause in seconds.
    Returns:
        None
    """
    pyautogui.sleep(duration)


if __name__ == "__main__":
    move_hover(240, 1175)
    left_click(240, 1175)
