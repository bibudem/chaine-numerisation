import os
import sys
import re
import io
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader


# DPI cible pour le rendu PDF
TARGET_DPI = 300

def get_groups(tiff_files):
    groups = {}
    for filename in tiff_files:
        match = re.match(r"(\d+)_\d+\.TIF$", filename, re.IGNORECASE)
        if match:
            prefix = match.group(1)
            groups.setdefault(prefix, []).append(filename)
    return groups

def sort_by_page_number(filenames):
    def extract_page(f):
        match = re.match(r"\d+_(\d+)\.TIF$", f, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    return sorted(filenames, key=extract_page)

def tiff_images_to_pdf(folder, prefix, tiff_files, dpi=300):
    output_pdf_path = os.path.join(os.path.dirname(folder), f"{prefix}.pdf")
    c = canvas.Canvas(output_pdf_path, pagesize=letter)

    width_inch, height_inch = letter[0] / 72.0, letter[1] / 72.0  # Lettre US: 8.5x11 pouces

    for filename in tiff_files:
        tiff_path = os.path.join(folder, filename)
        img = Image.open(tiff_path)
        img.load()

        # Redimensionner l'image pour tenir dans une page Lettre à la résolution choisie
        max_width_px = int(width_inch * dpi)
        max_height_px = int(height_inch * dpi)

        img.thumbnail((max_width_px, max_height_px), Image.LANCZOS)

        # Convertir en mode RGB si nécessaire
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Sauvegarder dans un buffer mémoire
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG', dpi=(dpi, dpi))
        img_buffer.seek(0)

        # Utiliser ImageReader depuis la mémoire
        image_reader = ImageReader(img_buffer)
        c.drawImage(image_reader, 0, 0, width=letter[0], height=letter[1])
        c.showPage()


    c.save()
    print(f"PDF créé : {output_pdf_path}")


def main():
    if len(sys.argv) < 2:
        print("Utilisation : python tif@pdf.py <chemin_du_dossier>")
        return

    folder = sys.argv[1]
    if not os.path.isdir(folder):
        print("Le chemin fourni n'est pas un dossier.")
        return

    tiff_files = [f for f in os.listdir(folder) if f.upper().endswith((".TIF", ".TIFF"))]
    groups = get_groups(tiff_files)

    for prefix, files in groups.items():
        sorted_files = sort_by_page_number(files)
        tiff_images_to_pdf(folder, prefix, sorted_files, dpi=TARGET_DPI)

if __name__ == "__main__":
    main()
