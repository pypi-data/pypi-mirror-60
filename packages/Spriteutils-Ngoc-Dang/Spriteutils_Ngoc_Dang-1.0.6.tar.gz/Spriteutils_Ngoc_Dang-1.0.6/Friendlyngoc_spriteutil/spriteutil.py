#!/usr/bin/env python 3.6
"""IMPORTS"""
import random
import copy
import timeit
from PIL import Image
from PIL import ImageDraw
import numpy as np


BACKGROUND_LABEL = 0
RGB_TUPLE = 3
RGBA_TUPLE = 4
DEFAULT_RGB_BACKGROUND = (255, 255, 255)
RGB_MODE = 'RGB'
RGBA_MODE = 'RGBA'
P_MODE = "P"
L_MODE = "L"
LIST_OF_SUPPORTED_MODE = ['RGB','RGBA','L']


# Way_point2:
class Sprite:
    """A class represents a Sprite in an image"""
    def __init__(self, label, x1, y1, x2, y2):
        """The constructor method of the Class Sprite

        Args:
            label (int): the label
                of the dectected sprite
            x1 (int): x axis value
                of top left coordinates
            x2 (int): x axis value
                of bottom right coordinates
            y1 (int): y axis value
                of top left coordinates
            y2 (int): y axis value
                of bottom right cooridnates

        Raises:
            TypeError: If any of the params
                is not an integer
            ValueError: If any of the params
                is not an possitive ingeter
            If the coordinate of the top
                left is higher than the bottom right
        """
        # Inputs' type must be whole number
        # No negative integer is allowed
        list_check = [label, x1, y1, x2, y2]
        for integer_coordinates in list_check:
            if not isinstance(integer_coordinates, int):
                raise TypeError("Invalid coordinates")
            if integer_coordinates < 0:
                raise ValueError("Invalid coordinates")

        # top left coordinates must be lower than
        # right most corner coordinates
        if x1 > x2 or y1 > y2:
            raise ValueError("Invalid coordinates")

        self.__label = label # sprite label
        self.__top_left = x1,y1 # top left coordinates
        self.__bottom_right = x2,y2 # bottom right coordinates
        self.__witdth = x2 - x1 + 1
        self.__height = y2 - y1 + 1

    @property
    def top_left(self):
        """The property of top left attribute"""
        return self.__top_left

    @property
    def bottom_right(self):
        """The property of bottom right attribute"""
        return self.__bottom_right

    @property
    def label(self):
        """The property of label attribute"""
        return self.__label

    @property
    def width(self):
        """The number of piexel horizontally"""
        return self.__witdth

    @property
    def height(self):
        """The number of piexel vertically"""
        return self.__height


