
import os
from google.cloud import vision
from datetime import datetime

def extract_text_from_slides():
    """
    Extracts text from PNG files in the 'slides/' directory using Google Cloud Vision API,
    orders them by filename timestamp, and saves the text to a file with slide breaks.
    """
    slides_dir = "slides"
    output_dir = "output"
    output_txt_path = os.path.join(output_dir, "slides_text.txt")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_files = [f for f in os.listdir(slides_dir) if f.endswith(".png")]
    image_files.sort(key=lambda x: datetime.strptime(x, "Screenshot %Y-%m-%d %I.%M.%S %p.png"))

    client = vision.ImageAnnotatorClient()

    with open(output_txt_path, "w") as output_file:
        for i, filename in enumerate(image_files):
            filepath = os.path.join(slides_dir, filename)
            
            with open(filepath, "rb") as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            response = client.text_detection(image=image)
            texts = response.text_annotations

            output_file.write(f"--- Slide {i+1} ---\n")
            if texts:
                output_file.write(texts[0].description)
            output_file.write("\n\n")

    print(f"Successfully extracted text to {output_txt_path}")

if __name__ == "__main__":
    extract_text_from_slides()
