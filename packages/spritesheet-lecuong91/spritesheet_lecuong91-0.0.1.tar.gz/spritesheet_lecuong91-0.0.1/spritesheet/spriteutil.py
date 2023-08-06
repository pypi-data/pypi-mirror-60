from PIL import Image, ImageDraw
import numpy as np
import timeit
import io

RGB = 'RGB'
RGBA = 'RGBA'
L = 'L'

class Sprite():
    """ Class Sprite """

    def __init__(self, label, x1, y1, x2, y2):
        for arg in [label, x1, y1, x2, y2]:
            if not isinstance(arg, int) or arg < 0:
                raise ValueError('Invalid coordinates')

        if x2 < x1 or y2 < y1:
            raise ValueError('Invalid coordinates')

        self.__label = label
        self.__top_left = (x1, y1)
        self.__bottom_right = (x2, y2)
        self.__width = x2 - x1 + 1
        self.__height = y2 - y1 + 1
    
    @property
    def label(self):
        return self.__label
        
    @property
    def top_left(self):
        return self.__top_left
        
    @property
    def bottom_right(self):
        return self.__bottom_right

    @property
    def width(self):
        return self.__width
    
    @property
    def height(self):
        return self.__height

class SpriteSheet():
    """ Class SpriteSheet """

    def __init__(self, fd, background_color=None):
        if isinstance(fd, Image.Image):
            self.image = fd
        else:
            self.image = Image.open(fd, 'r')

        if background_color == None:
            self.__background_color = self.find_most_common_color(self.image)

            if self.image.mode == RGBA and len(self.__background_color) == 3:
                self.__background_color =tuple(list(self.__background_color).append(255))
        
        elif ((self.image.mode == RGB and 
                not isinstance(background_color, tuple))
            or (self.image.mode == RGBA and 
                not isinstance(background_color, tuple))
            or (self.image.mode == L and 
                not isinstance(background_color, int)) ):
            raise TypeError('Wrong type background color')
        else:
            self.__background_color = background_color

        self.__sprites, self.__label_map = self.find_sprites()
    
    @property
    def background_color(self):
        return self.__background_color

    @property
    def sprites(self):
        return self.__sprites
    
    @property
    def label_map(self):
        return self.__label_map

    @staticmethod
    def find_most_common_color(image):
        """Returns the pixel color that is the most used in this image.
        
        Arguments:
            image {Object} -- A image.
        """

        return max(image.getcolors(maxcolors=image.height*image.width))[1]

    def find_sprites(self):
        """Returns a tuple (sprites, label_map) where:

        sprites: A collection of key-value pairs (a dictionary) 
        where each key-value pair maps the key (the label of a sprite) 
        to its associated value (a Sprite object);

        label_map: A 2D array of integers of equal dimension (width and height) 
        as the original image where the sprites are packed in. 
        The label_map array maps each pixel of the image passed to the function 
        to the label of the sprite this pixel corresponds to, or 0 if 
        this pixel doesn't belong to a sprite (e.g., background color).
        
        Arguments:
            image {Object} -- An image object.
        
        Keyword Arguments:
            background_color {Integer or Tuple, optional} -- An integer 
            if the image format is grayscale, or a tuple (red, green, blue) 
            if the image format is RGB. (default: {None})
        """

        background_color = list(self.__background_color)
        neighbors = {} #Pixels neighborhood
        label = 0 #Label increase
        sprites = {}
        np_image = np.array(self.image).tolist()
        np_sprites = np.zeros(self.image.size[::-1],dtype=np.int).tolist()

        #Labeling
        for row in range(self.image.height):
            for col in range(self.image.width):
                if np_image[row][col] != background_color:
                    temp = [] #List pixels neighbor
                    prev_row = row - 1
                    prev_col = col - 1
                    next_col = col + 1

                    try: #Zero is background
                        if np_sprites[prev_row][prev_col] != 0:
                            temp.append(np_sprites[prev_row][prev_col])

                        if np_sprites[prev_row][col] != 0:
                            temp.append(np_sprites[prev_row][col])

                        if np_sprites[prev_row][next_col] != 0:
                            temp.append(np_sprites[prev_row][next_col])
                            
                        if np_sprites[row][prev_col] != 0:
                                temp.append(np_sprites[row][prev_col])
                    except:
                        pass

                    if len(temp) > 0: #Have neighbor
                        try:
                            neighbors[min(temp)].extend(temp)
                        except:
                            neighbors[min(temp)] = temp

                        np_sprites[row][col] = min(temp)

                    else:
                        label += 1
                        np_sprites[row][col] = label

                        if label not in neighbors:
                            neighbors[label] = [label]

        #Connect related labels 
        checked = [] #Key checked
        _neighbors = neighbors.copy()
        for key in neighbors:
            if key in checked:
                continue

            neighbors[key] = list(set(neighbors[key]))
            _neighbors.pop(key)

            for _key in _neighbors:
                if _key in neighbors[key]:
                    neighbors[_key].extend(neighbors[key])
                    checked.append(neighbors[key])

        #Reduce labels
        for key in neighbors:
            neighbors[key] = min(neighbors[key])

        #Relabel
        for row in range(self.image.height):
            for col in range(self.image.width):
                if np_image[row][col] != background_color:
                    np_sprites[row][col] = neighbors[np_sprites[row][col]]
                    
                    try:
                        if col < sprites[np_sprites[row][col]][1]:
                            sprites[np_sprites[row][col]][1] = col
                        if row > sprites[np_sprites[row][col]][2]:
                            sprites[np_sprites[row][col]][2] = row
                        if col > sprites[np_sprites[row][col]][3]:
                            sprites[np_sprites[row][col]][3] = col
                    except:
                        sprites[np_sprites[row][col]] = [row, col, row, col]

        #Create label-Sprite pairs
        for sprite in sprites:
            y1, x1, y2, x2 = sprites[sprite]
            sprites[sprite] = Sprite(sprite, x1, y1, x2, y2)

        return (sprites, np.array(np_sprites))

    def create_sprite_labels_image(self):
        """Returns an image of equal dimension (width and height) as the 
            original image that was passed to the function find_sprites.
        
        Arguments:
            sprites {Dictionary} -- A dictionary where each key-value 
                pair maps the key (the label of a sprite) to its 
                associated value (a Sprite object).
            label_map {Array} -- A 2D array of the original image where 
                the sprites are packed in.
        
        Keyword Arguments:
            background_color {Tuple} -- The color to use as the background
                of the image to create. (default: {(255, 255, 255)})
        """

        if len(self.__background_color) == 3: #Check mode of image to create
            new_image = Image.new(
                RGB, self.__label_map.shape[::-1], self.__background_color)
        else:
            new_image = Image.new(
                RGBA, self.__label_map.shape[::-1], self.__background_color)
        
        im_height, im_width = self.__label_map.shape
        im_draw = ImageDraw.Draw(new_image)
        im_px = new_image.load()
        sprites_color = {} #Sprites's color

        #Draw bounded
        for sprite in self.__sprites:
            #Get random color
            color = tuple(np.random.choice(range(256), size=3))
            sprites_color[sprite] = color
            im_draw.rectangle(
                            self.__sprites[sprite].top_left +
                            self.__sprites[sprite].bottom_right, 
                            outline=color)

        #Draw sprites
        for row in range(im_height):
            for col in range(im_width):
                if self.__label_map[row][col] != 0:
                    im_px[col, row] = sprites_color[self.__label_map[row][col]]

        return new_image

def main():

    image = SpriteSheet('optimized_sprite_sheet.png')
    # sprites, label = image.find_sprites()
    sprite_label_image = image.create_sprite_labels_image()
    sprite_label_image.save('test.png')

if __name__ == "__main__":
    main()