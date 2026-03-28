import customtkinter as ctk
import asyncio
import logging

logger = logging.getLogger(__name__)


class GUIUserInput(ctk.CTk):
    def __init__(
        self,
        title="Agent requires human input",
        text="Do you have a TODO App?",
        width=400,
        height=100,
    ):
        super().__init__()

        self.geometry(f"{width}x{height}")
        self.title(title)
        self.attributes("-topmost", True)

        # Handle window closure gracefully (the "X" button)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.is_running = True

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.label = ctk.CTkLabel(
            self, text=text, text_color="#C5C9D6", font=("Consolas", 16, "bold")
        )
        self.label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.textbox = ctk.CTkTextbox(
            self,
            fg_color="#FEFEFF",
            text_color="#000000",
            border_color="#233554",
            border_width=2,
            scrollbar_button_color="#233554",
            scrollbar_button_hover_color="#64FFDA",
            font=("Consolas", 13),
        )
        self.textbox.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.textbox.focus_set()

        self.button = ctk.CTkButton(
            self,
            text="Submit",
            fg_color="#005EB6",
            hover_color="#3BBBF7",
            text_color="white",
            font=("Consolas", 14, "bold"),
            corner_radius=8,
            height=40,
            command=self.submit,
        )
        self.button.grid(row=2, column=0, padx=20, pady=20)

        self.user_input = None

    def submit(self):
        self.user_input = self.textbox.get("1.0", "end-1c")
        self.is_running = False

    def on_close(self):
        self.is_running = False


async def get_input(text: str = "Do you have a TODO App?") -> str | None:

    logger.info("Waiting for user...")

    app = GUIUserInput(text=text, width=400, height=200)

    # Process GUI events and yield control to user's event loop
    while app.is_running:
        try:
            app.update()
        except Exception:
            break
        await asyncio.sleep(0.02)  # ~50 FPS refresh rate

    result = app.user_input

    try:
        app.destroy()
    except Exception:
        pass  # Ignore any late-firing Tcl errors during final teardown

    logger.info(f"User input received: {result}")

    return result


# Testing it
if __name__ == "__main__":

    async def main():
        user_input = await get_input("Please enter your response:")
        print(f"Async loop continued! User said: {user_input}")

    asyncio.run(main())
