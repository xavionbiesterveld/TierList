import tkinter as tk
import customtkinter as ctk
from customtkinter import CTkImage
from mal_request import MALClient
from PIL import Image
from logger import get_logger
import os
import re

class TierImage():
    pass

class TierFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color, tier):
        super().__init__(parent, fg_color=fg_color, corner_radius=0)

        self.tier_label = ctk.CTkLabel(self, text=tier, fg_color="#4482b8", font=("Arial", 22))
        self.tier_label.configure(
            compound="left",
            text_color="white"
        )
        self.tier_label.place(relx=0, rely=0, relwidth=0.1, relheight=1)

class TopFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)

        self.tier_frameS = TierFrame(self, fg_color="#f2f7fe", tier="S")
        self.tier_frameS.grid(row=0, column=0, sticky="nsew")

        self.tier_frameA = TierFrame(self, fg_color="#98b1c8", tier="A")
        self.tier_frameA.grid(row=1, column=0, sticky="nsew")

        self.tier_frameB = TierFrame(self, fg_color="#446d92", tier="B")
        self.tier_frameB.grid(row=2, column=0, sticky="nsew")

        self.tier_frameC = TierFrame(self, fg_color="#24496b", tier="C")
        self.tier_frameC.grid(row=3, column=0, sticky="nsew")

        self.grid_rowconfigure("all", weight=1)
        self.grid_columnconfigure(0, weight=1)


class BottomFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, mal_client):
        super().__init__(parent, fg_color="#071f35", corner_radius=0)

        self.client = mal_client

        def show_popup(info):
            popup = ctk.CTkToplevel(self)
            popup.title("Anime Info")
            popup.geometry("850x400")

            popup.transient(self.master)  # Set the popup on top of the main app
            popup.grab_set()  # Make the popup modal

            popup.lift()  # Bring popup to front
            popup.focus()  # Focus on the popup

            name_label = ctk.CTkLabel(popup, text=info['title'], font=("Arial", 22), fg_color="#f4acb7")
            name_label.configure(
                compound="left",
                text_color="#9d8189"
            )
            name_label.place(relx=0, rely=0, relwidth=1, relheight=0.1)

            openings_scrollable = ctk.CTkScrollableFrame(popup, fg_color="#ffcad4", corner_radius=0)
            openings_scrollable.place(relx=0, rely=0.1, relwidth=1, relheight=0.2)
            openings_scrollable.grid_columnconfigure(0, weight=1)
            openings_scrollable.grid_rowconfigure("all", weight=1)
            i = 0
            for opening in info['opening_themes']:
                opening_label = ctk.CTkLabel(openings_scrollable, text=opening['text'], font=("Arial", 16))
                opening_label.configure(
                    compound="center",
                    text_color="#9d8189"
                )
                opening_label.grid(row=i, column=0)
                i += 1


            form_frame = ctk.CTkFrame(popup, fg_color="#ffe5d9", corner_radius=0)
            form_frame.place(relx=0, rely=0.3, relwidth=1, relheight=0.7)

        def edit_opening_s(opening_text):
            for opening in opening_text:
               opening['text'] = re.sub(r'#\d: |\([^()]*\)', '', opening['text'])

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
                    text="",
                    fg_color="#071f35",  # Use background color, not "transparent",
                    width=0,
                    hover_color="#071f35"
                )
                image_button.info_dict = self.client.get_info(entry.name.replace(".jpg", ""))
                edit_opening_s(image_button.info_dict['opening_themes'])
                image_button.configure(command=lambda info=image_button.info_dict: show_popup(info))

                image_button.grid(row=row, column=col, pady=1, padx=1)
                col += 1

                # Move to the next row if MAX_PER_ROW is reached
                if col >= MAX_PER_ROW:
                    col = 0
                    row += 1

                self.grid_columnconfigure("all", weight=1)



class App(ctk.CTk):
    def __init__(self, mal_client, logger):
        super().__init__()

        self.logger = logger
        client = mal_client
        if client.is_valid_token():
            client.get_mal_list()
            client.download_images()
            client.get_anime_info()
            client.cache_info()
            self.logger.info("MAL Initialization Finished")
        else:
            self.logger.warning("Invalid access token")

        # App Frame
        self.title("Tier List")
        self.geometry("1280x720")

        self.top_frame = TopFrame(self)
        self.top_frame.place(relx=0, rely=0, relwidth=1, relheight=0.7)


        self.bottom_frame = BottomFrame(self, client)
        self.bottom_frame.place(relx=0, rely=0.7, relwidth=1, relheight=0.3)


client = MALClient()
logger = get_logger(__name__)
app = App(client, logger)
app.mainloop()