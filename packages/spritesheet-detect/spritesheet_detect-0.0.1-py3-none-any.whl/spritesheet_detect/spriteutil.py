#!/usr/bin/env python3
"""A practice for Image Parsing"""
import logging
from operator import itemgetter
import random
from PIL import Image, ImageDraw
import numpy as np


# Set logging
logging.basicConfig(level=logging.ERROR, filemode='w')

COLOR_MODE = {"RGB": 3, "RGBA": 4}
COLOR = {"WHITE": (255, 255, 255)}

# Waypoint 2: Write a Class Sprite


class Sprite:
    """Class represent a sprite in sheet"""

    def __init__(self, label, x1, y1, x2, y2):
        """The constructor for Sprite class

        Parameters:
            label (int) a whole number presented to label of the sprite
            x1 (int) a whole number presented x-coordinates of the top-left point
            y1 (int) a whole number presented y-coordinates of the top-left point
            x2 (int) a whole number presented x-coordinates of the bottom_right point
            y2 (int) a whole number presented y-coordinates of the bottom_right point
        """

        # Data validation
        if any([not isinstance(x, int) or x <
                0 for x in [label, x1, y1, x2, y2]]):
            logging.error("Invalid values")
        if x2 < x1 or y2 < y1:
            logging.error("Invalid coordinates")
        self.__label = label
        self.__top_left = (x1, y1)
        self.__bottom_right = (x2, y2)
        self.__height = y2 - y1 + 1
        self.__width = x2 - x1 + 1

    @property
    def label(self):
        """Label of Sprite"""
        return self.__label

    @property
    def top_left(self):
        """Coordinates of top left corner point of the sprite"""
        return self.__top_left

    @property
    def bottom_right(self):
        """Coordinates of bottom right corner point of the sprite"""
        return self.__bottom_right

    @property
    def height(self):
        """The number of pixels horizontally of the sprite"""
        return self.__height

    @property
    def width(self):
        """The number of pixels vertically of the sprite"""
        return self.__width


