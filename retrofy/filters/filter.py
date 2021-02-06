import numpy as np
import requests
import os
from PIL import Image
from pathlib import Path
import retrofy.utils as utils


class Filter():

    def __init__(self, img_src):
        self.__img_src = img_src


    @property
    def modified_img(self):
        return self.__modified_img

    @modified_img.setter
    def modified_img(self, img):
        if isinstance(img, Image.Image) == False:
            raise TypeError("Filter attribute 'modified_img' must be an Pillow Image object.")
        self.__before_last_mod = self.__modified_img
        self.__modified_img = img

    @property
    def original_img(self):
        return self.__original_img


    def load_image(self):
        if utils.is_url(self.__img_src) == True:
            try:
                self.__img_src = requests.get(self.__img_src, stream=True).raw
                self.__original_img = Image.open(self.__img_src).convert("RGB")
                self.__modified_img = self.__original_img
            except:
                raise ValueError("Could not download image from URL '{}'.".format(self.__img_src))
        else:
            try:
                self.__original_img = Image.open(self.__img_src).convert("RGB")
                self.__modified_img = self.__original_img
            except:
                raise ValueError("Could not access image on file '{}'.".format(self.__img_src))


    def undo(self):
        if hasattr(self, "_Filter__before_last_mod"):
            self.modified_img = self.__before_last_mod


    def reset(self):
        self.modified_img = self.__original_img


    def show(self, original=False):
        if original == False:
            self.__modified_img.show()
        else:
            self.__original_img.show()


    def save(self, path, original=False):
        if isinstance(path, str) == False and isinstance(file_path, Path) == False:
            raise TypeError("Parameter 'path' for 'save_result' method must be a string or a Path object.")
        path = Path(path)
        if path.suffix == "":
            path = path.parent / Path(path.stem + ".png")
        if self.__modified_img.mode == "RGBA" and path.suffix != "png":
            raise ValueError("RGBA Image must have 'png' file extension.")
        try:
            if original == False:
                self.__modified_img.save(path)
            else:
                self.__original_img.save(path)
        except:
            raise ValueError("Could not save image on especified path.")
