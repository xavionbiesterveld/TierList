import tkinter as tk
import customtkinter as ctk
from customtkinter import CTkImage
from mal_request import MALClient
from PIL import Image
from logger import get_logger
from db_ops import db
import os
import re

db = db()
client = MALClient()
logger = get_logger(__name__)

class TopButtonFrame(ctk.CTkFrame):
    def __init__(self, parent, tier, fgcolor):
        super().__init__(parent, fg_color=fgcolor, corner_radius=0)
        self.tier = tier
        self.fgcolor = fgcolor

        self.canvas = tk.Canvas(self, highlightthickness=0, height=180, bg=fgcolor)  # height as needed
        self.scrollbar = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.inner_frame = ctk.CTkFrame(self.canvas, fg_color=fgcolor, corner_radius=0)

        self.inner_frame_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="top", fill="both", expand=True)
        self.scrollbar.pack(side="bottom", fill="x")

        # Configure resizing
        self.inner_frame.bind("<Configure>", self._on_frame_configure)

        self.create_image_buttons(tier, fgcolor)

    def _on_frame_configure(self, event):
        # Update scrollregion to match the true size of the inner_frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_image_buttons(self, tier, color):
        # Remove previous widgets
        for widget in self.inner_frame.winfo_children():
            if widget != getattr(self, 'tier_label', None):
                widget.destroy()

        results = db.find_tier(tier)
        if not results:
            return

        # Sort by sum of indices 10-13, descending
        results = sorted(results, key=lambda item: sum(item[10:14]), reverse=True)

        for col, result in enumerate(results):
            pil_image = Image.open(f"images/{result[3]}.jpg")
            image = CTkImage(pil_image, size=(106, 150))
            image_button = ctk.CTkButton(
                self.inner_frame,
                image=image,
                text="",
                fg_color=color,
                width=0,
                hover_color=color
            )
            image_button.info = result
            image_button.configure(command=lambda info=image_button.info:
            logger.info(f"Name: {info[1]}; Total Score: {sum(info[10:14])}; Music Score: {info[10]}; Visual Score: {info[11]}; Narrative Score: {info[12]}; Memorability Score: {info[13]}"))

            image_button.grid(row=0, column=col, pady=1, padx=1, sticky="n")



class TierFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color, tier):
        super().__init__(parent, fg_color=fg_color, corner_radius=0)

        self.tier_label = ctk.CTkLabel(
            self,
            text=tier,
            fg_color="#4482b8",
            font=("Arial", 22),
            text_color="white"
        )
        self.tier_label.place(relx=0, rely=0, relwidth=0.1, relheight=1)

        self.button_frame = TopButtonFrame(self, tier, fg_color)
        self.button_frame.place(relx=0.1, rely=0, relwidth=0.9, relheight=1)


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
    def __init__(self, parent):
        super().__init__(parent, fg_color="#071f35", corner_radius=0)


        def show_popup(info, refresh):
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

            def show_form(form_frame, opening_text, info, popup):
                for widget in form_frame.winfo_children():
                    widget.destroy()

                # 2 columns, 5 rows (labels, optionmenus, submit)
                for i in range(4):  # rows for labels/menus
                    form_frame.grid_rowconfigure(i, weight=1)
                for i in range(2):
                    form_frame.grid_columnconfigure(i, weight=1)
                form_frame.grid_rowconfigure(4, weight=0)  # submit row

                # Visual
                visual_label = ctk.CTkLabel(form_frame, text="Visual Score", fg_color="#ffe5d9", text_color="#9d8189")
                visual_label.grid(row=0, column=0, sticky="s", padx=5, pady=(10, 2))
                visual_score_var = tk.StringVar(value="1")
                visual_entry = ctk.CTkOptionMenu(form_frame, variable=visual_score_var, values=[str(i) for i in range(1, 11)],
                                                 fg_color="#ffc2d1", dropdown_fg_color="#ffc2d1", dropdown_text_color="#9d8189",
                                                       text_color="#9d8189", button_color="#ff8fab", button_hover_color="#ff8fab")
                visual_entry.grid(row=1, column=0, sticky="n", padx=5, pady=(2, 10))

                # Music
                music_label = ctk.CTkLabel(form_frame, text="Music Score", fg_color="#ffe5d9", text_color="#9d8189")
                music_label.grid(row=0, column=1, sticky="s", padx=5, pady=(10, 2))
                music_score_var = tk.StringVar(value="1")
                music_entry = ctk.CTkOptionMenu(form_frame, variable=music_score_var, values=[str(i) for i in range(1, 11)],
                                                fg_color="#ffc2d1", dropdown_fg_color="#ffc2d1", dropdown_text_color="#9d8189",
                                                       text_color="#9d8189", button_color="#ff8fab", button_hover_color="#ff8fab")
                music_entry.grid(row=1, column=1, sticky="n", padx=5, pady=(2, 10))

                # Narrative
                narrative_label = ctk.CTkLabel(form_frame, text="Narrative Score", fg_color="#ffe5d9", text_color="#9d8189")
                narrative_label.grid(row=2, column=0, sticky="s", padx=5, pady=(10, 2))
                narrative_score_var = tk.StringVar(value="1")
                narrative_entry = ctk.CTkOptionMenu(form_frame, variable=narrative_score_var, values=[str(i) for i in range(1, 11)],
                                                    fg_color="#ffc2d1", dropdown_fg_color="#ffc2d1", dropdown_text_color="#9d8189",
                                                     text_color="#9d8189", button_color="#ff8fab", button_hover_color="#ff8fab")
                narrative_entry.grid(row=3, column=0, sticky="n", padx=5, pady=(2, 10))

                # Memorability
                memorability_label = ctk.CTkLabel(form_frame, text="Memorability Score", fg_color="#ffe5d9", text_color="#9d8189")
                memorability_label.grid(row=2, column=1, sticky="s", padx=5, pady=(10, 2))
                memorability_score_var = tk.StringVar(value="1")
                memorability_entry = ctk.CTkOptionMenu(form_frame, variable=memorability_score_var, values=[str(i) for i in range(1, 11)],
                                                       fg_color="#ffc2d1", dropdown_fg_color="#ffc2d1", dropdown_text_color="#9d8189",
                                                       text_color="#9d8189", button_color="#ff8fab", button_hover_color="#ff8fab")
                memorability_entry.grid(row=3, column=1, sticky="n", padx=5, pady=(2, 10))
                
                def on_submit():
                    scores = [int(visual_score_var.get()), int(music_score_var.get()), int(narrative_score_var.get()), int(memorability_score_var.get())]
                    db.insert_data(opening_text, info, scores)
                    popup.destroy()
                    refresh()

                submit_btn = ctk.CTkButton(form_frame, text="Submit", command=on_submit, fg_color='#ffb3c6', hover_color='#ff8fab', text_color="#9d8189")
                submit_btn.grid(row=4, column=0, columnspan=2, pady=(15, 5))

            row_num = 0
            for opening in info['opening_themes']:
                opening_button = ctk.CTkButton(
                    openings_scrollable,
                    text=opening['text'],
                    font=("Arial", 16),
                    text_color="#9d8189",
                    fg_color="#ffcad4",
                    hover_color="blue"
                )
                # Assign the correct command
                opening_button.configure(command=lambda o=opening: show_form(form_frame, o, info, popup))
                opening_button.grid(row=row_num, column=0)
                row_num += 1

            form_frame = ctk.CTkFrame(popup, fg_color="#ffe5d9", corner_radius=0)
            form_frame.place(relx=0, rely=0.3, relwidth=1, relheight=0.7)

        def refresh_images(self):
            create_image_buttons(self)
            app.top_frame.tier_frameS.button_frame.create_image_buttons("S",
                                                                        app.top_frame.tier_frameS.button_frame.fgcolor)
            app.top_frame.tier_frameA.button_frame.create_image_buttons("A",
                                                                        app.top_frame.tier_frameA.button_frame.fgcolor)
            app.top_frame.tier_frameB.button_frame.create_image_buttons("B",
                                                                        app.top_frame.tier_frameB.button_frame.fgcolor)
            app.top_frame.tier_frameC.button_frame.create_image_buttons("C",
                                                                        app.top_frame.tier_frameC.button_frame.fgcolor)

        def create_image_buttons(self):
            for widget in self.winfo_children():
                widget.destroy()

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
                    image_button.info_dict = client.get_info(entry.name.replace(".jpg", ""))
                    try:
                        edit_opening_s(image_button.info_dict['opening_themes'])
                    except KeyError as e:
                        logger.error(f"KeyError on {entry.name.replace(".jpg", "")}: {e}; Moving to next image")
                        continue


                    #stop condition here
                    filtered_openings = [opening for opening in image_button.info_dict['opening_themes']
                                         if not db.find_if_exists(opening['text'])]
                    if not filtered_openings:
                        continue
                    image_button.info_dict['opening_themes'] = filtered_openings

                    image_button.configure(command=lambda info=image_button.info_dict: show_popup(info, lambda: refresh_images(self)))

                    image_button.grid(row=row, column=col, pady=1, padx=1)
                    col += 1

                    # Move to the next row if MAX_PER_ROW is reached
                    if col >= MAX_PER_ROW:
                        col = 0
                        row += 1

                    self.grid_columnconfigure("all", weight=1)

        create_image_buttons(self)



class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # App Frame
        self.title("Tier List")
        self.geometry("1280x880")

        self.top_frame = TopFrame(self)
        self.top_frame.place(relx=0, rely=0, relwidth=1, relheight=0.82)


        self.bottom_frame = BottomFrame(self)
        self.bottom_frame.place(relx=0, rely=0.82, relwidth=1, relheight=0.18)



if client.is_valid_token():
    client.get_mal_list()
    client.download_images()
    client.get_anime_info()
    client.cache_info()
    logger.info("MAL Initialization Finished")
else:
    logger.warning("Invalid access token")
app = App()
app.mainloop()