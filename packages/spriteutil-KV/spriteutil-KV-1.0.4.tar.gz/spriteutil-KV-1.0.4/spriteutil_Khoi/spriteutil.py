#!/usr/bin/env python
import timeit
from PIL import Image, ImageDraw
import time
from random import randint

class Sprite:
    '''
    Write a class Sprite which constructor takes 5 arguments label, x1, y1, x2, and y2
    '''
    def __init__(self, label, x1, y1, x2, y2):
        '''
        These arguments are used to initialize private attributes of the class Sprite.
        '''
        # raises an exception ValueError if:
        #       label, x1, y1, x2, and y2 is not positive integer
        #       x2 and y2 is not equal or greater respectively than x1 and y1
        #       label, x1, y1, x2, and y2 is a string
        for i in label, x1, y1, x2, y2:
            if isinstance(i, str) or i < 0:
                raise ValueError('Invalid coordinates')

        if x1 > x2 or y1 > y2:
            raise ValueError('Invalid coordinates')

        self.__label = label
        self.__x1 = x1
        self.__y1 = y1
        self.__x2 = x2
        self.__y2 = y2
        self.__top_left = (x1, y1)
        self.__bottom_right = (x2, y2)
        self.__width = x2 - x1 + 1
        self.__height = y2 - y1 + 1

    @property
    def label(self):
        '''
        @return: label
        '''
        return self.__label

    @property
    def x1(self):
        '''
        @return: x1
        '''
        return self.__x1

    @property
    def x2(self):
        '''
        @return: x2
        '''
        return self.__x2

    @property
    def y1(self):
        '''
        @return: y1
        '''
        return self.__y1

    @property
    def y2(self):
        '''
        @return: y2
        '''
        return self.__y2

    @property
    def top_left(self):
        '''
        @return: a tuple (x1,y1)
        '''
        return self.__top_left

    @property
    def bottom_right(self):
        '''
        @return: a tuple (x2,y2)
        '''
        return self.__bottom_right

    @property
    def width(self):
        '''
        @return: respectively the number of pixels horizontally
        '''
        return self.__width

    @property
    def height(self):
        '''
        @return: respectively the number of pixels vertically
        '''
        return self.__height



