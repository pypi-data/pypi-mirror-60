Lib: colours_library

Lead dev: Eryk Malczyk

Running from source code

pip install webcolors==1.3

pip install Pillow

pip install pytest  ---  runing tests with - pytest

INSTALLATION

pip install colours_library

----------------------------

USAGE

python3

------------>

from colours_library import colours

c = colours.MostCommonColor('path_to_image'
                            ,N(number of colors))

-------------------------------
Optional

To check current path/limit use print(c.get_path()/c.get_color_limit())

To change path/limit use c.set_path(new-Path)/c.set_color_limit()(new-Limit)


--------------------------------

c.produce()

-----------------------------
OUTPUT

List of N colours sorted by frequency.
