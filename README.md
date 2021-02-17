# Retrofy

Python package that uses linear algebra to give a retro/VHS look to your photos.

## Instalation

Download the repository on your machine and execute the follow command on a terminal line:

```bash
python -m pip install -e <repository_path>
```

Or simply navigate to the folder where the repository is and execute the follow command:

```bash
python -m pip install -e ./Retrofy
```

## Quick Start

The simplest way to use the package is as follow:

```python
from retrofy import VHS

retrofier = VHS("YOUR_PHOTO_PATH") #you can use URLs for photos on the web or Pillow Image Objects as well
retrofier.apply_all_effects() #applies all effects that forms the VHS filter

#OR you can do it with inplace = False
resulted_img = retrofier.apply_all_effects(inplace=False)

#OR with some extra effects:
retrofier.apply_all_effects(play_text=True, wave_warp=True) #to apply the VHS "play" text on the image and the wave warp effect on a random row on the image

retrofier.show() #shows the modiefied image so far
retrofier.save(path="YOUR_SAVE_PATH") #saves the modified image on the selected path
```
**Before:**
![Alt](https://github.com/begalv/Retrofy/blob/main/docs/images/before.jpg)
**After:**
![Alt](https://github.com/begalv/Retrofy/blob/main/docs/images/after.png)

Note that all effects used on this example used default values as arguments. <br /><br /> If you want to adjust the arguments values, you can call the effects methods separately. <br /><br /> For more information, look at the examples folder.
