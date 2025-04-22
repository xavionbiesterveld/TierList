import tkinter as tk
import customtkinter as ctk
from customtkinter import CTkImage
from mal_request import MALClient
from PIL import Image
import os

class TierFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color):
        super().__init__(parent, fg_color=fg_color, corner_radius=0)

class TopFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)

        self.tier_frameS = TierFrame(self, fg_color="#f2f7fe")
        self.tier_frameS.grid(row=0, column=0, sticky="nsew")

        self.tier_frameA = TierFrame(self, fg_color="#98b1c8")
        self.tier_frameA.grid(row=1, column=0, sticky="nsew")

        self.tier_frameB = TierFrame(self, fg_color="#446d92")
        self.tier_frameB.grid(row=2, column=0, sticky="nsew")

        self.tier_frameC = TierFrame(self, fg_color="#24496b")
        self.tier_frameC.grid(row=3, column=0, sticky="nsew")

        self.grid_rowconfigure("all", weight=1)
        self.grid_columnconfigure(0, weight=1)


class BottomFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#071f35", corner_radius=0)

        MAX_PER_ROW = 10  # Set how many buttons per row
        row = 0
        col = 0

        for entry in os.scandir("images"):
            if entry.is_file():
                pil_image = Image.open(entry.path)
                image = CTkImage(pil_image, size=(106, 150))
                image_button = ctk.CTkButton(
                    self,
                    image=image,
                    command=lambda: print("Button clicked!"),
                    text="",
                    fg_color="#071f35",  # Use background color, not "transparent",
                    width=0
                )

                image_button.grid(row=row, column=col, pady=1, padx=1)
                col += 1

                # Move to the next row if MAX_PER_ROW is reached
                if col >= MAX_PER_ROW:
                    col = 0
                    row += 1

                self.grid_columnconfigure("all", weight=1)



class App(ctk.CTk):
    def __init__(self, mal_client):
        super().__init__()

        client = mal_client
        if client.is_valid_token():
            client.get_mal_list('xavion03')
            client.download_images()
        else:
            print("Invalid access token")

        # App Frame
        self.title("Tier List")
        self.geometry("1280x720")

        self.top_frame = TopFrame(self)
        self.top_frame.place(relx=0, rely=0, relwidth=1, relheight=0.7)


        self.bottom_frame = BottomFrame(self)
        self.bottom_frame.place(relx=0, rely=0.7, relwidth=1, relheight=0.3)


client = MALClient()
app = App(client)
app.mainloop()