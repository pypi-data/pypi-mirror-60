from PIL import Image
from PIL import ImageDraw
import pprint
import random


INDEX_8_NEIGHBOR_PIXELS = [
    (-1, -1), # Top_left
    (-1, 0), # Top
    (-1, 1), # Top-right
    (0, 1), # Right
    (1, 1), # Bottom-right
    (1, 0), # Bottom
    (1, -1), # Bottom-left
    (0, -1), # Left
]

# Waypoint 1: Find the Most Common Color in an Image.
def find_most_common_color(image):
    """
    This function takes an argument image (a Image object) and that returns the pixel color that is the most used in this image.
    
    @param image: a Image object.

    @return the pixel color that is the most used in this image.
    """
    if not isinstance(image, Image.Image):
        raise TypeError("Argument image must be Image object.")

    # Get width and height of image.
    width, height = image.size

    # Use getcolors() to get all colors in image and the number of their occurrences
    all_color = image.getcolors(width*height)

    # Sort up ascending.
    sort_color = sorted(all_color)

    return sort_color[-1][1]



# Waypoint 2: Write a Class Sprite
class Sprite:
    """
    This class represents smaller images called sprites.
    For each different sprite there will be a different label
    and there will be a different coordinates.
    """
    # The constructor of the class Sprite.
    def __init__(self, label, x1, y1, x2, y2):
        
        # All argument must be an integer(whole numbers).
        for arg in [label, x1, y1, x2, y2]:
            if not isinstance(arg, int):
                raise TypeError(f'Argument {arg} must be an integer.')

        # To create a quadrilateral, x2 must > x1, y2 must > y1.
        if x2 < x1 or y2 < y1 or label < 0 or x1 < 0 or x2 < 0 or y1 < 0 or y2 < 0:
            raise ValueError("Invalid coordinates")
        
        # These arguments are used to initialize PRIVATE ATTRIBUTES.
        self.__label = label
        self.__x1 = x1
        self.__y1 = y1
        self.__x2 = x2
        self.__y2 = y2

    @property
    def label(self):
        return self.__label

    @property
    def x1(self):
        return self.__x1

    @property
    def x2(self):
        return self.__x2

    @property
    def y1(self):
        return self.__y1

    @property
    def y2(self):
        return self.__y2

    @property
    def top_left(self):
        return (self.__x1, self.__y1)
    
    @property
    def bottom_right(self):
        return (self.__x2, self.__y2)

    @property
    def width(self):
        width = self.__x2 - self.__x1 + 1
        return width
    
    @property
    def height(self):
        height = self.__y2 - self.__y1 + 1
        return height





