"""
This module provides functions to simulate keyboard actions.
It includes functions to press a key,
 type a string, and perform keyboard shortcuts."""

import pyautogui
from agent_framework import tool


__all__ = ["press", "typetext", "shortcut", "pause_keyboard", "keyboard_keylist", "keyboard_keyset", "typeset"]

keyboard_keylist = [
    "\t",
    "\n",
    "\r",
    " ",
    "!",
    '"',
    "#",
    "$",
    "%",
    "&",
    "'",
    "(",
    ")",
    "*",
    "+",
    ",",
    "-",
    ".",
    "/",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    ":",
    ";",
    "<",
    "=",
    ">",
    "?",
    "@",
    "[",
    "\\",
    "]",
    "^",
    "_",
    "`",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "{",
    "|",
    "}",
    "~",
    "accept",
    "add",
    "alt",
    "altleft",
    "altright",
    "apps",
    "backspace",
    "browserback",
    "browserfavorites",
    "browserforward",
    "browserhome",
    "browserrefresh",
    "browsersearch",
    "browserstop",
    "capslock",
    "clear",
    "convert",
    "ctrl",
    "ctrlleft",
    "ctrlright",
    "decimal",
    "del",
    "delete",
    "divide",
    "down",
    "end",
    "enter",
    "esc",
    "escape",
    "execute",
    "f1",
    "f10",
    "f11",
    "f12",
    "f13",
    "f14",
    "f15",
    "f16",
    "f17",
    "f18",
    "f19",
    "f2",
    "f20",
    "f21",
    "f22",
    "f23",
    "f24",
    "f3",
    "f4",
    "f5",
    "f6",
    "f7",
    "f8",
    "f9",
    "final",
    "fn",
    "hanguel",
    "hangul",
    "hanja",
    "help",
    "home",
    "insert",
    "junja",
    "kana",
    "kanji",
    "launchapp1",
    "launchapp2",
    "launchmail",
    "launchmediaselect",
    "left",
    "modechange",
    "multiply",
    "nexttrack",
    "nonconvert",
    "num0",
    "num1",
    "num2",
    "num3",
    "num4",
    "num5",
    "num6",
    "num7",
    "num8",
    "num9",
    "numlock",
    "pagedown",
    "pageup",
    "pause",
    "pgdn",
    "pgup",
    "playpause",
    "prevtrack",
    "print",
    "printscreen",
    "prntscrn",
    "prtsc",
    "prtscr",
    "return",
    "right",
    "scrolllock",
    "select",
    "separator",
    "shift",
    "shiftleft",
    "shiftright",
    "sleep",
    "space",
    "stop",
    "subtract",
    "tab",
    "up",
    "volumedown",
    "volumemute",
    "volumeup",
    "win",
    "winleft",
    "winright",
    "yen",
    "command",
    "option",
    "optionleft",
    "optionright",
]

keyboard_keyset = set(keyboard_keylist)
typeset = set(keyboard_keylist[:72])


@tool
def press(key: str) -> None:
    """
    Press a key on the keyboard.
    Args:
        key (str): The key to press.
        It can be a single character
         or a special key like "enter", "shift", etc.
    Returns:
        None
    """
    if key not in keyboard_keyset:
        raise ValueError(f"Key '{key}' is not a valid key.")
    pyautogui.press(key)


@tool
def typetext(text: str) -> None:
    """
    Type a string of text.
    Args:
        text (str): The text to type.
    Returns:
        None
    """
    for char in text:
        if char not in typeset:
            raise ValueError(f"Character '{char}' is not a valid key.")
    pyautogui.typewrite(text)


@tool
def shortcut(*keys: str) -> None:
    """Perform a keyboard shortcut by pressing multiple keys simultaneously.
    Args:
        *keys (str): The keys to press in the shortcut.
        Each key can be a single character or a special key
          like "ctrl", "alt", etc.
    Returns:
        None
    """
    if any(key not in keyboard_keyset for key in keys):
        invalid_keys = [key for key in keys if key not in keyboard_keyset]
        raise ValueError(f"Keys '{', '.join(invalid_keys)}'\
                          are not valid keys.")
    pyautogui.hotkey(*keys)


@tool
def pause_keyboard(duration: int) -> None:
    """Pauses the keyboard actions for the specified duration in seconds.
    Args:
        duration (int): The duration to pause in seconds.
    Returns:
        None
    """
    pyautogui.sleep(duration)


if __name__ == "__main__":
    print(typeset)
