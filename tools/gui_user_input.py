import customtkinter as ctk

class GUIUserInput(ctk.CTk):
    def __init__(self, title="Agent requires human input", text="Do you have a TODO App?", width=400, height=100):
        super().__init__()

        self.geometry(f"{width}x{height}")
        self.title(title)
        self.attributes("-topmost", True)

        # Configure grid: Row 1 (the textbox) will expand to fill space
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) 

        # 1. Header Label (Silver/White text)
        self.label = ctk.CTkLabel(
            self, 
            text=text, 
            text_color="#C5C9D6", 
            font=("Consolas", 16, "bold")
        )
        self.label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # 2. Text Area (Deep Navy with subtle border)
        self.textbox = ctk.CTkTextbox(
            self,
            fg_color="#FEFEFF",
            text_color="#000000",
            border_color="#233554",
            border_width=2,
            scrollbar_button_color="#233554",
            scrollbar_button_hover_color="#64FFDA",
            font=("Consolas", 13)
        )
        self.textbox.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.textbox.focus_set()

        # 3. Submit Button (Ocean Blue with Glow-like hover)
        self.button = ctk.CTkButton(
            self,
            text="Submit",
            fg_color="#005EB6",
            hover_color="#3BBBF7",
            text_color="white",
            font=("Consolas", 14, "bold"),
            corner_radius=8,
            height=40,
            command=self.submit
        )
        self.button.grid(row=2, column=0, padx=20, pady=20)

        self.user_input = None

    def submit(self):
        # Note: Textbox requires start and end indexes. "1.0" is start, "end-1c" removes trailing newline.
        self.user_input = self.textbox.get("1.0", "end-1c")
        self.destroy()

def get_input():
    app = GUIUserInput(width=500, height=250)
    app.mainloop()
    return app.user_input

# Testing it
if __name__ == "__main__":
    result = get_input()
    print(f"Captured Text:\n{result}")