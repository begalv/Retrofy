# Retrofy

Python package that uses linear algebra to give a retro/VHS look to your photos.

## Instalation

Download the repository on your machine and execute the follow command on a terminal line:

```bash
python -m pip install -e <repository_path>
```

Or simply navigate to the folder where the repository is through terminal and execute the follow command:

```bash
python -m pip install -e ./Retrofy
```

## Quick Start

The simplest way to use the package is as follow:

```python
from retrofy import Retrowave

retrofier = Retrowave("YOUR_PHOTO_PATH") #you can use URLs for photos on the web
retrofier.apply_vhs_effects() #applies all effects that forms the VHS filter

retrofier.show() #shows the modiefied image so far
retrofier.save(path="YOUR_SAVE_PATH") #saves the modified image on the selected path
```
**Before:**

**After:**

Note that all effects used on this example used the default values as arguments. <br /><br /> If you want to adjust the arguments values, you can call the effects methods separately. <br /><br />