# Waypoint 3: Find Sprites in an Image
def find_sprites(image, background_color=None):
    """
    This function find all sprites in an object Image.
    Pixels that are not part of sprite will be labeled 0.
    Each sprite will be labeled differently, the pixels in each sprite will have the same label.

    @param image: an object image.
    @background_color: a tuple or an integer represents a certain color.

    @return: 
        sprites: a dictionary with key is label of sprite, value is an object Sprite.
        label_map: A 2D array of integers of equal dimension (width and height) as the original image where the sprites are packed in.
    """
    if not isinstance(image, Image.Image):
        raise TypeError("Argument image must be Image object")

    if background_color == None:
        background_color = find_most_common_color(image)

    if image.mode == 'RGB':
        if not isinstance(background_color, tuple):
            raise TypeError("Background_color must be a tuple.")

        if len(background_color) != 3:
            raise ValueError("Background_color of RGB must be a tuple leght 3.")
        
        if type(background_color[0]) != int or type(background_color[1]) != int or type(background_color[2]) != int:
            raise TypeError("(Red, Green, Blue) must be an integer >=0 and <= 255.")
        
        if not 0 <= background_color[0] <= 255 or not 0 <= background_color[1] <= 255 or not 0 <= background_color[2] <= 255:
            raise ValueError("(Red, Green, Blue) must be an integer >=0 and <= 255.")
    
    if image.mode == 'RGBA':
        if not isinstance(background_color, tuple):
            raise TypeError("Background_color must be a tuple.")

        if len(background_color) != 4:
            raise ValueError("Background_color of RGB must be a tuple leght 3.")

        if type(background_color[0]) != int or type(background_color[1]) != int or type(background_color[2]) != int or type(background_color[3]) != int:
            raise TypeError("(Red, Green, Blue, Alpha) must be an integer >=0 and <= 255.")

        if not 0 <= background_color[0] <= 255 or not 0 <= background_color[1] <= 255 or not 0 <= background_color[2] <= 255 or not 0 <= background_color[3] <= 2550:
            raise ValueError("(Red, Green, Blue, Alpha) must be an integer >=0 and <= 255.")

    if image.mode == 'L':
        if not isinstance(background_color, int):
            raise TypeError("Background_color of grayscale image must be an integer.")

        if not 0 <= background_color <= 255:
            raise ValueError("Background_color of grayscale image must be an integer >=0 and <= 255.")

    # Get width and height of image.
    width, height = image.size

    # Creat the empty label map.
    # label_map is a 2-dimensional array.
    # label_map has number of elements same as pixel of image. 
    label_map = [[0 for x in range(width)] for y in range(height)]

    # Use for loop, use getpixel() to check color of each pixel.
    # From left to right, from top to bottom.
    label = 0
    for h in range(height):
        for w in range(width):
            # List 4 surrounding labels of the pixel being checked.
            temp_list_label_neighborhood = []
            # If the pixel color is different from the background color, label it.
            if image.getpixel((w, h)) != background_color:
                # Check for 4 pixels, 3 on top, 1 right ahead.
                # The index of these 4 pixels must not be negative because if negative it will be rotated.
                # And no bigger than width, height because there will be an error out of range.
                try: # 1. Pixel Top-left
                    if label_map[h-1][w-1] != 0 and (h-1) >= 0 and (w-1) >= 0:
                        temp_list_label_neighborhood.append(label_map[h-1][w-1])
                except:
                    pass

                try: # 2. Pixel Top
                    if label_map[h-1][w] != 0 and (h-1) >= 0:
                        temp_list_label_neighborhood.append(label_map[h-1][w])
                except:
                    pass

                try: # 3. Pixel Top-right
                    if label_map[h-1][w+1] != 0 and (h-1) >= 0 and (w+1) < (width-1):
                        temp_list_label_neighborhood.append(label_map[h-1][w+1])
                except:
                    pass

                try: # 4. Pixel Left
                    if label_map[h][w-1] != 0 and (w-1) >= 0:
                        temp_list_label_neighborhood.append(label_map[h][w-1])
                except:
                    pass
            
                # When len of this list = 0, that is labels around all 0, must create new labels.
                if len(temp_list_label_neighborhood) == 0:
                    label += 1
                    label_map[h][w] = label
                else:
                    label_map[h][w] = min(temp_list_label_neighborhood)
    
    # Continue to loop through the pixels, check the label around 8 points.
    reduce_dict ={}
    for h in range(height):
        for w in range(width):
            # Chỉ xét các label khác 0.
            if label_map[h][w] != 0:
                reduce_dict.setdefault(label_map[h][w], []).extend(all_8_labels_around(label_map, h, w, height, width))

    # Remove duplicate labels.
    for key in reduce_dict:
        reduce_dict[key] = list(set(reduce_dict[key]))
        reduce_dict[key].sort()
    
    # Count the number of sprites in the image.
    # Can be considered as the official label.
    sprites_count = []
    for key in reduce_dict:
        if key == min(reduce_dict[key]):
            sprites_count.append(key)
    
    # Based on the label that traced back to find the labels were interlinked.
    # Only when the smallest label belongs to the official label in sprites_count, we will take it.
    for key in reduce_dict:
        if key not in sprites_count:
            while True:
                temp = []
                for i in reduce_dict[key]:
                    temp.extend(reduce_dict[i])

                temp = list(set(temp))
                temp.sort()
                reduce_dict[key] = temp

                if min(reduce_dict[key]) in sprites_count:
                    break
    
    # Last iteration of label_map to return reduced sprite.
    for h in range(height):
        for w in range(width):
            if label_map[h][w] != 0:
                label_map[h][w] = min(reduce_dict[label_map[h][w]])

    # Create a dict containing sprite name as key, value as [x1, y1, x2, y2], default [width, height, 0, 0]
    sprites_index = {}
    for i in sprites_count:
        sprites_index.setdefault(i, [width, height, 0, 0])

    # Label_map loop through again to get all the coordinates of each sprite.
    for h in range(height):
        for w in range(width):
            if label_map[h][w] in sprites_count:
                if w < sprites_index[label_map[h][w]][0]:
                    sprites_index[label_map[h][w]][0] = w
                
                if h < sprites_index[label_map[h][w]][1]:
                    sprites_index[label_map[h][w]][1] = h
                
                if w > sprites_index[label_map[h][w]][2]:
                    sprites_index[label_map[h][w]][2] = w

                if h > sprites_index[label_map[h][w]][3]:
                    sprites_index[label_map[h][w]][3] = h

    # Create dictionary sprites, key is name sprite, value is object of sprite itself.
    sprites = {}
    for key in sprites_index:
        sprites.setdefault(key, Sprite(key, sprites_index[key][0], sprites_index[key][1], sprites_index[key][2], sprites_index[key][3]))

    return (sprites, label_map)


