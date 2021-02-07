import numpy as np
import random
from PIL import Image, ImageFilter, ImageOps, ImageEnhance, ImageChops
import blend_modes
from pathlib import Path
from retrofy.filters.filter import Filter
from retrofy.configs import VHS_Configs
import retrofy.utils as utils

CONFIGS = VHS_Configs()

class VHS(Filter):

    def __init__(self, img_src):
        super().__init__(img_src)


    @staticmethod
    def get_noise_lines_by_id(id):
        if isinstance(id, int) == False:
            raise TypeError("Parameter 'id' must be an integer.")

        is_id_validated, id_path = utils.is_in_folder(CONFIGS.PATHS["images"]["noise_lines"], str(id), format="png")
        if is_id_validated == True:
            noise_lines_img = Image.open(id_path).convert("L")
            return noise_lines_img
        else:
            raise ValueError("Invalid ID '{}' for noise lines images.".format(id))


    @staticmethod
    def generate_noise_lines(size=CONFIGS.SIZE, intensity=CONFIGS.DEFAULTS["noise_lines"]["intensity"], blur=CONFIGS.DEFAULTS["noise_lines"]["blur"], bright=CONFIGS.DEFAULTS["noise_lines"]["bright"]):
        if isinstance(size, tuple) == False:
            raise TypeError("Parameter 'size' must be a tuple.")
        if isinstance(intensity, float) == False:
            raise TypeError("Parameter 'intensity' must be a float.")
        if isinstance(blur, float) == False:
            raise TypeError("Parameter 'blur' must be a float.")
        if isinstance(bright, float) == False:
            raise TypeError("Parameter 'bright' must be a float.")

        intensity = utils.clamp(intensity, 0, 1)
        blur = utils.clamp(blur, 0, 1)
        bright = utils.clamp(bright, 0, 1)

        p_threshold = utils.translate_ranges(intensity, 1, 0, CONFIGS.MINS["noise_lines"]["p_threshold"], 1)

        iterations = int(utils.pctg_to_value(intensity, CONFIGS.MAXS["noise_lines"]["iter"]))
        blur = utils.pctg_to_value(blur, CONFIGS.MAXS["noise_lines"]["blur"])
        bright = utils.pctg_to_value(bright, CONFIGS.MAXS["noise_lines"]["bright"])

        size = (size[1], size[0])
        if isinstance(size, tuple) == False:
            raise TypeError("Parameter 'size' from 'generate_noise_lines' method must be a tuple.")

        noise_arr = np.zeros(size, dtype=np.uint8)

        n_rows = noise_arr.shape[0]
        n_cols = noise_arr.shape[1]

        for i in range(iterations):
            for row in range(n_rows):
                p = random.uniform(0,1) #probability of row become a noise line
                if row < n_rows/10 or n_rows - row < n_rows/10: #increases probability for top and bottom rows
                    p += p * 0.1
                elif row < n_rows/30 or n_rows - row < n_rows/30:
                    p += p * 0.1

                if p > p_threshold: #row becomes a noise line
                    hsize = np.random.choice(np.arange(1,3), p=[0.95, 0.05]) #line horizontal size
                    vstart = random.randint(0, n_cols-1) #line vertical start pixel
                    vend = random.randint(0, int(n_cols / np.random.choice(np.array([5, 10, 15, 20]), p=[0.1, 0.2, 0.3, 0.4]))) #line vertical end pixel based on array size. Smaller lines have more chance to occur

                    noise_arr[row : row + hsize, vstart % n_cols : (vstart + vend) % n_cols] = 1

                    np.random.shuffle(noise_arr[row, vstart : vstart + vend + int(n_cols/15)]) #creates noise for each line

        noise_lines_img = Image.fromarray(noise_arr*255, "L")
        noise_lines_img = noise_lines_img.filter(ImageFilter.GaussianBlur(blur)) #applying gaussian blur
        bright_enhancer = ImageEnhance.Brightness(noise_lines_img)
        noise_lines_img = bright_enhancer.enhance(bright) #enhancing brightness

        return noise_lines_img


    def apply_noise_lines(self, intensity=CONFIGS.DEFAULTS["noise_lines"]["intensity"], blur=CONFIGS.DEFAULTS["noise_lines"]["blur"], bright=CONFIGS.DEFAULTS["noise_lines"]["bright"], img_id=None, inplace=True):
        if isinstance(intensity, float) == False:
            raise TypeError("Parameter 'intensity' must be a float.")
        if isinstance(blur, float) == False:
            raise TypeError("Parameter 'blur' must be a float.")
        if isinstance(bright, float) == False:
            raise TypeError("Parameter 'bright' must be a float.")
        if isinstance(img_id, int) == False and img_id != None:
            raise TypeError("Parameter 'img_id' must be an integer.")
        if isinstance(inplace, bool) == False:
            raise TypeError("Parameter 'inplace' must be a boolean.")

        if img_id != None:
            noise_lines_mask = VHS.get_noise_lines_by_id(img_id)
            noise_lines_mask = noise_lines_mask.resize(self.modified_img.size)
        else:
            noise_lines_mask = VHS.generate_noise_lines(size=self.modified_img.size, intensity=intensity, blur=blur, bright=bright)

        white_img = Image.new("RGB", self.modified_img.size, (255,255,255))

        resulted_img = Image.composite(white_img, self.modified_img, noise_lines_mask)

        if inplace == False:
            return resulted_img
        else:
            self.modified_img = resulted_img


    def __get_single_channel_rgb_img(self, channel):
        if self.modified_img.mode not in ["RGB", "RGBA"]:
            raise ValueError("Invalid image mode '{}'. Image must have 3 channels or more.".format(self.modified_img.mode))
        r,g,b = self.modified_img.split()[:3]
        channel = channel.strip().lower()
        if channel == "r":
            g = g.point(lambda x: x-x)
            b = b.point(lambda x: x-x)
        elif channel == "g":
            r = r.point(lambda x: x-x)
            b = b.point(lambda x: x-x)
        elif channel == "b":
            r = r.point(lambda x: x-x)
            g = g.point(lambda x: x-x)
        else:
            raise ValueError("Invalid channel '{}' for RGB image.".format(channel))

        return Image.merge("RGB", (r,g,b))


    def apply_color_glitch(self, intensity=0.3, crop=True, inplace=True):
        if isinstance(intensity, float) == False:
            raise TypeError("Parameter 'intensity' must be a float.")
        if isinstance(crop, bool) == False:
            raise TypeError("Parameter 'crop' must be a boolean.")
        if isinstance(inplace, bool) == False:
            raise TypeError("Parameter 'inplace' must be a boolean.")

        intensity = utils.clamp(intensity, 0, 1)
        offset = int(utils.pctg_to_value(intensity, CONFIGS.MAXS["color_glitch"]["distortion"]))

        red_img = self.__get_single_channel_rgb_img("r").convert("RGBA")
        red_img = ImageChops.offset(red_img, offset, -offset)

        green_img = self.__get_single_channel_rgb_img("g").convert("RGBA")

        blue_img = self.__get_single_channel_rgb_img("b").convert("RGBA")
        blue_img = ImageChops.offset(blue_img, -offset, offset)

        resulted_img = ImageChops.add(green_img, red_img, 1)
        resulted_img = ImageChops.add(resulted_img, blue_img, 1)

        if crop == True:
            resulted_img = ImageOps.crop(resulted_img, offset)

        if inplace == False:
            return resulted_img
        else:
            self.modified_img = resulted_img


    def apply_film_grain(self, intensity=0.5, blur=0.3, inplace=True):
        if isinstance(intensity, float) == False:
            raise TypeError("Parameter 'intensity' must be a float.")
        if isinstance(blur, float) == False:
            raise TypeError("Parameter 'blur' must be a float.")
        if isinstance(inplace, bool) == False:
            raise TypeError("Parameter 'inplace' must be a boolean.")

        intensity = utils.clamp(intensity, 0, 1)
        blur = utils.clamp(blur, 0, 1)
        blur = utils.pctg_to_value(blur, CONFIGS.MAXS["film_grain"]["blur"])

        middle_gray = Image.new("RGB", self.modified_img.size, (119, 119, 119)).convert("RGBA")

        w, h = self.modified_img.size
        noise_arr = np.random.normal(0, CONFIGS.DEFAULTS["film_grain"]["gaussian_std"], w*h)
        noise_arr = np.uint8(noise_arr.reshape(h, w))
        noise_img = Image.fromarray(noise_arr).convert("RGBA")

        noise_img = Image.blend(middle_gray, noise_img, intensity)
        noise_img = noise_img.filter(ImageFilter.GaussianBlur(blur))

        resulted_img = self.modified_img
        if resulted_img.mode != "RGBA":
            resulted_img = resulted_img.convert("RGBA")

        noise_arr = np.array(noise_img).astype(float)
        resulted_arr = np.array(resulted_img).astype(float)

        resulted_arr = blend_modes.overlay(resulted_arr, noise_arr, intensity/2)
        resulted_img = Image.fromarray(resulted_arr.astype(np.uint8))

        if inplace == False:
            return resulted_img
        else:
            self.modified_img = resulted_img

    def apply_horizontal_lines(self, intensity=0.5, blur=0.5, inplace=True):
        if isinstance(intensity, float) == False:
            raise TypeError("Parameter 'intensity' must be a float.")
        if isinstance(blur, float) == False:
            raise TypeError("Parameter 'blur' must be a float.")
        if isinstance(inplace, bool) == False:
            raise TypeError("Parameter 'inplace' must be a boolean.")

        intensity = utils.clamp(intensity, 0, 1)
        intensity = utils.translate_ranges(intensity, 0, 1, 0.35, 0.75)
        height_divider = utils.pctg_to_value(intensity, CONFIGS.MAXS["horizontal_lines"]["height_divider"])
        height_divider = utils.translate_ranges(height_divider, 0, CONFIGS.MAXS["horizontal_lines"]["height_divider"], CONFIGS.MAXS["horizontal_lines"]["height_divider"], 0)

        blur = utils.clamp(blur, 0, 1)
        blur = utils.pctg_to_value(blur, CONFIGS.MAXS["horizontal_lines"]["blur"])

        w, h = self.modified_img.size
        resulted_img = self.modified_img
        if resulted_img.mode != "RGBA":
            resulted_img = resulted_img.convert("RGBA")

        resulted_arr = np.array(resulted_img).astype(float)

        lines_arr = np.zeros((h,w), dtype=np.uint8)
        lines_rows = lines_arr.shape[0]
        lines_cols = lines_arr.shape[1]

        pixels_between = int(h/height_divider)
        for row in range(lines_rows):
            if row % pixels_between == 0:
                lines_arr[row,:] = 1

        lines_img = Image.fromarray(lines_arr*255).convert("RGBA")
        lines_img = lines_img.filter(ImageFilter.GaussianBlur(blur))
        lines_arr = np.array(lines_img).astype(float)

        resulted_arr = blend_modes.soft_light(resulted_arr, lines_arr,intensity)
        resulted_img = Image.fromarray(resulted_arr.astype(np.uint8))

        if inplace == False:
            return resulted_img
        else:
            self.modified_img = resulted_img


    def apply_all_effects(self, inplace=True):
        if isinstance(inplace, bool) == False:
            raise TypeError("Parameter 'inplace' must be a boolean.")

        self.apply_noise_lines()
        self.apply_color_glitch()
        self.apply_horizontal_lines()
        self.apply_film_grain()

        if inplace==False:
            resulted_img = self.modified_img
            self.undo(4)
            return resulted_img
