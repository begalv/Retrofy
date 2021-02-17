import numpy as np
import random
from PIL import Image, ImageFilter, ImageOps, ImageEnhance, ImageChops, ImageDraw, ImageFont
import blend_modes
from pathlib import Path
import datetime as dt
from retrofy.filters.filter import Filter
from retrofy.configs import VHS_Configs
import retrofy.utils as utils
import copy

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
        if isinstance(intensity, (int, float)) == False:
            raise TypeError("Parameter 'intensity' must be a float.")
        if isinstance(blur, (int, float)) == False:
            raise TypeError("Parameter 'blur' must be a float.")
        if isinstance(bright, (int, float)) == False:
            raise TypeError("Parameter 'bright' must be a float.")

        intensity = utils.clamp(intensity, CONFIGS.MINS["noise_lines"]["intensity"], 1)
        blur = utils.clamp(blur, 0, 1)
        bright = utils.clamp(bright, 0, 1)

        p_threshold = utils.translate_ranges(intensity, 1, 0, CONFIGS.MINS["noise_lines"]["p_threshold"], 1)

        iterations = int(utils.pctg_to_value(intensity, CONFIGS.MAXS["noise_lines"]["iter"]))
        blur = utils.pctg_to_value(blur, CONFIGS.MAXS["noise_lines"]["blur"])
        bright = utils.pctg_to_value(bright, CONFIGS.MAXS["noise_lines"]["bright"])

        size = (size[1], size[0])
        if isinstance(size, tuple) == False:
            raise TypeError("Parameter 'size' must be a tuple.")

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
        if isinstance(intensity, (int, float)) == False:
            raise TypeError("Parameter 'intensity' must be a float.")
        if isinstance(blur, (int, float)) == False:
            raise TypeError("Parameter 'blur' must be a float.")
        if isinstance(bright, (int, float)) == False:
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



    def apply_color_glitch(self, intensity=CONFIGS.DEFAULTS["color_glitch"]["intensity"], crop=True, inplace=True):
        if isinstance(intensity, (int, float)) == False:
            raise TypeError("Parameter 'intensity' must be a float.")
        if isinstance(crop, bool) == False:
            raise TypeError("Parameter 'crop' must be a boolean.")
        if isinstance(inplace, bool) == False:
            raise TypeError("Parameter 'inplace' must be a boolean.")

        h = self.modified_img.size[1]

        intensity = utils.clamp(intensity, 0, 1)
        intensity = utils.translate_ranges(intensity, 0, 1, CONFIGS.MINS["color_glitch"]["intensity"], CONFIGS.MAXS["color_glitch"]["intensity"])
        offset = int(utils.pctg_to_value(intensity, h/CONFIGS.DEFAULTS["color_glitch"]["height_divider"]))
        offset = utils.clamp(offset, CONFIGS.MINS["color_glitch"]["offset"], CONFIGS.MAXS["color_glitch"]["offset"])

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



    def apply_film_grain(self, intensity=CONFIGS.DEFAULTS["film_grain"]["intensity"], blur=CONFIGS.DEFAULTS["film_grain"]["blur"], inplace=True):
        if isinstance(intensity, (int, float)) == False:
            raise TypeError("Parameter 'intensity' must be a float.")
        if isinstance(blur, (int, float)) == False:
            raise TypeError("Parameter 'blur' must be a float.")
        if isinstance(inplace, bool) == False:
            raise TypeError("Parameter 'inplace' must be a boolean.")

        w, h = self.modified_img.size

        intensity = utils.clamp(intensity, 0, 1)
        intensity = utils.translate_ranges(intensity, 0, 1, CONFIGS.MINS["film_grain"]["intensity"], 1)
        blur = utils.clamp(blur, 0, 1)
        blur = utils.pctg_to_value(blur, CONFIGS.MAXS["film_grain"]["blur"])

        middle_gray = Image.new("RGB", self.modified_img.size, (119, 119, 119)).convert("RGBA")

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



    def apply_horizontal_lines(self, intensity=CONFIGS.DEFAULTS["horizontal_lines"]["intensity"], blur=CONFIGS.DEFAULTS["horizontal_lines"]["blur"], inplace=True):
        if isinstance(intensity, (int, float)) == False:
            raise TypeError("Parameter 'intensity' must be a float.")
        if isinstance(blur, (int, float)) == False:
            raise TypeError("Parameter 'blur' must be a float.")
        if isinstance(inplace, bool) == False:
            raise TypeError("Parameter 'inplace' must be a boolean.")

        w, h = self.modified_img.size

        intensity = utils.clamp(intensity, CONFIGS.MINS["horizontal_lines"]["intensity"], CONFIGS.MAXS["horizontal_lines"]["intensity"])

        height_divided = h/CONFIGS.DEFAULTS["horizontal_lines"]["height_divider"]
        n_lines = utils.pctg_to_value(intensity, height_divided)
        n_lines = utils.translate_ranges(n_lines, 0, height_divided, height_divided, 0)

        blur = utils.clamp(blur, 0, 1)
        blur = utils.pctg_to_value(blur, CONFIGS.MAXS["horizontal_lines"]["blur"])

        resulted_img = self.modified_img
        if resulted_img.mode != "RGBA":
            resulted_img = resulted_img.convert("RGBA")

        resulted_arr = np.array(resulted_img).astype(float)

        lines_arr = np.zeros((h,w), dtype=np.uint8)
        lines_rows = lines_arr.shape[0]
        lines_cols = lines_arr.shape[1]

        pixels_between = int(h/n_lines)
        for row in range(lines_rows):
            if row % pixels_between == 0:
                lines_arr[row,:] = 1

        lines_img = Image.fromarray(lines_arr*255).convert("RGBA")
        lines_img = lines_img.filter(ImageFilter.GaussianBlur(blur))
        lines_arr = np.array(lines_img).astype(float)

        resulted_arr = blend_modes.soft_light(resulted_arr, lines_arr, CONFIGS.DEFAULTS["horizontal_lines"]["bright"])
        resulted_img = Image.fromarray(resulted_arr.astype(np.uint8))

        if inplace == False:
            return resulted_img
        else:
            self.modified_img = resulted_img



    def apply_wave_warp(self, intensity=CONFIGS.DEFAULTS["wave_warp"]["intensity"], row=None, inplace=True):
        if isinstance(intensity, (float, int)) == False:
            raise TypeError("Parameter 'intensity' must be a float.")
        if isinstance(row, int) == False and row != None:
            raise TypeError("Parameter 'row' must be an integer.")
        if isinstance(inplace, bool) == False:
            raise TypeError("Parameter 'inplace' must be a boolean.")

        w, h = self.modified_img.size

        if row != None:
            if row < 0 or row >= h:
                raise ValueError("Parameter 'row' must be lesser than image's height.")
        else:
            row = random.randint(0, h)

        intensity = utils.clamp(intensity, CONFIGS.MINS["wave_warp"]["intensity"], CONFIGS.MAXS["wave_warp"]["intensity"])

        height_divided = h/CONFIGS.DEFAULTS["wave_warp"]["height_divider"]
        max_number_of_warps = utils.pctg_to_value(intensity, height_divided)
        max_number_of_warps = utils.translate_ranges(max_number_of_warps, 0, height_divided, height_divided, 0)

        img_arr = np.asarray(self.modified_img)
        img_arr.flags.writeable = True

        size = int(h/max_number_of_warps)

        if row - size*2 >= 0:
            img_arr[row - size:row,:] = img_arr[row - size*2:row - size,:]

        resulted_img = Image.fromarray(img_arr)
        if inplace == False:
            return resulted_img
        else:
            self.modified_img = resulted_img



    def apply_play_text(self, intensity=CONFIGS.DEFAULTS["play_text"]["intensity"], datetime=None, hour=None, inplace=True):
        if isinstance(intensity, (int, float)) == False:
            raise TypeError("Parameter 'intensity' must be a float.")
        if isinstance(datetime, dt.datetime) == False and datetime != None:
            raise TypeError("Parameter 'datetime' must be a datetime.datetime object.")
        if isinstance(hour, int) == False and hour != None:
            raise TypeError("Parameter 'hour' must be an integer.")
        if isinstance(inplace, bool) == False:
            raise TypeError("Parameter 'inplace' must be a boolean.")

        if hour != None and (hour < 0 or hour > 23):
            raise ValueError("Parameter 'hour' must be an integer between 0 and 23.")

        if datetime == None:
            datetime = utils.get_random_datetime(1980, 1990, hour)
        elif datetime != None and hour != None:
            raise ValueError("Parameter 'hour' can only be passed if parameter 'datetime' is None.")

        intensity = utils.clamp(intensity, 0, 1)
        intensity = utils.translate_ranges(intensity, 0, 1, CONFIGS.MINS["play_text"]["intensity"], CONFIGS.MAXS["play_text"]["intensity"])

        w, h = self.modified_img.size
        x_offset = w * CONFIGS.DEFAULTS["play_text"]["offset_multiplier"]
        y_offset = h * CONFIGS.DEFAULTS["play_text"]["offset_multiplier"]

        width_divided = w/CONFIGS.DEFAULTS["play_text"]["width_divider"]
        font_size = int(utils.pctg_to_value(intensity, width_divided))

        resulted_img = copy.deepcopy(self.modified_img)

        draw = ImageDraw.Draw(resulted_img)

        vhs_font_path = str(CONFIGS.PATHS["fonts"] / Path("VCR_OSD_MONO_1.001.ttf"))
        play_icon_path = str(CONFIGS.PATHS["fonts"] / Path("play_icon.ttf"))
        vhs_font = ImageFont.truetype(vhs_font_path, font_size)
        play_icon = ImageFont.truetype(play_icon_path, font_size)

        draw.text((x_offset, y_offset), "PLAY", (255,255,255), font=vhs_font)
        draw.text((x_offset + 2.2*font_size, y_offset), ">", (255,255,255), font=play_icon)
        draw.text((w - x_offset - 3*font_size, h - y_offset - font_size), "SP", (255,255,255), font=vhs_font)
        draw.text((w - x_offset - 3*font_size, y_offset), "--:--", (255,255,255), font=vhs_font)

        month = datetime.strftime("%h").upper()
        day = datetime.strftime("%0d")
        period = datetime.strftime("%p")
        hour = datetime.strftime("%0I")
        minute = datetime.strftime("%0M")

        datetime_str = "{}:{} {}\n{}. {} {}".format(hour, minute, period, month, day, datetime.year)

        draw.text((x_offset, h - y_offset - 2*font_size), datetime_str, (255,255,255), font=vhs_font)

        if inplace == False:
            return resulted_img
        else:
            self.modified_img = resulted_img



    def apply_all_effects(self, inplace=True, play_text=False, wave_warp=False):
        if isinstance(inplace, bool) == False:
            raise TypeError("Parameter 'inplace' must be a boolean.")
        if isinstance(play_text, bool) == False:
            raise TypeError("Parameter 'play_text' must be a boolean.")
        if isinstance(wave_warp, bool) == False:
            raise TypeError("Parameter 'wave_warp' must be a boolean.")

        undo_times = 4

        self.apply_noise_lines()
        self.apply_color_glitch()
        self.apply_horizontal_lines()
        self.apply_film_grain()

        if play_text == True:
            undo_times+=1
            self.apply_play_text()
        if wave_warp == True:
            self.apply_wave_warp()
            undo_times+=1

        if inplace==False:
            resulted_img = self.modified_img
            self.undo(undo_times)
            return resulted_img
