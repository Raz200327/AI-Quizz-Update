import pytesseract
from PIL import Image
import os
import pyheif
import argparse

class LectureSlides:
    def __init__(self, slide_directory):

        if slide_directory.split(".")[1] == "heic":

            heif_file = pyheif.read(f"./media/{slide_directory}")

            # Convert the image to a PIL Image object
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )
            image.save(f"./media/{slide_directory.split('.')[0]}.png", "PNG")
            os.remove(f"./media/{slide_directory}")
            self.slide_directory = f"{slide_directory.split('.')[0]}.png"

        else:
            self.slide_directory = slide_directory

    def image_extract(self):
        self.text = pytesseract.image_to_string(Image.open(f"./media/{self.slide_directory}")).replace("\n", " ")
        for i in os.listdir("./media/"):
            os.remove(f"./media/{i}")
        return self.text
