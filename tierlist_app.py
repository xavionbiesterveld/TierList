import tkinter as tk
import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # App Frame
        self.geometry("1280x720")
        self.title("Tier List")



app = App()
app.mainloop()