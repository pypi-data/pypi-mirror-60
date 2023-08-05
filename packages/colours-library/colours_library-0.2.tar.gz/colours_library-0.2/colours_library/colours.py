import webcolors
from PIL import Image
import sys
import re
"""
Input: image path and int n
Output: list of n most popular colours in given image
"""
def produce(*args):
    if args[1] < 1 or len(args) != 2:
        raise ValueError
    else:
        if not isinstance(args[0], str) or not isinstance(args[1], int) :
            raise TypeError
        else:
            return produce_colour_name_list(args[0], args[1])

def produce_colour_name_list(image, n):
    try:
        pixel_rgb_values = process_image_into_rgb_list(image)
        colour_dict = create_colour_dict(pixel_rgb_values)
        return limit_dict_to_final_output(colour_dict, n)
    except FileNotFoundError:
        print("file not found")
        return 1
    except TypeError:
        print("bad file format")
        return 2
def process_image_into_rgb_list(image):
    if re.search(r".*\.jpe?g", image):
        im = Image.open(image, 'r')
       # width, height = im.size
        pixel_rgb_values = list(im.getdata())
        return pixel_rgb_values
    else:
        raise TypeError

def create_colour_dict(pixel_rgb_values):
    color_dict = {}
    for i in range(len(pixel_rgb_values)):
        if(get_colour_name(pixel_rgb_values[i]) in color_dict):
            color_dict[get_colour_name(pixel_rgb_values[i])] += 1
        else:
            color_dict[get_colour_name(pixel_rgb_values[i])] = 1
    return color_dict

def limit_dict_to_final_output(color_dict, n):
    improved = sorted(color_dict, key=color_dict.get, reverse=True)
    final = []
    for i in range(n):
        final.append(improved[i])
    return final

def get_colour_name(requested):
    try:
        closest = webcolors.rgb_to_name(requested)
    except ValueError:
        closest = closest_colour(requested)
    return closest

def closest_colour(requested):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested[0]) ** 2
        gd = (g_c - requested[1]) ** 2
        bd = (b_c - requested[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

