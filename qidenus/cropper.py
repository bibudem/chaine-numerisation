###########################################################################
# Script pour recadrer des images, par exemple issues du Qidenus
#
# On doit lui donner en paramètre le nom d'un dossier qui contient des
# TIFF (.tif ou .tiff). Les fichiers vont aussi contenir la chaîne
# "_Page_gauche" ou "Page_droite".
#
# Le script va les ouvrir un par un, les pages gauches ensuite les pages
# droite, les montrer à l'écran, permettre de recadrer en présentant
# la dernière zone de recadrage par défaut.
#
# Les images résultants sont enregistrées dans un sous-dossier "crop",
# et les "_Page_gauche" et "_Page_droite" sont retirées des noms
# de fichier.
###########################################################################
import os
import sys
from PIL import Image, ImageTk
import tkinter as tk

HANDLE_SIZE = 10  # Pour les coins du rectangle
CROP_FOLDER = "crop"    # Sous-dossier pour les images recadrées

import os

def is_already_cropped(filepath: str) -> bool:
    """
    Retourne True si une version 'croppée' du fichier existe dans le sous-dossier 'crop'.

    Exemple : pour 'path/to/Test_Page_gauche.tif',
    vérifie si 'path/to/crop/Test.tif' existe.
    """
    folder = os.path.dirname(filepath)
    filename = os.path.basename(filepath)

    # Retirer les suffixes "_Page_gauche" et "_Page_droite"
    base_name = filename.replace("_Page_gauche", "").replace("_Page_droite", "")

    # Construire le chemin du fichier croppé
    crop_folder = os.path.join(folder, CROP_FOLDER)
    cropped_path = os.path.join(crop_folder, base_name)

    return os.path.exists(cropped_path)


def get_cropped_output_path(input_path: str) -> str:
    """
    Prend un chemin d'image en entrée (ex: a/b/c/toto_Page_gauche.TIF)
    et retourne le chemin vers le fichier dans le sous-dossier 'crop',
    avec '_Page_gauche' ou '_Page_droite' retiré du nom.
    
    Crée le dossier 'crop' si nécessaire.
    """
    # Récupérer le dossier d'origine
    folder = os.path.dirname(input_path)
    
    # Créer le chemin vers le sous-dossier "crop"
    crop_folder = os.path.join(folder, CROP_FOLDER)
    os.makedirs(crop_folder, exist_ok=True)

    # Récupérer le nom de fichier sans les suffixes
    filename = os.path.basename(input_path)
    filename = filename.replace("_Page_gauche", "").replace("_Page_droite", "")

    # Retourner le chemin final
    return os.path.join(crop_folder, filename)