class SpriteSheet:
    def __init__(self, fd, background_color=None):
        self.__background_color = background_color

        if isinstance(fd, Image.Image):
            self.image_object = fd

        elif not isinstance(fd, Image.Image):
            try:
                self.image_object = Image.open(fd)
            except Exception:
                raise ValueError("can't create object")    
    
    @property
    def background_color(self):
        """
        get background_color
        return: a tuple
        """
        # if background_color is None, return find_most_common_color to get color of background
        # if background_color is not None, check some validation and return backgound_color
        if self.__background_color == None:
            self.__background_color = SpriteSheet.find_most_common_color(self.image_object)
            return self.__background_color
        
        else:
            # check validation:
                # + background_color must be tuple
                # + element in background_color must be integer
                # + element in background_color  must be integer (0, 255)
            if self.image_object.mode == 'L':
                if len(self.__background_color) != 1:
                    raise ValueError('mode is grayscale must be return an integer')
                if not isinstance(self.__background_color, tuple):
                    raise TypeError("background_color must be a tuple.")
                for i in self.__background_color:
                    if not isinstance(i, int):
                        raise ValueError('must be integer')
            
            elif self.image_object.mode == 'RGB':
                if len(self.__background_color) != 3:
                    raise ValueError('mode is RGB must be return a tuple (red, green, blue)')
                if not isinstance(self.__background_color, tuple):
                    raise TypeError("background_color must be a tuple.")
                for i in self.__background_color:
                    if not isinstance(i, int):
                        raise ValueError('red, green, blue must be integer')
                    if 255 < i or i < 0:
                        raise ValueError('(red, green, blue) must be integer (0, 255)')

            elif self.image_object.mode == 'RGBA':
                if len(self.__background_color) != 4:
                    raise ValueError('mode is RGBA must be return a tuple (red, green, blue, alpha)')
                if not isinstance(self.__background_color, tuple):
                    raise TypeError("background_color must be a tuple.")
                for i in self.__background_color:
                    if not isinstance(i, int):
                        raise ValueError('red, green, blue, alpha must be integer')
                    if 255 < i or i < 0:
                        raise ValueError('(red, green, blue, alpha) must be integer (0, 255)')
            
            else:
                raise ValueError('mode is not supported')        
    
            return self.__background_color

    @staticmethod
    def find_most_common_color(image):
        '''
        Write a function find_most_common_color that takes an argument image (a Image object) and that returns the pixel color that is the most used in this image.
        @param: image (a Image object)
        @return: the pixel color that is the most used in this image
            an integer if the mode is grayscale;
            a tuple (red, green, blue) of integers (0 to 255) if the mode is RGB;
            a tuple (red, green, blue, alpha) of integers (0 to 255) if the mode is RGBA.
        '''
        #open image and get size(width, height)
        width, height = image.size
        # mode is RGB --> use getcolors to get color is the most used with a tuple (red, green, blue)
        # mode is RGB --> use getcolors to get color is the most used with a tuple (red, green, blue, alpha)
        # mode is L(grayscale) --> return an integer
        return max(image.getcolors(width*height))[1]



    def find_sprites(self):
        '''
        Write a function find_sprites that takes an argument image (an Image object).
        This function accepts an optional argument background_color (an integer if the image format is grayscale, or a tuple (red, green, blue) 
                if the image format is RGB) that identifies the background color (i.e., transparent color) of the image. 
                The function ignores any pixels of the image with this color.
        If this argument background_color is not passed, the function determines the background color of the image as follows:
                1. The image, such as a PNG file, has an alpha channel: the function ignores all the 
                        pixels of the image which alpha component is 0;
                2. The image has no alpha channel: the function identifies the most common color of 
                        the image as the background color (cf. our function find_most_common_color).
        @Return:
            sprites: A collection of key-value pairs (a dictionary) where each key-value pair maps 
                the key (the label of a sprite) to its associated value (a Sprite object);
            label_map: A 2D array of integers of equal dimension (width and height) as the original image 
                where the sprites are packed in. The label_map array maps each pixel 
                of the image passed to the function to the label of the sprite this pixel corresponds to, 
                or 0 if this pixel doesn't belong to a sprite (e.g., background color).
        '''
        # get width and height of image and find most common color
        image = self.image_object
        max_width = image.width
        max_height = image.height
        background_color = SpriteSheet(image).background_color

        if image.mode is 'P':
            raise ValueError('The image mode P is not supported')


        #create label map with all elements has value are 0
        label_map = [[0 for i in range(image.width)] for j in range(image.height)]

        # Get color of all pixel
        # Check if color of pixel is not color of background --> take this pixel to check color of neighbours
        four_position = [[-1, -1], [0, -1], [1, -1], [-1, 0]]
        label = 0
        for h in range(image.height):
            for w in range(image.width):
                temporary_labels = []
                if image.getpixel((w, h)) != background_color:
                    # check if color of neighbours is not color of background --> set label
                    # Check if color of neighbours is color of background --> increase label
                    for i in four_position:
                        pixel_neighbours = (w + i[0], h + i[1])
                        if 0 <= pixel_neighbours[0] < max_width - 1 and 0 <= pixel_neighbours[1] < max_height - 1:

                            if image.getpixel(pixel_neighbours) != background_color:

                                if label_map[pixel_neighbours[1]][pixel_neighbours[0]] != 0:
                                    temporary_labels.append(label_map[pixel_neighbours[1]][pixel_neighbours[0]])

                    if len(temporary_labels) == 0:                    
                        label_map[h][w] = label = label + 1
                    else:
                        label_map[h][w] = min(temporary_labels)



        # Check 8 position around pixel
        value_of_position = {}
        eight_position = [[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]
        for h in range(image.height):
            for w in range(image.width):

                if label_map[h][w] > 0:

                    for i in eight_position:
                        pixel_neighbours = (w + i[0], h + i[1])

                        # if position around pixel != 0 --> use setdefault to positions around pixel to dictionary          
                        if 0 <= pixel_neighbours[0] < max_width - 1 and 0 <= pixel_neighbours[1] < max_height - 1:

                            if label_map[pixel_neighbours[1]][pixel_neighbours[0]] != 0:
                                value_of_position.setdefault(label_map[h][w],[]).append(
                                        label_map[pixel_neighbours[1]][pixel_neighbours[0]])

        # get all value in dictionary is small lists
        # take first list and compare with lists from after positon second
        # if list after position second and first list have same element --> + two list and remove element duplicate
        list_intersection = []
        for key,value in value_of_position.items():
            list_intersection.append((set(value)))

        label_reduce = []
        while len(list_intersection)>0:
            first, *rest = list_intersection
            first = set(first)

            lf = -1
            while len(first)>lf:
                lf = len(first)

                rest2 = []
                for r in rest:
                    if len(first.intersection(set(r)))>0:
                        first |= set(r)
                    else:
                        rest2.append(r)     
                rest = rest2


            label_reduce.append(first)
            list_intersection = rest


        # if position of label =! 0 --> reduce it = min(list label)
        sprites_temporary = {}
        for h in range(image.height):
            for w in range(image.width):
                for i in label_reduce:

                    if label_map[h][w] in i:
                        label_map[h][w] = min(i)

                        if min(i) not in sprites_temporary.keys():
                            sprites_temporary[min(i)] = [[w, h], [w, h]]

                        else:
                            if label_map[h][w] == min(i) and w < sprites_temporary.get(min(i))[0][0]:
                                sprites_temporary.get(min(i))[0][0] = w

                            if label_map[h][w] == min(i) and h < sprites_temporary.get(min(i))[0][1]:
                                sprites_temporary.get(min(i))[0][1] = h

                            if label_map[h][w] == min(i) and w > sprites_temporary.get(min(i))[1][0]:
                                sprites_temporary.get(min(i))[1][0] = w

                            if label_map[h][w] == min(i) and h > sprites_temporary.get(min(i))[1][1]:
                                sprites_temporary.get(min(i))[1][1] = h

        # return each sprite into Sprite object
        sprites = {}
        for sprite in sprites_temporary:
            sprites[sprite] = Sprite(sprite, sprites_temporary[sprite][0][0], sprites_temporary[sprite][0][1], sprites_temporary[sprite][1][0], sprites_temporary[sprite][1][1])

        return sprites, label_map



    def create_sprite_labels_image(self, background_color = (255, 255, 255)):
        
        image = self.image_object
        sprites = SpriteSheet(image).find_sprites()[0]
        label_map = SpriteSheet(image).find_sprites()[1]

        if len(background_color) < 3 or len(background_color) > 4:
                raise ValueError("background_color must be (R, G, B) or (R, G, B, A)")
        
        # len background_color = 3 --> create image with mode RGB
        if len(background_color) == 3:
            img = Image.new('RGB', (image.width, image.height), color=background_color)

        # len background_color = 4 --> create image with mode RGBA
        if len(background_color) == 4:
            img = Image.new('RGBA', (image.width, image.height), color=background_color)

        for label in sprites:
            if len(background_color) == 4:
                color = (randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255))

            if len(background_color) == 3:
                color = (randint(0, 255), randint(0, 255), randint(0, 255))
            
        # create each tuple = (x1, y1, x2, y2)
        # use draw.rectangle to draw rectangle with position x1, y1, x2, y2
            sprite = (sprites.get(label).x1, sprites.get(label).y1, sprites.get(label).x2, sprites.get(label).y2)   
            draw = ImageDraw.Draw(img)
            draw.rectangle((sprite[0], sprite[1], sprite[2], sprite[3]), outline = color)
            
            # in rectangle which drawed, if pixel == label --> draw pixel
            for h in range(sprite[1], sprite[3]):
                for w in range(sprite[0], sprite[2]):
                    if label_map[h][w] == label:
                        draw.point([(w, h)], fill= color)
        return img