# This function take all non-zero labels around the checked label.
def all_8_labels_around(label_map, h, w, height, width):
    """
    This function support for Waypoint 3.
    This function take all non-zero labels around the checked label.

    @param label_map: A 2D array of integers of equal dimension (width and height) as the original image where the sprites are packed in.
        The label_map array maps each pixel of the image passed to the function to the label of the sprite this pixel corresponds to, or 0 if this pixel doesn't belong to a sprite (e.g., background color).
        When we run this function, label_map not really complete.

    @param h, w: an integer, Used to determine location of checked label.

    @param height, width: an integer, size of label_map.

    @return: a list, contains all non-duplicate labels around the checked label.
    """
    # Create an empty list.
    # It will contain all the different labels around the checked label.
    all_labels_around = []

    # Has created a contain variable name INDEX_8_NEIGHBOR_PIXELS
    # It contains the deviation of the address of 8 points around, compared to the origin (the checked label).
    for i in INDEX_8_NEIGHBOR_PIXELS:
        try:
            if label_map[h+i[0]][w+i[1]] !=0 and 0 <= (h+i[0]) <= (height-1) and 0 <= (w+i[1]) <= (width-1):
                all_labels_around.append(label_map[h+i[0]][w+i[1]])
        except:
            continue
    
    # Finally, we must append the label itself, to avoid the case all around label is 0, and the returned list is empty.
    all_labels_around.append(label_map[h][w])
    
    # Remove duplicate labels.
    all_labels_around = list(set(all_labels_around))
    
    return all_labels_around



# Waypoint 4: Draw Sprite Label Bounding Boxes
def create_sprite_labels_image(sprites, label_map, background_color=(255, 255, 255)):
    """
    The function create_sprite_labels_image draws the masks of the sprites at the exact same position that the sprites were in the original image. 
        The function draws each sprite mask with a random uniform color (one color per sprite mask). 
            The function also draws a rectangle (bounding box) around each sprite mask, of the same color used for drawing the sprite mask.

    @param sprites: A collection of key-value pairs (a dictionary) where each key-value pair maps the key (the label of a sprite) 
        to its associated value (a Sprite object);

    @param label_map: A 2D array of integers of equal dimension (width and height) as the original image where the sprites are packed in. 
        The label_map array maps each pixel of the image passed to the function to the label of the sprite this pixel corresponds to, 
            or 0 if this pixel doesn't belong to a sprite (e.g., background color).

    @param background_color: a tuple, either a tuple (R, G, B) or a tuple (R, G, B, A) that identifies the color to use as the background of the image to create. 
        If this argument is not passed to the function, the default value is (255, 255, 255)

    @return: returns an image of equal dimension (width and height) as the original image that was passed to the function find_sprites.
    """
    # Argument sprites must be a dictionary.
    if not isinstance(sprites, dict):
        raise TypeError("Argument sprites must be a dictionary.")

    # Argument background_color must be a tuple.
    if not isinstance(background_color, tuple):
        raise TypeError("Argument background_color must be a tuple.")
    else:
        if len(background_color) < 3 or len(background_color) > 4:
            raise ValueError("Argument background_color must be (R, G, B) or (R, G, B, A)")
    
    # Base on label_map to find width and height
    width = len(label_map[0])
    height = len(label_map)

    # Creat a new Image object and random color for each sprite.
    if len(background_color) == 3:
        img = Image.new(mode='RGB', size=(width, height), color=background_color)
        sprites_color = {}
        for key in sprites:
            sprites_color.setdefault(key, (random.randint(0,255), random.randint(0,255), random.randint(0,255)))
        
    if len(background_color) == 4:
        img = Image.new(mode='RGBA', size=(width, height), color=background_color)
        sprites_color = {}
        for key in sprites:
            sprites_color.setdefault(key, (random.randint(0,255), random.randint(0,255), random.randint(0,255), 255))

    # Based on label_map use Draw.point to draw the sprite on the img object.
    for h in range(height):
        for w in range(width):
            if label_map[h][w] in sprites.keys():
                draw_point = ImageDraw.Draw(img)
                draw_point.point((w, h), fill=sprites_color[label_map[h][w]])

    # Draw rectangle for each sprite
    # Use dict sprites, loop to take x1,y1,x2,y7
    # Use dict sprites_color to take color of each sprite.
    for key in sprites:
        draw_rectangle = ImageDraw.Draw(img)
        draw_rectangle.rectangle([sprites[key].x1, sprites[key].y1, sprites[key].x2, sprites[key].y2], outline=sprites_color[key])

    return img



