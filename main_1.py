import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from typing import Dict, Set, Optional, List
import webbrowser
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


ProvinceName = str
LanguageCode = str
FeatureName = str
FilePath = str
ProvinceSet = Set[ProvinceName]
LanguageDict = Dict[LanguageCode, ProvinceSet]
NameDict = Dict[LanguageCode, str]
LayerDict = Dict[ProvinceName, FilePath]
PhotoImageDict = Dict[ProvinceName, ImageTk.PhotoImage]
CanvasItemDict = Dict[ProvinceName, int]
BooleanVarDict = Dict[LanguageCode, tk.BooleanVar]
FeatureDict = Dict[FeatureName, Set[LanguageCode]]
FeatureBoolVarDict = Dict[FeatureName, tk.BooleanVar]
FeatureDetailDict = Dict[FeatureName, Dict[str, str]]
PopulationDict = Dict[LanguageCode, int]


BACKGROUND_FILENAME = "./map/background.png"

with Image.open(BACKGROUND_FILENAME) as img:
    IMAGE_WIDTH, IMAGE_HEIGHT = img.size


class LanguageMapApp(tk.Tk):
    """
    A Tkinter application to display language distribution maps based on province layers.

    Allows users to select languages individually or by feature groups (intersection logic),
    and view the corresponding provinces highlighted on a base map. Includes options
    to view province/feature details (with web links, population chart) and deselect all.
    Clears languages when no features are selected. Info popups resize automatically.
    Control frame is wider. Assumes Matplotlib is installed.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the application window, load data, and set up widgets.
        """
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Language Distribution Map Viewer")

        self.languages: LanguageDict = {
            "CMN": {
                "Beijing",
                "Hebei",
                "Tianjin",
                "Liaoning",
                "Jilin",
                "Heilongjiang",
                "Shandong",
                "Henan",
                "Ningxia",
                "Gansu",
                "Xinjiang",
                "Sichuan",
                "Chongqing",
                "Guizhou",
                "Hubei",
                "Jiangsu",
                "Guangxi",
                "Shaanxi",
                "Anhui",
            },
            "WUU": {"Shanghai", "Jiangsu", "Zhejiang", "Anhui", "Yunnan"},
            "GAN": {"Jiangxi", "Anhui"},
            "MIN": {"Fujian", "Guangdong", "Hainan"},
            "YUE": {"Guangdong", "Guangxi"},
            "HSN": {"Hunan"},
            "HAK": {"Guangdong", "Guangxi", "Fujian", "Jiangxi"},
            "CJY": {"Shanxi"},
        }
        self.language_names: NameDict = {
            "CMN": "Mandarin",
            "WUU": "Wu",
            "GAN": "Gan",
            "MIN": "Min",
            "YUE": "Yue (Cantonese)",
            "HSN": "Xiang (Hunanese)",
            "HAK": "Hakka",
            "CJY": "Jin (Jinyu)",
        }
        self.lang_features: FeatureDict = {
            "No Audible Release": {"WUU", "YUE", "GAN", "MIN", "HAK"},
            "Voiced Consonants": {"MIN", "WUU", "HSN"},
            "Literary and colloquial readings (strict)": {
                "WUU",
                "YUE",
                "GAN",
                "MIN",
                "HSN",
                "HAK",
                "CJY",
            },
            "Reduced Diphthong": {"WUU"},
            "No-Palatalization": {"WUU", "MIN", "YUE", "HAK"},
            "Post-Verb Adv.": {"YUE"},
            "Post-Noun Adj.": {"YUE", "MIN"},
        }

        self.language_populations: PopulationDict = {
            "CMN": 990,
            "WUU": 80,
            "GAN": 23,
            "MIN": 75,
            "YUE": 85,
            "HSN": 38,
            "HAK": 47,
            "CJY": 48,
        }

        feature_details_path = "./feature_details.json"

        with open(feature_details_path, "r", encoding="utf-8") as f:
            self.feature_details: FeatureDetailDict = json.load(f)

        self.all_provinces: ProvinceSet = (
            set().union(*self.languages.values()) if self.languages else set()
        )
        self.layer_filenames: LayerDict = {
            province: f"./map/{province}.png" for province in self.all_provinces
        }

        self.province_layer_images: PhotoImageDict = {}
        self.province_canvas_items: CanvasItemDict = {}
        self.language_vars: BooleanVarDict = {}
        self.feature_vars: FeatureBoolVarDict = {}
        self.bg_photo_image: Optional[ImageTk.PhotoImage] = None

        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            main_frame, width=IMAGE_WIDTH, height=IMAGE_HEIGHT, bg="white"
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        controls_frame_outer = tk.Frame(main_frame, width=300)
        controls_frame_outer.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        controls_frame_outer.pack_propagate(False)

        controls_canvas = tk.Canvas(controls_frame_outer, borderwidth=0)
        controls_frame_inner = tk.Frame(controls_canvas)
        scrollbar = tk.Scrollbar(
            controls_frame_outer, orient="vertical", command=controls_canvas.yview
        )
        controls_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        controls_canvas.pack(side="left", fill="both", expand=True)

        controls_canvas_window = controls_canvas.create_window(
            (0, 0), window=controls_frame_inner, anchor="nw"
        )

        controls_frame_inner.bind(
            "<Configure>",
            lambda e: controls_canvas.configure(
                scrollregion=controls_canvas.bbox("all")
            ),
        )

        controls_canvas.bind(
            "<Configure>",
            lambda e: controls_canvas.itemconfig(controls_canvas_window, width=e.width),
        )

        self.load_background()
        self.load_province_layers()
        self.create_controls(controls_frame_inner)
        self.update_map_display()

    def load_image(
        self, filepath: FilePath, item_name: str
    ) -> Optional[ImageTk.PhotoImage]:
        """
        Loads an image using Pillow, converts to RGBA, resizes if necessary,
        and returns a PhotoImage object. Assumes file exists and loads.
        """
        img = Image.open(filepath)
        img = img.convert("RGBA")
        if img.size != (IMAGE_WIDTH, IMAGE_HEIGHT):
            img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS)

        photo_image = ImageTk.PhotoImage(img)
        return photo_image

    def load_background(self) -> None:
        """
        Loads the background image and places it on the canvas.
        Stores the PhotoImage in self.bg_photo_image to prevent garbage collection.
        """
        self.bg_photo_image = self.load_image(BACKGROUND_FILENAME, "background")
        self.canvas.create_image(
            0, 0, anchor="nw", image=self.bg_photo_image, tags="background"
        )

    def load_province_layers(self) -> None:
        """
        Loads all province layer images specified in self.layer_filenames,
        stores the PhotoImage objects in self.province_layer_images,
        and places them hidden on the canvas, storing item IDs in
        self.province_canvas_items. Assumes all layers load correctly.
        """
        for province, filename in self.layer_filenames.items():
            photo_img = self.load_image(filename, province)
            self.province_layer_images[province] = photo_img
            item_id = self.canvas.create_image(
                0,
                0,
                anchor="nw",
                image=photo_img,
                state="hidden",
                tags=("layer", province),
            )
            self.province_canvas_items[province] = item_id

    def create_controls(self, parent_frame: tk.Frame) -> None:
        """
        Creates all control widgets (language selectors, feature selectors, buttons)
        within the provided parent frame using standard tk widgets.
        """
        tk.Label(parent_frame, text="Languages:", font="-weight bold").pack(
            pady=(10, 2), anchor="w", padx=10
        )

        lang_rows_frame = tk.Frame(parent_frame)
        lang_rows_frame.pack(fill="x", expand=True, anchor="w", padx=10)
        lang_rows_frame.columnconfigure(0, weight=1)

        sorted_language_codes = sorted(self.languages.keys())

        for i, lang_code in enumerate(sorted_language_codes):
            display_name = self.language_names.get(lang_code, lang_code)
            var = tk.BooleanVar(value=False)
            self.language_vars[lang_code] = var

            chk = tk.Checkbutton(
                lang_rows_frame,
                text=display_name,
                variable=var,
                anchor="w",
                command=self.update_map_display,
            )
            chk.grid(row=i, column=0, sticky="w", padx=(5, 2), pady=1)

            info_button = tk.Button(
                lang_rows_frame,
                text="?",
                width=1,
                command=lambda code=lang_code: self.show_province_info(code),
            )
            info_button.grid(row=i, column=1, sticky="e", padx=(2, 5), pady=1)

        if self.lang_features:
            tk.Label(
                parent_frame, text="Features (Intersection):", font="-weight bold"
            ).pack(pady=(10, 2), anchor="w", padx=10)

            feature_rows_frame = tk.Frame(parent_frame)
            feature_rows_frame.pack(fill="x", expand=True, anchor="w", padx=10)
            feature_rows_frame.columnconfigure(0, weight=1)

            sorted_feature_names = sorted(self.lang_features.keys())

            for i, feature_name in enumerate(sorted_feature_names):
                var = tk.BooleanVar(value=False)
                self.feature_vars[feature_name] = var

                chk = tk.Checkbutton(
                    feature_rows_frame,
                    text=feature_name,
                    variable=var,
                    anchor="w",
                    justify=tk.LEFT,
                    wraplength=250,
                    command=self.update_languages_based_on_all_features,
                )
                chk.grid(row=i, column=0, sticky="w", padx=(5, 2), pady=1)

                info_button = tk.Button(
                    feature_rows_frame,
                    text="?",
                    width=1,
                    command=lambda name=feature_name: self.show_feature_info(name),
                )
                info_button.grid(row=i, column=1, sticky="e", padx=(2, 5), pady=1)

        button_frame = tk.Frame(parent_frame)
        button_frame.pack(pady=(15, 5), padx=10, anchor="w", fill="x")

        deselect_button = tk.Button(
            button_frame, text="Deselect All", command=self.deselect_all
        )
        deselect_button.pack(side=tk.LEFT, padx=(0, 5))

    def show_province_info(self, lang_code: LanguageCode) -> None:
        """
        Displays a popup messagebox showing the list of provinces
        where the specified language is spoken.
        """
        full_name = self.language_names.get(lang_code, lang_code)
        province_set = self.languages.get(lang_code, set())

        province_list = sorted(list(province_set))
        if not province_list:
            province_text = "N/A"
        else:
            province_text = "\n".join(province_list)

        messagebox.showinfo(
            f"Provinces for {full_name}", f"Distributed in:\n\n{province_text}"
        )

    def show_feature_info(self, feature_name: FeatureName) -> None:
        """
        Displays a Toplevel window with details about the selected feature,
        including population pie chart, languages, and a web link button.
        Auto-sizes to content. Requires Matplotlib installed.
        """
        popup = tk.Toplevel(self)
        popup.title(f"Feature Info: {feature_name}")

        details = self.feature_details.get(feature_name, {})
        description = details.get("desc", "No description available.")
        wiki_link_url = details.get("link")
        langs_with_feature = self.lang_features.get(feature_name, set())

        pop_with_feature = 0
        pop_without_feature = 0
        total_pop = 0
        all_app_langs = set(self.language_populations.keys())
        langs_without_feature = all_app_langs - langs_with_feature

        for lang_code in langs_with_feature:
            pop_with_feature += self.language_populations.get(lang_code, 0)
        for lang_code in langs_without_feature:
            pop_without_feature += self.language_populations.get(lang_code, 0)

        total_pop = pop_with_feature + pop_without_feature

        language_names_list = sorted(
            [self.language_names.get(code, code) for code in langs_with_feature]
        )

        tk.Label(popup, text=feature_name, font="-weight bold").pack(
            pady=(10, 5), padx=10
        )

        desc_label = tk.Label(popup, text=description, wraplength=330, justify=tk.LEFT)
        desc_label.pack(pady=5, padx=10, anchor="w", fill=tk.X)

        tk.Label(
            popup, text="Languages with this feature:", font="-underline true"
        ).pack(pady=(10, 2), anchor="w", padx=10)

        lang_frame = tk.Frame(popup)
        lang_label = tk.Label(
            lang_frame,
            text=("\n".join(language_names_list) if language_names_list else "None"),
            justify=tk.LEFT,
        )
        lang_label.pack(side=tk.LEFT)
        lang_frame.pack(pady=2, padx=10, anchor="w")

        tk.Label(popup, text="Population:", font="-underline true").pack(
            pady=(10, 2), anchor="w", padx=10
        )
        chart_frame = tk.Frame(popup)

        if total_pop > 0 and (pop_with_feature > 0 or pop_without_feature > 0):
            labels = []
            sizes = []
            colors = []
            explode_list = []

            if pop_with_feature > 0:
                labels.append(f"With Feature\n({pop_with_feature}M)")
                sizes.append(pop_with_feature)
                colors.append("#99ff99")
                explode_list.append(0.05)

            if pop_without_feature > 0:
                labels.append(f"Without Feature\n({pop_without_feature}M)")
                sizes.append(pop_without_feature)
                colors.append("#ff9999")
                explode_list.append(0)

            explode = tuple(explode_list)

            fig = Figure(figsize=(3.5, 2.5), dpi=80)
            ax = fig.add_subplot(111)

            wedges, texts, autotexts = ax.pie(
                sizes,
                explode=explode,
                labels=labels,
                colors=colors,
                autopct="%1.1f%%",
                shadow=False,
                startangle=90,
                textprops=dict(color="black", size=8),
            )

            ax.axis("equal")
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        else:
            tk.Label(chart_frame, text="No population data available for chart.").pack()

        chart_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        if wiki_link_url:
            link_button = tk.Button(
                popup,
                text="Open Wikipedia Page",
                command=lambda url=wiki_link_url: webbrowser.open_new_tab(url),
            )
            link_button.pack(pady=(5, 5))
        else:
            tk.Label(popup, text="Wiki Link: N/A").pack(
                pady=(5, 5), anchor="w", padx=10
            )

        close_button = tk.Button(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=(5, 10))

    def deselect_all(self) -> None:
        """
        Sets all language AND feature BooleanVars to False and updates the map display.
        """
        for lang_var in self.language_vars.values():
            lang_var.set(False)
        for feature_var in self.feature_vars.values():
            feature_var.set(False)
        self.update_map_display()

    def update_languages_based_on_all_features(self) -> None:
        """
        Updates language selections based on the INTERSECTION of
        all currently checked feature checkboxes. Clears all language selections
        if no features are checked. Overwrites manual selections.
        """
        selected_features: List[FeatureName] = [
            name for name, var in self.feature_vars.items() if var.get()
        ]

        languages_to_select: Set[LanguageCode]

        if not selected_features:
            for var in self.language_vars.values():
                var.set(False)
        else:
            first_feature_name = selected_features[0]
            languages_to_select = self.lang_features.get(
                first_feature_name, set()
            ).copy()

            for i in range(1, len(selected_features)):
                feature_name = selected_features[i]
                current_feature_langs = self.lang_features.get(feature_name, set())
                languages_to_select.intersection_update(current_feature_langs)
                if not languages_to_select:
                    break

            for lang_code, var in self.language_vars.items():
                if lang_code in languages_to_select:
                    var.set(True)
                else:
                    var.set(False)

        self.update_map_display()

    def update_map_display(self) -> None:
        """
        Updates the visibility of province layers on the canvas based on the
        current state of the language checkboxes (self.language_vars).
        """
        provinces_to_show: ProvinceSet = set()
        for lang_code, var in self.language_vars.items():
            if var.get():
                provinces_for_this_language = self.languages.get(lang_code, set())
                provinces_to_show.update(provinces_for_this_language)

        for province, item_id in self.province_canvas_items.items():
            if province in provinces_to_show:
                self.canvas.itemconfigure(item_id, state="normal")
                self.canvas.tag_raise(item_id)
            else:
                self.canvas.itemconfigure(item_id, state="hidden")


if __name__ == "__main__":
    app = LanguageMapApp()
    app.mainloop()
