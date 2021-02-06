import re
import os
from pathlib import Path
from collections.abc import Iterable


def is_url(string):
    if isinstance(string, str) == False:
        return False
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if re.match(regex, string) is not None:
        return True
    else:
        return False


def get_number_of_files(folder_path, formats):
    is_string = isinstance(folder_path, str)
    if (is_string == False and isinstance(folder_path, Path) == False) or isinstance(formats, Iterable) == False:
        return None

    if is_string == True:
        folder_path = Path(folder_path)
    if os.path.isdir(folder_path) == False:
        return None

    for i, format in enumerate(formats):
        formats[i] = format.strip().lower()

    files = []
    for name in os.listdir(folder_path):
        name_path = Path(name)
        if os.path.isfile(folder_path / name_path):
            if name_path.suffix.strip(".") in formats:
                files.append(name)
    return len(files)



def is_in_folder(folder_path, filename, format=None):
    is_folder_path_string = isinstance(folder_path, str)
    is_filename_string = isinstance(filename, str)

    if (is_folder_path_string == False and isinstance(folder_path, Path) == False) or (is_filename_string == False and isinstance(filename, Path) == False):
        return False, None

    if is_folder_path_string == True:
        folder_path = Path(folder_path)

    if os.path.isdir(folder_path) == False:
        return False, None

    if is_filename_string == True:
        filename = Path(filename)

    if filename.suffix == "" and format == None:
        return False, None
    elif format != None:
        filename = Path(filename.stem + ".{}".format(format))

    file_path = folder_path / filename

    is_in = os.path.isfile(file_path)
    if is_in == False:
        file_path = None
    return is_in, file_path


def clamp(n, minn, maxn):
    if n < minn:
        return minn
    elif n > maxn:
        return maxn
    else:
        return n


def pctg_to_value(pctg, max_value, min_value=0):
    value = pctg * max_value
    value = clamp(value, min_value, max_value)
    return value


def translate_ranges(value, from_min, from_max, to_min, to_max):
    # Figure out how 'wide' each range is
    from_range = from_max - from_min
    to_range = to_max - to_min

    # Convert the from range into a 0-1 range (float)
    value_scaled = float(value - from_min) / float(from_range)

    # Convert the 0-1 range into a value in the to range.
    return to_min + (value_scaled * to_range)