# Waypoint 5: Write a Class SpriteSheet
class SpriteSheet:
    """
    This class represents all smaller images called sprites in an object image.
    For each different sprite there will be a different label
    and there will be a different coordinates.
    """
    # The constructor of the class Sprite.
    def __init__(self, fd, background_color=None):
        if isinstance(fd, Image.Image):
            self.__image = fd
        else:
            try: 
                self.__image = Image.open(fd, mode='r')
            except:
                raise TypeError("fd must be the name and path (a string) or a pathlib.Path object or a file object")
        self.__background_color = background_color
        self.__sprites = None
        self.__label_map = None

    # Integrate the function find_most_common_color as a static method of the class SpriteSheet.
    @staticmethod
    def find_most_common_color(image):
        """
        This function takes an argument image (a Image object) and that returns the pixel color that is the most used in this image.
    
        @param image: a Image object.

        @return the pixel color that is the most used in this image.
        """
        if not isinstance(image, Image.Image):
            raise TypeError("Argument image must be Image object.")

        # Get width and height of image.
        width, height = image.size

        # Use getcolors() to get all colors in image and the number of their occurrences
        all_color = image.getcolors(width*height)

        # Sort up ascending.
        sort_color = sorted(all_color)

        return sort_color[-1][1]

    @property
    def background_color(self):
        if self.__background_color == None:
            self.__background_color = SpriteSheet.find_most_common_color(self.__image)

        return self.__background_color

    # Instance method
    def find_sprites(self):
        """
        This function find all sprites in an object Image.
        Pixels that are not part of sprite will be labeled 0.
        Each sprite will be labeled differently, the pixels in each sprite will have the same label.

        @param image: an object image.
        @background_color: a tuple or an integer represents a certain color.

        @return: 
            sprites: a dictionary with key is label of sprite, value is an object Sprite.
            label_map: A 2D array of integers of equal dimension (width and height) as the original image where the sprites are packed in.
        """
        if not isinstance(self.__image, Image.Image):
            raise TypeError("Argument image must be Image object.")

        if self.__background_color == None:
            background_color = SpriteSheet.find_most_common_color(self.__image)
        else:
            background_color = self.__background_color

        # Get width and height of image.
        width, height = self.__image.size

        # Creat the empty label map.
        # label_map is a 2-dimensional array.
        # label_map has number of elements same as pixel of image. 
        label_map = [[0 for x in range(width)] for y in range(height)]

        # Use for loop, use getpixel() to check color of each pixel.
        # From left to right, from top to bottom.
        label = 0
        for h in range(height):
            for w in range(width):
                # List 4 surrounding labels of the pixel being checked.
                temp_list_label_neighborhood = []
                # If the pixel color is different from the background color, label it.
                if self.__image.getpixel((w, h)) != background_color:
                    # Check for 4 pixels, 3 on top, 1 right ahead.
                    # The index of these 4 pixels must not be negative because if negative it will be rotated.
                    # And no bigger than width, height because there will be an error out of range.
                    try: # 1. Pixel Top-left
                        if label_map[h-1][w-1] != 0 and (h-1) >= 0 and (w-1) >= 0:
                            temp_list_label_neighborhood.append(label_map[h-1][w-1])
                    except:
                        pass

                    try: # 2. Pixel Top
                        if label_map[h-1][w] != 0 and (h-1) >= 0:
                            temp_list_label_neighborhood.append(label_map[h-1][w])
                    except:
                        pass

                    try: # 3. Pixel Top-right
                        if label_map[h-1][w+1] != 0 and (h-1) >= 0 and (w+1) < (width-1):
                            temp_list_label_neighborhood.append(label_map[h-1][w+1])
                    except:
                        pass

                    try: # 4. Pixel Left
                        if label_map[h][w-1] != 0 and (w-1) >= 0:
                            temp_list_label_neighborhood.append(label_map[h][w-1])
                    except:
                        pass

                    # When len of this list = 0, that is labels around all 0, must create new labels.
                    if len(temp_list_label_neighborhood) == 0:
                        label += 1
                        label_map[h][w] = label
                    else:
                        label_map[h][w] = min(temp_list_label_neighborhood)

        # Continue to loop through the pixels, check the label around 8 points.    
        reduce_dict ={}
        for h in range(height):
            for w in range(width):
                # Chỉ xét các label khác 0.
                if label_map[h][w] != 0:
                    reduce_dict.setdefault(label_map[h][w], []).extend(self.__all_8_labels_around(label_map, h, w, height, width))

        # Remove duplicate labels.
        for key in reduce_dict:
            reduce_dict[key] = list(set(reduce_dict[key]))
            reduce_dict[key].sort()

        # Count the number of sprites in the image.
        # Can be considered as the official label.
        sprites_count = []
        for key in reduce_dict:
            if key == min(reduce_dict[key]):
                sprites_count.append(key)

        # Based on the label that traced back to find the labels were interlinked.
        # Only when the smallest label belongs to the official label in sprites_count, we will take it.
        for key in reduce_dict:
            if key not in sprites_count:
                while True:
                    temp = []
                    for i in reduce_dict[key]:
                        temp.extend(reduce_dict[i])

                    temp = list(set(temp))
                    temp.sort()
                    reduce_dict[key] = temp

                    if min(reduce_dict[key]) in sprites_count:
                        break
    
        # Last iteration of label_map to return reduced sprite.
        for h in range(height):
            for w in range(width):
                if label_map[h][w] != 0:
                    label_map[h][w] = min(reduce_dict[label_map[h][w]])

        # Create a dict containing sprite name as key, value as [x1, y1, x2, y2], default [width, height, 0, 0]
        sprites_index = {}
        for i in sprites_count:
            sprites_index.setdefault(i, [width, height, 0, 0])
        
        # Label_map loop through again to get all the coordinates of each sprite.
        for h in range(height):
            for w in range(width):
                if label_map[h][w] in sprites_count:
                    if w < sprites_index[label_map[h][w]][0]:
                        sprites_index[label_map[h][w]][0] = w

                    if h < sprites_index[label_map[h][w]][1]:
                        sprites_index[label_map[h][w]][1] = h

                    if w > sprites_index[label_map[h][w]][2]:
                        sprites_index[label_map[h][w]][2] = w

                    if h > sprites_index[label_map[h][w]][3]:
                        sprites_index[label_map[h][w]][3] = h

        # Create dictionary sprites, key is name sprite, value is object of sprite itself.
        sprites = {}
        for key in sprites_index:
            sprites.setdefault(key, Sprite(key, sprites_index[key][0], sprites_index[key][1], sprites_index[key][2], sprites_index[key][3]))

        self.__sprites = sprites
        self.__label_map = label_map
        return (sprites, label_map)


    # Private methods
    def __all_8_labels_around(self, label_map, h, w, height, width):
        """
        This function support for Waypoint 3.
        This function take all non-zero labels around the checked label.

        @param label_map: A 2D array of integers of equal dimension (width and height) as the original image where the sprites are packed in.
            The label_map array maps each pixel of the image passed to the function to the label of the sprite this pixel corresponds to, 
                or 0 if this pixel doesn't belong to a sprite (e.g., background color).
            When we run this function, label_map not really complete.

        @param h, w: an integer, Used to determine location of checked label.

        @param height, width: an integer, size of label_map.

        @return: a list, contains all non-duplicate labels around the checked label.
        """
        # Create an empty list.
        # It will contain all the different labels around the checked label.
        all_labels_around = []

        # Has created a contain variable name INDEX_8_NEIGHBOR_PIXELS
        # It contains the deviation of the address of 8 points around, compared to the origin (the checked label).
        for i in INDEX_8_NEIGHBOR_PIXELS:
            try:
                if label_map[h+i[0]][w+i[1]] !=0 and 0 <= (h+i[0]) <= (height-1) and 0 <= (w+i[1]) <= (width-1):
                    all_labels_around.append(label_map[h+i[0]][w+i[1]])
            except:
                continue

        # Finally, we must append the label itself, to avoid the case all around label is 0, and the returned list is empty.
        all_labels_around.append(label_map[h][w])

        # Remove duplicate labels.
        all_labels_around = list(set(all_labels_around))

        return all_labels_around

    # Instance method
    def create_sprite_labels_image(self, background_color=(255, 255, 255)):
        """
        The function create_sprite_labels_image draws the masks of the sprites at the exact same position that the sprites were in the original image. 
            The function draws each sprite mask with a random uniform color (one color per sprite mask). 
                The function also draws a rectangle (bounding box) around each sprite mask, of the same color used for drawing the sprite mask.
        Function find_sprites 

        @param sprites: A collection of key-value pairs (a dictionary) where each key-value pair maps the key (the label of a sprite) 
            to its associated value (a Sprite object);

        @param label_map: A 2D array of integers of equal dimension (width and height) as the original image where the sprites are packed in. 
            The label_map array maps each pixel of the image passed to the function to the label of the sprite this pixel corresponds to, 
                or 0 if this pixel doesn't belong to a sprite (e.g., background color).

        @param background_color: a tuple, either a tuple (R, G, B) or a tuple (R, G, B, A) that identifies the color to use as the background of the image to create. 
            If this argument is not passed to the function, the default value is (255, 255, 255)

        @return: returns an image of equal dimension (width and height) as the original image that was passed to the function find_sprites.
        """
        # We must have sprites and label_map before we run create_sprite_labels_image.
        if self.__sprites is None or self.__label_map is None:
            sprites, label_map = self.find_sprites()

        sprites, label_map = self.__sprites, self.__label_map

        # Base on label_map to find width and height
        width = len(label_map[0])
        height = len(label_map)

        # Creat a new Image object and random color for each sprite.
        if len(background_color) == 3:
            img = Image.new(mode='RGB', size=(width, height), color=background_color)
            sprites_color = {}
            for key in sprites:
                sprites_color.setdefault(key, (random.randint(0,255), random.randint(0,255), random.randint(0,255)))

        if len(background_color) == 4:
            img = Image.new(mode='RGBA', size=(width, height), color=background_color)
            sprites_color = {}
            for key in sprites:
                sprites_color.setdefault(key, (random.randint(0,255), random.randint(0,255), random.randint(0,255), 255))

        # Based on label_map use Draw.point to draw the sprite on the img object.
        for h in range(height):
            for w in range(width):
                if label_map[h][w] in sprites.keys():
                    draw_point = ImageDraw.Draw(img)
                    draw_point.point((w, h), fill=sprites_color[label_map[h][w]])

        # Draw rectangle for each sprite
        # Use dict sprites, loop to take x1,y1,x2,y7
        # Use dict sprites_color to take color of each sprite.
        for key in sprites:
            draw_rectangle = ImageDraw.Draw(img)
            draw_rectangle.rectangle([sprites[key].x1, sprites[key].y1, sprites[key].x2, sprites[key].y2], outline=sprites_color[key])

        return img