class SpriteSheet():
    def __init__(self, fd, background_color=None):

        if isinstance(fd, Image.Image):
            self.__fd = fd

        elif not isinstance(fd, Image.Image):
            try:
                self.__fd = Image.open(fd)
            except Exception:
                raise ValueError(
                    "input must be a path, file or Image object")

        if self.__fd.mode not in LIST_OF_SUPPORTED_MODE:
            raise ValueError(
                f"The image mode {self.__fd.mode} is not supported")

        if background_color is None:
            self.__background_color =\
                SpriteSheet.find_most_common_color(self.__fd)

        if background_color:
            fd_mode = self.__fd.mode
            len_background_color = len(background_color)

            if fd_mode is RGB_MODE:
                if not isinstance(background_color, tuple):
                    raise TypeError(
                        "The background color must be a tuple")
                if len_background_color != 3:
                    raise ValueError(
                        "RGB tuple must only have 3 intergers")
                if not all([i in range(256) for i in background_color]):
                    raise ValueError(
                        "All integer must range from 0 to 255")
                self.__background_color = background_color

            elif fd_mode is RGBA_MODE:
                if not isinstance(background_color, tuple):
                    raise TypeError(
                        "The background color must be a tuple")
                if len_background_color not in range(3,5):
                    raise ValueError(
                        "RGB tuple must only have 4 intergers")
                if len_background_color == 3:
                    self.__background_color = (
                        background_color[0],
                        background_color[1],
                        background_color[2],
                        255)
                elif len_background_color == 4:
                    self.__background_color = background_color

                if not all([i in range(256) for i in self.__background_color]):
                    raise ValueError("All integer must range from 0 to 255")

            elif fd_mode is L_MODE:
                if not isinstance(background_color, int)\
                    and background_color not in range(257):
                    raise ValueError(
                        "This mode color is single integer")
                self.__background_color = background_color


        self.__sprites, self.__label_map = self.__find_sprites()


    @staticmethod
    def find_most_common_color(image):
        """
        Args:
            image (obj): An Image object
            of the picture input

        Returns:
            The most used color in the
            picture in a tuple

        Raises:
            TypeError: If image is not
            an Image instance
        """
        # The total pixels in a picture is
        # equal to the multiplication of its
        # witdth and height
        image_width = image.width
        image_height = image.height
        total_pixel_image = image_width * image_height

        # getcolors returns a list of tuples
        # Inlcuding ratio and its color
        color_in_image = image.getcolors(
            total_pixel_image)

        # Sort the list based on the ratio
        # Reverse the order, meaning its from high to low
        # So the first value will be the most common used
        sorted_colors = sorted(
            color_in_image, key=lambda x: x[0], reverse=True)
        return sorted_colors[0][1]


    @property
    def background_color(self):
        return self.__background_color

    def __find_sprites(self):
        """
        Args:
            image (obj): An Image object
                of the picture input
            background_color (tuple): can be a tuple
                or integer depends on the image mode

        Returns:
            A tuple of sprites and label map

            sprites (dict): A collection of key-value
                pairs (a dictionary) where each key-value pair
                maps the key (the label of a sprite)
                to its associated value (a Sprite object);

            label_map (list): A 2D array of integers
                of equal dimension (width and height)
                as the original image
                where the sprites are packed in.
                The label_map array maps each pixel
                of the image passed to the function
                to the label of the sprite
                this pixel corresponds to,
                or 0 if this pixel doesn't belong
                to a sprite (e.g., background color).

        Raises:
            ValueError: If image is not
            an Image instance
            ValueError: If the background_color is provided
                but is not associated with the image mode
            For example:
                If image mode is "L" or "P" the background
                    if provided should be an integer
        """

        label_map = []
        dict_label = {}
        label_id = []
        label_background = 0
        count_id = 0
        list_of_coordinates = []

        for y in range(self.__fd.height):
            sprite_layers = []
            for x in range(self.__fd.width):
                pixel_colour = self.__fd.getpixel((x,y))

                # if background color is deceted
                if pixel_colour == self.__background_color:
                    if count_id == 0:
                        # Use a list hold that label to reuse in increasing stage
                        sprite_layers.append(
                                label_background)
                        # Only holds the background label(0) only 1 time
                        label_id.append(
                                label_background)
                        count_id += 1
                    else:
                        sprite_layers.append(
                                label_background)

                # if current pixel is forgeground
                elif pixel_colour != self.__background_color:
                    count = 0
                    while True:
                        # Check 4 connectivity based on previous layer
                        # from top left, top middle, top right and left
                        # If there is valid label in these position
                        # Take it, if none of these have label create a new label
                        try:
                            if count == 0:
                                new_label = label_map[-1][x-1]
                                if new_label != 0:
                                    sprite_layers.append(new_label)
                                else:
                                    count += 1
                            if count == 1:
                                new_label = label_map[-1][x]
                                if new_label != 0:
                                    sprite_layers.append(new_label)
                                else:
                                    count += 1
                            if count == 2:
                                new_label = label_map[-1][x+1]
                                if new_label != 0:
                                    sprite_layers.append(new_label)
                                else:
                                    count += 1
                            if count == 3:
                                new_label = sprite_layers[-1]
                                if new_label != 0:
                                    sprite_layers.append(new_label)
                                else:
                                    count += 1
                            if count == 4:

                                if len(label_id) == 0:
                                    label_sprite = 1
                                    label_id.append(label_sprite)
                                    sprite_layers.append(label_sprite)

                                else:
                                    # Increse the label because not connectivies
                                    label_sprite = sorted(label_id)[-1] + 1
                                    # fill this pixel with this new label
                                    sprite_layers.append(label_sprite)
                                    # Hold this new label on the label_id list
                                    # to use to increase the next one
                                    label_id.append(label_sprite)
                                # We also create a dict key with its value
                                # Since some might carry itself already
                                dict_label.setdefault(label_sprite,[label_sprite])

                            break
                        # Since some collumn index has no top position value
                        # Increase count to check left or create new one
                        except IndexError:
                            count += 1
                            continue

            # Append each layer to the label map list
            label_map.append(sprite_layers)

        # Only start the check from the second layer
        # Since the top will be background only or some main labels
        # Also, checking 8 connectivity is more available for this case
        label_map_height = len(label_map)
        label_map_width = len(label_map[1])
        for i in range(1, label_map_height-1):
            for a in range(label_map_width-1):
                # When meet a label
                if label_map[i][a] > 0:
                    current_label = label_map[i][a]
                    while True:
                        # Checking 8 connectivites but have to check all
                        # only append label that is not 0
                        # and not in the value of the current label in the dict
                        try:
                            new_label = label_map[i-1][a-1]
                            label_value = dict_label[current_label]
                            if new_label != label_background:
                                if new_label not in label_value:
                                    label_value.append(new_label)

                            new_label = label_map[i-1][a]
                            if new_label != label_background:
                                if new_label not in label_value:
                                    label_value.append(new_label)

                            new_label = label_map[i-1][a+1]
                            if new_label != label_background:
                                if new_label not in label_value:
                                    label_value.append(new_label)

                            new_label = label_map[i][a+1]
                            if new_label != label_background:
                                if new_label not in label_value:
                                    label_value.append(new_label)

                            new_label = label_map[i+1][a+1]
                            if new_label != label_background:
                                if new_label not in label_value:
                                    label_value.append(new_label)

                            new_label = label_map[i+1][a]
                            if new_label != label_background:
                                if new_label not in label_value:
                                    label_value.append(new_label)

                            new_label = label_map[i+1][a-1]
                            if new_label != label_background:
                                if new_label not in label_value:
                                    label_value.append(new_label)

                            new_label = label_map[i][a-1]
                            if new_label != label_background:
                                if new_label not in label_value:
                                    label_value.append(new_label)
                            break
                        # Same situation with corner pixel label
                        except IndexError:
                            continue

        # Get label equivalence with the reduce function
        new_dict_lable = self.__reduce_label(dict_label)

        # Looping over the label again to correct the labels
        for k in range(label_map_height):
            for a in range(label_map_width):
                if label_map[k][a] > 0:
                    label_map[k][a] = min(new_dict_lable[label_map[k][a]])
                    # At the same time get all the cooridnates with label
                    # in a format of a tuple (label, x, y)
                    list_of_coordinates.append((label_map[k][a], a, k))

        # Create an nupy array based on the list of tuples above
        # This will be 2d array with records as the tuples
        # first, second, third collumns will be label, its X, its Y
        data = np.array(list_of_coordinates)

        # Get the uniqe of the first collumns
        # which are the labels after refined of the label map
        list_of_final_labels = np.unique(data[:,0])

        # Find the min X, min Y, max X, max Y based on the label
        # basially similar to groupby in SQL
        top_left_bottom_right = np.array(
            [list(
                (min(data[data[:,0]==i,1]),
                min(data[data[:,0]==i,2]),
                max(data[data[:,0]==i,1]),
                max(data[data[:,0]==i,2])))
                for i in list_of_final_labels])

        # Create the sprites dictionary to return
        sprites = {}
        for i in range(len(list_of_final_labels)):
            sprites[list_of_final_labels[i]] =\
                Sprite(
                    int(list_of_final_labels[i]),
                    int(top_left_bottom_right[i][0]),
                    int(top_left_bottom_right[i][1]),
                    int(top_left_bottom_right[i][2]),
                    int(top_left_bottom_right[i][3]))

        return (sprites, label_map)


    def __reduce_label(self, key_dict):
        """
        Args:
            key_dict (dict): A dict of labels and
                associated connected label

        Returns:
            A dictionary with maximum redction of
                label equivalence

        Raises:
            TypleError: If key_dict is not a dictionary
        """
        # Validation for dictionary argument
        if not isinstance(key_dict, dict):
            raise TypeError(
                "Argument must be a dictionary")

        count = 0
        while True:
            # Firstly check if the key in the value of another key
            # if so, append the min of the key to the other key value
            for i in key_dict:
                for key,value in key_dict.items():
                    if i in value and min(key_dict[i]) not in value:
                        key_dict[key].append(min(key_dict[i]))

            # After reduce compare it to previous one
            # Both match every single key, meaning it is fully reduced
            # return the reduced dictionary
            # else, keep reducing until the previous is equal to the new one
            if count > 0:
                if all(key_dict[key] == key_dict_copy[key] for key in key_dict):
                    return key_dict

            # Create a deep copy after each reduction
            # Deep copy is used because shallow will keep a pointer
            key_dict_copy = copy.deepcopy(key_dict)
            count += 1


    def find_sprites(self):
        return self.__sprites,self.__label_map


    def __random_color_generator(self, len_background_color):
        """
        Args:
            len_background_color (int): a length of
                the tuple of background_color
                argument passed to
                create_sprite_labels_image function

        Returns:
            A tuple of 3 to 4 random integers range from
                0 to 256
            In the case of 3, meaning the background color
                is on RGB mode
            In the case of 4, the last integer which is the alpha

        Raises:
            TypleError: If len_background_color is not
                an integer
        """
        if len_background_color == RGB_TUPLE:
            return (random.choice(range(256)),
                    random.choice(range(256)),
                    random.choice(range(256)))

        if len_background_color == RGBA_TUPLE:
            return (random.choice(range(256)),
                    random.choice(range(256)),
                    random.choice(range(256)),
                    random.choice(range(200, 256)))


    def create_sprite_labels_image(self, background_color=DEFAULT_RGB_BACKGROUND):
        """
        Args:
            sprites (dict): a dictionary which is returned from
                find sprites function which is a dictionary of
                key as label and value as its Sprite object
            label_map (list): a 2d dimension which is a list of
                lists, which represents the sprite sheet and each
                sprites within seperated by label (integer)
            background_color (tuple): either a tuple (R, G, B)
                or a tuple (R, G, B, A) that identifies the color
                to use as the background of the image to create.
                If nothing is passed, the default value is
                (255, 255, 255)

        Returns:
            An image object that has all the sprites seperated
                in bounding boxes drawed with distinct colors

        Raises:
            ValueError:
                If the background_color argument is not a tuple
                If the background_color argument has more
                    than 4 and less than 3
                If there is a negative integer within the tuple
                If there is an positive integer greater than 255
        """
        sprites, label_map = self.find_sprites()
        # Validation for sprites and label_map arguments
        if not isinstance(background_color, tuple):
            raise TypeError(
                "Background color must be a tuple")

        # Validation for background_color if it is passed on
        if background_color:
            if len(background_color) not in range(3, 5):
                raise ValueError(
                    "background color must be a tuple of 3 or 4")
            if not all([i in range(256) for i in background_color]):
                raise ValueError(
                    "All integer must range from 0 to 255")

        # sprite sheet size = height * width
        # since label_map represent sprite sheet
        # height = len(label_map)
        # width = len(label_map(list_inside_label_map))
        image_size = self.__fd.size
        background_color_mode_len = len(background_color)

        # Set the mode according to background passed
        if background_color_mode_len == RGB_TUPLE:
            image_mode = RGB_MODE
        elif background_color_mode_len == RGBA_TUPLE:
            image_mode = RGBA_MODE

        # if length of background color is 3,
        # create a new image with RGB mode, 4 for RGBA mode
        # Create an object to draw in a image object created
        new_image = Image.new(
            image_mode,
            image_size,
            background_color)
        draw = ImageDraw.Draw(
            new_image,
            mode=image_mode)

        dict_of_colors = {}
        for i in sprites:
            # gerenate a random color (tuple of integers)
            outline_color = self.__random_color_generator(
                                            background_color_mode_len)

            # In the case if the background color is insert has the same color
            # with an outline color, we run another loop to find a new one
            if outline_color == background_color:
                while True:
                    outline_color = self.__random_color_generator(
                                            background_color_mode_len)
                    if outline_color != background_color:
                        break

            # create keys include label and top left, bottom right
            # coordinate as keys and cooresponding colors
            dict_of_colors[i] = outline_color
            dict_of_colors[sprites[i].top_left,
                           sprites[i].bottom_right]\
                               = outline_color

        # Go through the label map to color the sprites
        for y in range(len(label_map)):
            for x in range(len(label_map[y])):
                if label_map[y][x] != 0:
                    # fill the color of the pixel based on label
                    # and that label value in the dict_of_colors
                    draw.point((x, y),
                            fill=dict_of_colors[label_map[y][x]])

        # Draw the bounding box for each sprites
        for i in sprites:
            top_left = sprites[i].top_left
            bottom_right = sprites[i].bottom_right

            # Use top left and bottom right attribute with reactangle
            # to draw the bounding box
            # The outline has to have the same color with the sprite
            # Meaning it is based on the value of the cooridinates
            # in dict_of_colors dictionary
            draw.rectangle(
                [top_left, bottom_right],
                outline=dict_of_colors[top_left, bottom_right])
        return new_image


def main():
    pass

if __name__ == "__main__":
    main()