import webcolors
from PIL import Image
import sys
import re
"""
Input: image path and int n
Output: list of n most popular colours in given image
"""

class MostCommonColor:
    def __init__(self, path, color_limit=5):
        self._path = path
        self.limit = color_limit

    def produce(self):
        if self.limit < 1:
             raise ValueError
        else:
            if isinstance(self._path, str) and isinstance(self.limit, int) :
                return self.produce_colour_name_list(self._path, self.limit)
            else:
                raise TypeError

    def produce_colour_name_list(self, image, n):
        try:
            pixel_rgb_values = MostCommonColor.process_image_into_rgb_list(image)
            print('rgb list created')
            colour_dict = self.create_colour_dict(pixel_rgb_values)
            print('colour dict created')
            return MostCommonColor.limit_dict_to_final_output(colour_dict, n)
        except FileNotFoundError:
            print("file not found")
            return 1
        except TypeError:
            print(TypeError)
            return 2

    @staticmethod
    def process_image_into_rgb_list(image):
        if re.match(r".*\.jpe?g", image):
            im = Image.open(image, 'r')
            pixel_rgb_values = list(im.getdata())
            return pixel_rgb_values
        else:
            print('there it is')
            raise TypeError
        
    def create_colour_dict(self, pixel_rgb_values):
        color_dict = {}
        for i in range(len(pixel_rgb_values)):
            temporary = self.get_colour_name(pixel_rgb_values[i])
            if temporary in color_dict:
                color_dict[temporary] += 1
            else:
                color_dict[temporary] = 1
        return color_dict

    @staticmethod
    def limit_dict_to_final_output(color_dict, n):
        improved = sorted(color_dict, key=color_dict.get, reverse=True)
        final = []
        for i in range(n):
            final.append(improved[i])
        return final

    def get_colour_name(self, requested):
        try:
            closest = webcolors.rgb_to_name(requested)
        except ValueError:
            closest = self.closest_colour(requested)
        return closest

    @staticmethod
    def closest_colour(requested):
        min_colours = {}
        for key, name in webcolors.css3_hex_to_names.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - requested[0]) ** 2
            gd = (g_c - requested[1]) ** 2
            bd = (b_c - requested[2]) ** 2
            min_colours[(rd + gd + bd)] = name
        return min_colours[min(min_colours.keys())]

#if __name__ == '__main__':
#    mcc = MostCommonColor('white.jpg', 1)
#    print(mcc.produce())