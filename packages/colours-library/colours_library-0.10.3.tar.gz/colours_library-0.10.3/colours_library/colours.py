import webcolors
from PIL import Image
from pathlib import Path
import sys
import re
import time
"""
Input: image path and int n
Output: list of n most popular colours in given image
"""

class MostCommonColor:
    def __init__(self, *args):
        if len(args) != 2 or args[1] < 1:
            raise ValueError
        self._path = args[0]
        self.limit = args[1]

#Getters Setters and validation of input
    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        if isinstance(path, str):
            self._path = path
        else:
            raise TypeError

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, limit):
        if not isinstance(limit, int):
            raise TypeError
        else:
            self._limit = limit

    def get_path(self):
        return self.path

    def get_color_limit(self):
        return self.limit

    def set_path(self, path):
        self.path = path

    def set_color_limit(self, limit):
        self.limit = limit

#Function that initializes main process
    def produce(self):
        return self.produce_colour_name_list(self._path, self.limit)
       
    def produce_colour_name_list(self, image, n):
        try:
            #RGB list
            pixel_rgb_values = MostCommonColor.process_image_into_rgb_list(image)
            #Dict of colors
            colour_dict = self.create_colour_dict(pixel_rgb_values)
            #Returning final dict limited to n colors
            return MostCommonColor.limit_dict_to_final_output(colour_dict, n)
        except FileNotFoundError:
            return 1
        except TypeError:
            return 2

    @staticmethod
    def process_image_into_rgb_list(image):
        #check image format
        if re.match(r".*\.jpe?g", image):
            #open img object
            im = Image.open(image, 'r')
            #resizing to reduce time
            im = im.resize((150,150))
            #populate and return list of rgb's
            pixel_rgb_values = list(im.getdata())
            return pixel_rgb_values
        else:
            raise TypeError
        
    def create_colour_dict(self, pixel_rgb_values):
        color_dict = {}
        #we instantiate and populate our color dict
        for i in range(len(pixel_rgb_values)):
            temporary = self.get_colour_name(pixel_rgb_values[i])
            if temporary in color_dict:
                color_dict[temporary] += 1
            else:
                color_dict[temporary] = 1
        return color_dict

    @staticmethod
    def limit_dict_to_final_output(color_dict, n):
        #we sort our colordict
        improved = sorted(color_dict, key=color_dict.get, reverse=True)
        final = []
        #we take n most frequent colors
        for i in range(n):
            final.append(improved[i])
        return final

    def get_colour_name(self, requested):
        try:
            #if color is in webcolors colordict we assign it to our variable
            closest = webcolors.rgb_to_name(requested)
        except ValueError:
            #if it's not we find closest to it
            closest = self.closest_colour(requested)
        return closest

    @staticmethod
    def closest_colour(requested):
        min_colours = {}
        #iterating over color dict from webcolors library
        for key, name in webcolors.css3_hex_to_names.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            #finding lowest difference in RGB from requested to colors in library
            rd = (r_c - requested[0]) ** 2
            gd = (g_c - requested[1]) ** 2
            bd = (b_c - requested[2]) ** 2
            sum_of_rgb_difference = rd + gd + bd 
            min_colours[(sum_of_rgb_difference)] = name
        return min_colours[min(min_colours.keys())]

#main mock for testing
#if __name__ == '__main__':
#    start = time.time()
#    mcc = MostCommonColor('/home/eryk/klimt.jpg', 5)
#    print(mcc.produce())
#    print(time.time() - start)