class SpriteSheet:
    """Class SpriteSheet define all Sprite on image"""

    def __init__(self, fd, background_color=None):

        if isinstance(fd, Image.Image):
            self.__image = fd
        else:
            try:
                self.__image = Image.open(fd)
            except Exception:
                raise Exception("Can not open this file")

        # Define background color
        if background_color:
            if not isinstance(background_color, (tuple, int)):
                raise TypeError("Must be an integer or a tuple")
            if isinstance(background_color, tuple) and\
                    all([len(background_color) != x for x in [3, 4]]):
                raise ValueError(
                    "Must be an tuple of 3-component or 4-component integers")
            if isinstance(background_color, tuple) and\
                    not all([isinstance(x, int) for x in background_color]):
                raise ValueError(
                    "Must be an tuple of 3-component or 4-component integers")
            if isinstance(background_color, tuple) and not all(
                    [0 <= x <= 255 for x in background_color]):
                raise ValueError("3-component integers must be in range 0-255")

        self.__background_color = background_color
        self.label_map = []
        self.sprites = {}

    @property
    def background_color(self):
        """Background color of SpriteSheet"""
        if not self.__background_color:
            return self.find_most_common_color(self.__image)
        return self.__background_color

    @property
    def image(self):
        """Image object of SpriteSheet"""
        return self.__image

    @staticmethod
    # Waypoint 1: Find the Most Common Color in an Image
    def find_most_common_color(image):
        """Find the Most Common Color in an Image

        Arguments:
            image: Image.Image object

        Raises:
            ValueError: arg is not an image object

        Returns:
            A tuple of pixel value
        """

        # Data valid
        if not isinstance(image, Image.Image):
            raise ValueError("Not an Image object")

        # Get width and height of image
        width, height = image.size

        # Get a list of all pixel colors of the picture
        pixel_values_list = list(image.getcolors(maxcolors=width * height))

        # Return the pixel value with the largest label_mapuency
        return max(pixel_values_list, key=itemgetter(0))[1]

    # Waypoint 3: Find Sprites in an Image

    def find_sprites(self):
        """Find sprites of sprite sheet

        Arguments:
            image: Image.Image object

        Raises:
            TypeError: argument is not an Image.Image object

        Returns: tuple (sprites, label_map)
            sprites: (dict)
                the key (int): the label of a sprite
                value (a Sprite object)
            label_map (list): A 2D array of integers of equal dimension (width and height)
                as the original image where the sprites are packed in.
        """

        image = self.image
        # Get background color of spritesheet
        image_width, image_height = image.size

        # Create an array to store result
        label_map = np.zeros(shape=(image_height, image_width), dtype=np.int)

        # Get an pixel colors array
        pixel_col_arr = image.load()

        # Update label map by assign new label
        center_point = 0
        last_label = self.__update_label_map_from_neighbor_pixels(
            image,
            label_map,
            pixel_col_arr,
            center_point)

        # Get a dictionary neighbor labels
        equivalent_label_dict = self.__get_label_equivalent_dict(
            image, last_label, label_map)

        # Get label ID from equivalent labels
        label_equivalence_dict = self.__get_labelid_from_equivalent_label(
            equivalent_label_dict)

        # Initialize sprites dict to store top-left and bottom right points
        sprites_dict = {}
        for key in label_equivalence_dict:
            sprites_dict.setdefault(key, []).append(
                [0, 0, image_width, image_height])

        # Replace label as equivalent table
        for key, values in label_equivalence_dict.items():
            for value in values:
                label_map[label_map == value] = key

        # Find bottom right and top left points
        for key in label_equivalence_dict:
            # Create array of coordinator of each keys
            label_index = np.where(label_map == key)
            list_of_label_index = list(zip(label_index[0], label_index[1]))
            sprites_dict.setdefault(key, []).append(
                [0, 0, image_width, image_height])
            for index in list_of_label_index:
                if index[0] < sprites_dict[key][0][3]:
                    sprites_dict[key][0][3] = index[0]
                if index[1] < sprites_dict[key][0][2]:
                    sprites_dict[key][0][2] = index[1]

                if index[0] > sprites_dict[key][0][1]:
                    sprites_dict[key][0][1] = index[0]
                if index[1] > sprites_dict[key][0][0]:
                    sprites_dict[key][0][0] = index[1]

        # Get sprite objects and store them to dict
        for label, coordinates in sprites_dict.items():
            sprite = Sprite(
                int(label), int(
                    coordinates[0][2]), int(
                    coordinates[0][3]), int(
                    coordinates[0][0]), int(
                    coordinates[0][1]))
            sprites_dict[label] = sprite

        # Update sprites and label map to object
        self.sprites = sprites_dict
        self.label_map = label_map

        return (sprites_dict, label_map)

    @staticmethod
    def __get_labelid_from_equivalent_label(label_dict):
        """Get label id from equivalent label

        Arguments:
            label_dict (dict): a dictionary store all equivalent label dict

        Returns:
            An Updated dictionary from old dict
        """
        label_list = label_dict.values()
        # A dict Store final result
        result_dict = {}

        while len(label_list) > 0:
            # Take the first list and the rest (nested list) to compare them
            first, *rest_list = label_list
            first = set(first)
            # Run until could not merge the first_temp list more
            temp_len = -1
            while len(first) > temp_len:
                temp_len = len(first)
                temp_list = []
                for lst in rest_list:
                    # Check if any common elemnt exists:
                        #   If yes, merge into first list
                        #   In no, add to other list
                    if len(first.intersection(set(lst))) > 0:
                        first = first | set(lst)
                    else:
                        temp_list.append(lst)
                # Update rest_list to continute merge
                rest_list = temp_list

            # Add the list which is merged
            result_dict[min(list(first))] = list(first)

            # Update label list to the rest_list which have not yet merged
            label_list = rest_list

        return result_dict

    def __update_label_map_from_neighbor_pixels(
            self,
            image,
            label_map,
            pixel_col_arr,
            center_point):
        """ To update center point base on 8-neighborhood pixel connectivity

        Arguments:
            center_point: (tuple) (x, y) coordinates of the center_point
            image: Image.Image object
            label_map: 2D array of label map of image
            pixel_col_arr: 2D array of color pixel of the image

        Returns:
            label of center center_point
        """
        image_width, image_height = image.size
        background_color = self.background_color
        # Add neighbor points to list
        for row in range(image_height):
            for col in range(image_width):
                # Center point is foreground
                current_pixel = pixel_col_arr[col, row]

                # Skip colors which are back ground
                if current_pixel == background_color:
                    continue

                if image.mode == 'RGBA' and current_pixel[-1] == 0:
                    continue

                neighbor_points = [
                    (row - 1, col - 1),
                    (row - 1, col),
                    (row - 1, col + 1),
                    (row, col - 1)]

                for point in neighbor_points:
                    try:
                        neighbor_label = label_map[point[0]][point[1]]

                    except IndexError:
                        continue
                    if neighbor_label:
                        label_map[row][col] = neighbor_label
                        # No need to loop all 4 neighbor point if exist point
                        break

                else:
                    center_point += 1
                    label_map[row][col] += center_point

        return center_point

    def __get_label_equivalent_dict(self, image, last_label, label_map):
        """ Get a dictionay of relevant label

        Arguments:
            image: Image.Image object
            last_label: (int) the last label which is assign before
            label_map: (numpy array) array of labels

        Returns:
            a dictionay of relevant label
        """

        image_width, image_height = image.size
        equivalent_label_dict = {}
        for key in range(1, last_label + 1):
            equivalent_label_dict.setdefault(key, [key])

        # Get neighbor table
        for row in range(image_height):
            for col in range(image_width):
                current_label = label_map[row, col]
                neighbor_points = [
                    (row - 1, col - 1),
                    (row - 1, col),
                    (row - 1, col + 1),
                    (row, col - 1)
                ]

                if current_label != 0:
                    for point in neighbor_points:
                        try:
                            neigh_label = label_map[point[0], point[1]]
                        except IndexError:
                            continue
                        if neigh_label != 0:
                            if neigh_label not in equivalent_label_dict[current_label]:
                                equivalent_label_dict[current_label].append(
                                    neigh_label)

        return equivalent_label_dict

    # Waypoint 4: Draw Sprite Label Bounding Boxes
    def create_sprite_labels_image(self, background_color=COLOR["WHITE"]):
        """Draw Sprite Label Bounding Boxes

        Arguments:
            sprites (dict): sprites: each key-value pair maps the key (the label of a sprite)
                to its associated value (a Sprite object);
            label_map (list) A 2D array of integers of equal dimension (width and height)
                as the original image where the sprites are packed in.

        Keyword Arguments:
            background_color (tuple) (default: {(255, 255, 255)})
                a tuple (R, G, B) or a tuple (R, G, B, A)) that identifies the color
                to use as the background of the image to create.
        """
        sprites, label_map = self.find_sprites()

        # Background color must be an int or appropriate tuple
        if background_color:
            if not isinstance(background_color, (int, tuple)):
                raise ValueError("Must be a tuple or integer type")
            if all([len(background_color) != x for x in [3, 4]]):
                raise ValueError(
                    "Must be an tuple of 3-component or 4-component integers")
            if not all([isinstance(x, int) for x in background_color]):
                raise ValueError(
                    "Must be an tuple of 3-component or 4-component integers")
            if not all([0 <= x <= 255 for x in background_color]):
                raise ValueError("3-component integers must be in range 0-255")

        # Get image mode based on the color mode if origin image
        image_mode = "RGB" if len(background_color) == 3 else "RGBA"

        # Create a image to draw all sprite sheets
        new_sprite_sheet = Image.new(
            image_mode,
            (label_map[:].shape[1],
             label_map[:].shape[0]),
            background_color)
        draw = ImageDraw.Draw(new_sprite_sheet)

        for label, sprite in sprites.items():
            # Get top-left and bottom-right coordinates of each sprite
            top_left_coordinate = sprite.top_left
            bottom_right_coordinate = sprite.bottom_right

            # Get each sprite color by random
            sprite_color = tuple([random.randint(0, 255) for _ in range(0, 3)])

            # Get coordinates of each sprites
            label_coordinate = np.where(label_map == label)
            list_of_label_coordinate = list(
                zip(label_coordinate[1], label_coordinate[0]))

            # Draw point as list of label coordinates
            draw.point(list_of_label_coordinate, fill=sprite_color)

            # Draw rectangle
            draw.rectangle([top_left_coordinate,
                            bottom_right_coordinate],
                           outline=sprite_color)

        return new_sprite_sheet
