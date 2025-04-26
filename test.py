import tkinter as tk
from tkinter import ttk  # For themed widgets like Checkbutton
from PIL import Image, ImageTk  # Use Pillow for better PNG support
import os # To check if files exist

# --- Configuration ---
# !! Replace these with your actual filenames and dimensions !!
BACKGROUND_FILENAME = "./map/background.png"
LAYER_FILENAMES = ["./map/Anhui.png", "./map/Beijing.png", "./map/Chongqing.png", "./map/Fujian.png", "./map/Gansu.png", "./map/Guangdong.png", "./map/Guangxi.png", "./map/Guizhou.png", "./map/Hainan.png", "./map/Hebei.png", "./map/Heilongjiang.png", "./map/Henan.png", "./map/Hubei.png", "./map/Hunan.png", "./map/InnerMongolia.png", "./map/Jiangsu.png", "./map/Jiangxi.png", "./map/Jilin.png", "./map/Liaoning.png", "./map/Ningxia.png", "./map/Qinghai.png", "./map/Shaanxi.png", "./map/Shandong.png", "./map/Shanghai.png", "./map/Shanxi.png", "./map/Sichuan.png", "./map/Tianjin.png", "./map/Tibet.png", "./map/Xinjiang.png", "./map/Yunnan.png", "./map/Zhejiang.png"]

# Get dimensions from the background image (assuming all layers are the same size)
# You might want to set default dimensions if the background might not exist yet
try:
    with Image.open(BACKGROUND_FILENAME) as img:
        IMAGE_WIDTH, IMAGE_HEIGHT = img.size
except FileNotFoundError:
    print(f"Warning: Background file '{BACKGROUND_FILENAME}' not found. Using default dimensions 600x500.")
    IMAGE_WIDTH, IMAGE_HEIGHT = 600, 500
except Exception as e:
    print(f"Error opening background image: {e}. Using default dimensions 600x500.")
    IMAGE_WIDTH, IMAGE_HEIGHT = 600, 500

NUM_LAYERS = len(LAYER_FILENAMES)

# --- Main Application Class ---
class LayerApp:
    def __init__(self, master):
        """Initialize the application."""
        self.master = master
        master.title("PNG Layer Viewer")

        # --- Data Structures --- [cite: 7]
        self.layer_images = {}  # Stores PhotoImage objects {filename: PhotoImage}
        self.canvas_items = {}  # Stores Canvas item IDs {filename: item_id}
        self.layer_vars = {}    # Stores BooleanVar for checkboxes {filename: BooleanVar}

        # --- GUI Setup ---
        # Canvas for displaying images
        self.canvas = tk.Canvas(master, width=IMAGE_WIDTH, height=IMAGE_HEIGHT, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Frame for checkboxes with scrollbar
        checkbox_frame_outer = ttk.Frame(master)
        checkbox_frame_outer.grid(row=0, column=1, sticky="ns")

        # Add a canvas inside the frame to hold checkboxes and allow scrolling
        checkbox_canvas = tk.Canvas(checkbox_frame_outer, borderwidth=0)
        checkbox_frame_inner = ttk.Frame(checkbox_canvas)
        scrollbar = ttk.Scrollbar(checkbox_frame_outer, orient="vertical", command=checkbox_canvas.yview)
        checkbox_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        checkbox_canvas.pack(side="left", fill="both", expand=True)
        checkbox_canvas.create_window((0, 0), window=checkbox_frame_inner, anchor="nw")

        # Update scrollregion when frame size changes
        checkbox_frame_inner.bind("<Configure>", lambda e: checkbox_canvas.configure(scrollregion=checkbox_canvas.bbox("all")))

        # --- Load and Place Images ---
        self.load_background()
        self.load_layers() # Function to load layer PNGs [cite: 6]

        # --- Create Checkboxes ---
        self.create_checkboxes(checkbox_frame_inner) # Function to create controls [cite: 6]

        # --- Initial Layer Update ---
        self.update_layer_visibility() # Function to manage visibility [cite: 6]

        # Configure resizing behavior
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1) # Canvas expands
        master.grid_columnconfigure(1, weight=0) # Checkbox frame doesn't expand horizontally

    def load_image(self, filepath):
        """Loads an image using Pillow, returns PhotoImage object."""
        # Function to handle image loading [cite: 6]
        if not os.path.exists(filepath):
             print(f"Warning: Image file not found: {filepath}")
             # Create a dummy transparent image as placeholder if file not found
             img = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT), (0,0,0,0))
        else:
            try:
                img = Image.open(filepath)
                # Ensure image is RGBA for transparency
                img = img.convert("RGBA")
                # Check if dimensions match background (optional, but good practice)
                if img.size != (IMAGE_WIDTH, IMAGE_HEIGHT):
                    print(f"Warning: Image {filepath} size {img.size} doesn't match background size ({IMAGE_WIDTH}, {IMAGE_HEIGHT}). Resizing.")
                    img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT))

            except Exception as e:
                print(f"Error loading image {filepath}: {e}")
                # Create a dummy transparent image on error
                img = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT), (0,0,0,0))

        return ImageTk.PhotoImage(img)

    def load_background(self):
        """Loads and displays the background image."""
        # Function for specific background task [cite: 6]
        self.bg_photo_image = self.load_image(BACKGROUND_FILENAME)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo_image, tags="background")

    def load_layers(self):
        """Loads all layer images and places them hidden on the canvas."""
        # Function for loading multiple layers [cite: 6]
        print("Loading layers...")
        for filename in LAYER_FILENAMES:
            photo_img = self.load_image(filename)
            self.layer_images[filename] = photo_img
            # Create the image on canvas but initially hidden
            item_id = self.canvas.create_image(0, 0, anchor="nw", image=photo_img, state="hidden", tags=("layer", filename))
            self.canvas_items[filename] = item_id
        print("Finished loading layers.")

    def create_checkboxes(self, parent_frame):
        """Creates checkboxes for controlling layer visibility."""
        # Function for creating UI elements [cite: 6]
        ttk.Label(parent_frame, text="Layers:").pack(pady=5)
        for i, filename in enumerate(LAYER_FILENAMES):
            # Use a dictionary for BooleanVars [cite: 7]
            var = tk.BooleanVar(value=False) # Start unchecked
            chk = ttk.Checkbutton(
                parent_frame,
                text=f"Layer {i+1}", # Or use filename if more descriptive
                variable=var,
                command=self.update_layer_visibility # Command triggers update
            )
            chk.pack(anchor="w", padx=5)
            self.layer_vars[filename] = var

    def update_layer_visibility(self):
        """Updates the visibility of layers on the canvas based on checkbox states."""
        # Function to update visualization [cite: 6, 8]
        # print("Updating visibility...") # Debug print
        for filename, var in self.layer_vars.items():
            item_id = self.canvas_items.get(filename)
            if item_id:
                new_state = "normal" if var.get() else "hidden"
                self.canvas.itemconfigure(item_id, state=new_state)
                # Optional: Bring visible layers to top if needed (uncomment next line)
                # if new_state == "normal": self.canvas.tag_raise(item_id)


# --- Run the Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = LayerApp(root)
    root.mainloop()