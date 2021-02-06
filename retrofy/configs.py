from pathlib import Path
import os

DOWNLOADS_FOLDER = Path(os.path.expanduser("~")) / Path("Downloads/")



class Retrowave_Configs():

    PATHS = {
        "images": {
            ".": Path("./filterfy/filters/retrowave/images"),
            "noise_lines": Path("./filterfy/filters/retrowave/images/noise_lines")
        }
    }

    MAXS = {
        "noise_lines": {
            "iter": 30, #iterations
            "blur": 3,
            "bright": 2.5
        },
        "color_glitch": {
            "distortion": 10, #offset in pixels
        },
        "film_grain": {
            "blur": 1.5
        },
        "horizontal_lines": {
            "height_divider": 500,
            "blur": 2
        }
    }

    MINS = {
        "noise_lines": {
            "p_threshold": 0.99 #probability threshold for a random noise line to occur
        }
    }

    DEFAULTS = {
        "noise_lines":{
            "intensity": 0.4,
            "blur": 0.8,
            "bright": 0.6
        },
        "film_grain": {
            "gaussian_std": 100000
        }

    }