def main():
    # image = Image.open('/home/hkquan/Downloads/metal_slug_sprite_standing_stance.png')
    # print(image.mode)
    # color = find_most_common_color(image)
    # print(color)
    # image = image.convert('L')
    # print(image.mode)
    # color = find_most_common_color(image)
    # print(color)


    # sprite = Sprite(1, 12, 23, 145, 208)
    # print(sprite.label)
    # print(sprite.top_left)
    # print(sprite.bottom_right)
    # sprite = Sprite(1, -1, 0, 0, 0)
    # sprite = Sprite(1, 12, 23, 145, 208)
    # print(sprite.width)
    # print(sprite.height)
    
    # image = Image.open('/home/hkquan/Downloads/metal_slug_single_sprite.png')
    # print(image.mode)
    # sprites, label_map = find_sprites(image)
    # print(len(sprites))
    # for label, sprite in sprites.items():
    #     print(f"Sprite ({label}): [{sprite.top_left}, {sprite.bottom_right}] {sprite.width}x{sprite.height}")
    # pprint.pprint(label_map, width=120)

    # image = Image.open('/home/hkquan/Downloads/optimized_sprite_sheet.png')
    # sprites, label_map = find_sprites(image)
    # print(len(sprites))
    # for label, sprite in sprites.items():
    #     print(f"Sprite ({label}): [{sprite.top_left}, {sprite.bottom_right}] {sprite.width}x{sprite.height}")

    # image = Image.open('/home/hkquan/Downloads/optimized_sprite_sheet.png')
    # sprites, label_map = find_sprites(image)
    # sprites_color = create_sprite_labels_image(sprites, label_map)
    # sprites_color.show()
    
    # img = SpriteSheet("/home/hkquan/Downloads/optimized_sprite_sheet.png")
    # print(img.background_color)
    # sprites, label_map = img.find_sprites()
    # new_img = img.create_sprite_labels_image()
    # new_img.show()

    pass

if __name__ == "__main__":
    main()


