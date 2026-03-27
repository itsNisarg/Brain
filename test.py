import asyncio
from concurrent.futures import ThreadPoolExecutor
import customtkinter as ctk

def quick_prompt():
    dialog = ctk.CTkInputDialog(text="Type something:", title="Modern Prompt")
    return dialog.get_input()

async def main():
    loop = asyncio.get_running_loop()
    
    # Run the blocking GUI in a separate thread
    print("Waiting for user...")
    user_input = await loop.run_in_executor(None, quick_prompt)
    
    print(f"Async loop continued! User said: {user_input}")

asyncio.run(main())