class Cropper:
    def __init__(self, folder):
        self.folder = folder
        self.tiff_files = self.load_tiff_files(folder)
        if not self.tiff_files:
            print("Aucune image TIFF trouvée.")
            sys.exit(1)

        self.index = 0
        self.crop_box = None
        self.last_crop_box = None
        self.drag_type = None
        self.dragging = False

        self.window = tk.Tk()
        self.window.title("Qidenus Cropper")
        self.canvas = tk.Canvas(self.window, cursor="cross")
        self.canvas.pack()

        # Barre de boutons
        btn_frame = tk.Frame(self.window)
        btn_frame.pack()
        tk.Button(btn_frame, text="Image précédente (<-)", command=self.previous_image).pack(side="left")
        tk.Button(btn_frame, text="Enregistrer (S)", command=self.save_crop).pack(side="left")
        tk.Button(btn_frame, text="Image suivante (->)", command=self.next_image).pack(side="left")

        # Barre d'état
        self.status_label = tk.Label(self.window, text="")
        self.status_label.pack()

        # Bind souris & clavier
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.window.bind("<Left>", lambda e: self.previous_image())
        self.window.bind("<Right>", lambda e: self.next_image())
        self.window.bind("<s>", lambda e: self.save_crop())
        self.window.bind("<S>", lambda e: self.save_crop())
        self.canvas.bind("<Motion>", self.on_mouse_motion)

        self.load_image()
        self.window.mainloop()

    def on_mouse_motion(self, event):
        x, y = event.x, event.y
        ctrl_held = (event.state & 0x4) != 0  # CTRL ?

        if ctrl_held:
            self.canvas.config(cursor="cross")
            return

        drag_type = self.detect_drag_type(x, y)
        if drag_type in {"nw", "ne", "sw", "se"}:
            self.canvas.config(cursor="cross")  # Redimensionner
        elif drag_type == "move":
            self.canvas.config(cursor="fleur")  # Déplacement
        else:
            self.canvas.config(cursor="arrow")

    def load_tiff_files(self, folder):
        files = [f for f in os.listdir(folder) if f.lower().endswith(('.tif', '.tiff'))]
        gauche = sorted([f for f in files if "Page_gauche" in f])
        droite = sorted([f for f in files if "Page_droite" in f])
        autres = sorted([f for f in files if f not in gauche + droite])
        return gauche + droite + autres

    def load_image(self):
        filepath = os.path.join(self.folder, self.tiff_files[self.index])
        self.original_image = Image.open(filepath)
        filename = os.path.basename(filepath)
        if "Page_gauche" in filename:
            self.original_image = self.original_image.rotate(90, expand=True)
        elif "Page_droite" in filename:
            self.original_image = self.original_image.rotate(-90, expand=True)
        self.display_image = self.original_image.copy()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        max_width = screen_width - 100
        max_height = screen_height - 200
        self.display_image.thumbnail((max_width, max_height), Image.LANCZOS)

        PADDING = 20
        self.tk_image = ImageTk.PhotoImage(self.display_image)

        self.canvas.config(width=self.tk_image.width() + 2 * PADDING, height=self.tk_image.height() + 2 * PADDING)
        self.canvas.create_image(PADDING, PADDING, anchor="nw", image=self.tk_image)

        if self.last_crop_box:
            self.crop_box = self.last_crop_box
        else:
            self.crop_box = None

        self.redraw_crop_box()
        self.status_label.config(text=f"{self.index+1}/{len(self.tiff_files)} : {self.tiff_files[self.index]}")
        if (is_already_cropped(filepath)):
            self.status_label.config(fg="green")
        else:
            self.status_label.config(fg="black")

    def redraw_crop_box(self):
        self.canvas.delete("crop")
        if self.crop_box:
            x1, y1, x2, y2 = self.crop_box
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2, tags="crop")
            for x, y in [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]:
                self.canvas.create_oval(x - HANDLE_SIZE, y - HANDLE_SIZE,
                                        x + HANDLE_SIZE, y + HANDLE_SIZE,
                                        fill="red", tags="crop")

    def on_mouse_press(self, event):
        x, y = event.x, event.y
        self.start_x = x
        self.start_y = y
        self.dragging = True

        ctrl_held = (event.state & 0x4) != 0  # CTRL (sur Windows/Linux)

        if ctrl_held or not self.crop_box:
            # Forcer une nouvelle sélection
            self.crop_box = (x, y, x, y)
            self.drag_type = "new"
        else:
            drag_type = self.detect_drag_type(x, y)
            if drag_type:
                self.drag_type = drag_type
            else:
                # Clic hors de la zone : rien
                self.dragging = False
                self.drag_type = None

        self.redraw_crop_box()

    def on_mouse_drag(self, event):
        if not self.dragging or not self.drag_type:
            return

        x, y = event.x, event.y
        x1, y1, x2, y2 = self.crop_box or (0, 0, 0, 0)

        if self.drag_type == "new":
            self.crop_box = (self.start_x, self.start_y, x, y)
        elif self.drag_type == "move":
            dx = x - self.start_x
            dy = y - self.start_y
            self.crop_box = (x1 + dx, y1 + dy, x2 + dx, y2 + dy)
            self.start_x, self.start_y = x, y
        elif self.drag_type == "nw":
            self.crop_box = (x, y, x2, y2)
        elif self.drag_type == "ne":
            self.crop_box = (x1, y, x, y2)
        elif self.drag_type == "sw":
            self.crop_box = (x, y1, x2, y)
        elif self.drag_type == "se":
            self.crop_box = (x1, y1, x, y)

        self.redraw_crop_box()

    def on_mouse_release(self, event):
        self.dragging = False
        if self.crop_box:
            x1, y1, x2, y2 = self.crop_box
            if abs(x2 - x1) < 5 or abs(y2 - y1) < 5:
                self.crop_box = None
            else:
                self.crop_box = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                self.last_crop_box = self.crop_box
        self.redraw_crop_box()

    def detect_drag_type(self, x, y):
        if not self.crop_box:
            return None

        x1, y1, x2, y2 = self.crop_box
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])

        # Détection des coins (pour redimensionnement)
        handles = {
            "nw": (x1, y1),
            "ne": (x2, y1),
            "sw": (x1, y2),
            "se": (x2, y2)
        }

        for key, (hx, hy) in handles.items():
            if abs(x - hx) <= HANDLE_SIZE and abs(y - hy) <= HANDLE_SIZE:
                return key

        # Détection des bords (redimensionnement aussi)
        edge_margin = 5
        if x1 - edge_margin <= x <= x2 + edge_margin and abs(y - y1) <= edge_margin:
            return "n"
        if x1 - edge_margin <= x <= x2 + edge_margin and abs(y - y2) <= edge_margin:
            return "s"
        if y1 - edge_margin <= y <= y2 + edge_margin and abs(x - x1) <= edge_margin:
            return "w"
        if y1 - edge_margin <= y <= y2 + edge_margin and abs(x - x2) <= edge_margin:
            return "e"

        # Sinon, déplacement uniquement si à l'intérieur du rectangle
        if x1 + edge_margin < x < x2 - edge_margin and y1 + edge_margin < y < y2 - edge_margin:
            return "move"

        return None



    def save_crop(self):
        if not self.crop_box:
            self.status_label.config(text="❌ Aucune sélection à recadrer.")
            return

        scale_x = self.original_image.width / self.display_image.width
        scale_y = self.original_image.height / self.display_image.height
        x1, y1, x2, y2 = [int(v * s) for v, s in zip(self.crop_box, (scale_x, scale_y, scale_x, scale_y))]

        cropped = self.original_image.crop((x1, y1, x2, y2))
        filepath = os.path.join(self.folder, self.tiff_files[self.index])
        try:
            cropped.save(get_cropped_output_path(filepath))
            self.status_label.config(text=f"✅ Enregistré : {get_cropped_output_path(filepath)}", fg="green")
            self.next_image()
        except Exception as e:
            self.status_label.config(text=f"❌ Erreur : {e}", fg="red")

    def next_image(self):
        if self.index < len(self.tiff_files) - 1:
            self.index += 1
            self.load_image()

    def previous_image(self):
        if self.index > 0:
            self.index -= 1
            self.load_image()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : python cropper.py <dossier_avec_images_TIFF>")
        sys.exit(1)
    Cropper(sys.argv[1])
