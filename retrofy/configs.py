from pathlib import Path
import os

DOWNLOADS_FOLDER = Path(os.path.expanduser("~")) / Path("Downloads/")



class VHS_Configs():

    SIZE = (705, 405)

    PATHS = {
        "images": {
            ".": Path("./retrofy/filters/vhs/images"),
            "noise_lines": Path("./retrofy/filters/vhs/images/noise_lines")
        },

        "fonts": Path("./retrofy/filters/vhs/fonts")

    }

    MAXS = {
        "noise_lines": {
            "iter": 30, #iterations
            "blur": 3,
            "bright": 2.5
        },
        "color_glitch": {
            "intensity": 0.7,
            "offset": 20
        },
        "film_grain": {
            "blur": 1.5
        },
        "horizontal_lines": {
            "blur": 2,
            "intensity": 0.9
        },
        "wave_warp": {
            "intensity": 0.9
        },
        "play_text": {
            "intensity": 0.8
        }
    }

    MINS = {
        "noise_lines": {
            "p_threshold": 0.99, #probability threshold for a random noise line to occur
            "intensity": 0.1
        },
        "color_glitch": {
            "intensity": 0.3,
            "offset": 3
        },
        "film_grain": {
            "intensity": 0.35
        },
        "horizontal_lines": {
            "intensity": 0.2
        },
        "wave_warp": {
            "intensity": 0.2
        },
        "play_text": {
            "intensity": 0.5
        }
    }

    DEFAULTS = {
        "noise_lines": {
            "intensity": 0.4,
            "blur": 0.8,
            "bright": 0.6
        },
        "color_glitch": {
            "intensity": 0.2,
            "height_divider": 95
        },
        "film_grain": {
            "gaussian_std": 100000,
            "intensity": 0.4,
            "blur": 0.3
        },
        "horizontal_lines": {
            "intensity": 0.4,
            "blur": 0.5,
            "height_divider": 2.5,
            "bright": 0.6
        },
        "wave_warp": {
            "intensity":0.6,
            "height_divider": 6
        },
        "play_text": {
            "offset_multiplier": 0.05,
            "width_divider": 12,
            "intensity": 0.3
        }

    }
