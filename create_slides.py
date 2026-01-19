
import os
from PIL import Image
from datetime import datetime

def create_slides_pdf():
    """
    Combines all PNG files from the 'slides/' directory into a single PDF file,
    ordered by their creation date.
    """
    slides_dir = "slides"
    output_dir = "output"
    output_pdf_path = os.path.join(output_dir, "slides.pdf")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_files = [f for f in os.listdir(slides_dir) if f.endswith(".png")]

    # Sort files by the timestamp in their filenames
    image_files.sort(key=lambda x: datetime.strptime(x, "Screenshot %Y-%m-%d %I.%M.%S %p.png"))

    images = []
    for filename in image_files:
        filepath = os.path.join(slides_dir, filename)
        img = Image.open(filepath)
        img = img.convert("RGB")
        images.append(img)
1
    if images:
        images[0].save(
            output_pdf_path, "PDF" ,resolution=100.0, save_all=True, append_images=images[1:]
        )
        print(f"Successfully created {output_pdf_path}")
    else:
        print("No PNG images found in the slides directory.")

if __name__ == "__main__":
    create_slides_pdf()
