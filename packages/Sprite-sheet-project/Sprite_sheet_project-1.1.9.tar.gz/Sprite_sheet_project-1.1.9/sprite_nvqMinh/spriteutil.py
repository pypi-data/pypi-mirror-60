import time
import math
import numpy as np
from PIL import Image
from pprint import pprint
from PIL import Image, ImageDraw
# WP1
IMAGE_RGBA = "RGBA"
IMAGE_RGB = "RGB"
DICT_COLOR = {"#4b8bbe":(75, 139, 190),"#ffd43b":(255, 212, 59),
"#812878": (129, 40, 120),"#e4682a":(228, 104, 42),"#8ed5fa":(142, 213, 250),
"#b52e31":(181, 46, 49),"#e09b00": (224, 155, 0),"#1d3a45":(29, 58, 69)}
COLOR = np.array(["#4b8bbe","#ffd43b","#812878","#e4682a","#8ed5fa","#b52e31","#e09b00","#1d3a45"])

def find_most_common_color(image):
    """The function find_most_common_color that takes an argument image 
    (a Image object) and that returns the pixel color that is the most used in this image.
    
    Arguments:
        image {obj} -- an obj image
    
    Raises:
        ValueError: if not img object
    
    Returns:
        
        .an integer if the mode is grayscale;
        .a tuple (red, green, blue) of integers (0 to 255) if the mode is RGB;
        .a tuple (red, green, blue, alpha) of integers (0 to 255) if the mode is RGBA.

    """

    try:
        if image.mode == IMAGE_RGBA or image.mode == IMAGE_RGB:
            image = max(image.getcolors(image.size[0] * image.size[1]))
            return (image[1])
    except:
        raise ValueError("Argument should be a image obj")
    return 0


#WP2
class Sprite:
    def __init__(self, label, x1, y1, x2, y2):

        for argument in (label, x1, y1, x2, y2):
            if not isinstance(argument, int) or argument < 0:
                raise ValueError('Invalid coordinates')

            if x2 < x1 or y2 < y1:
                raise ValueError('Invalid coordinates')


        self.__label = label
        self.__x1 = x1
        self.__y1 = y1
        self.__x2 = x2
        self.__y2 = y2

    @property
    def label(self):
        return self.__label

    @property
    def bottom_right(self):
        return (self.__x2, self.__y2)

    @property
    def top_left(self):
        return (self.__x1, self.__y1)

    @property
    def width(self):
        return ((self.__x2 - self.__x1) + 1)

    @property
    def height(self):
        return ((self.__y2 - self.__y1) + 1)


#WP3
def find_sprites(image, background_color=None):
    """ The function find_sprites that takes an argument image (an Image object).
    
    Arguments:
        image {img obj} -- an image object
    
    Keyword Arguments:
        background_color {tuple} -- The tuple of color (default: {None})
    
    Raises:
        TypeError: if image is not an image object
    
    Returns:
        l,sprites -- a tuple of sprites and label map
    """

    if not isinstance(image, Image.Image):
        raise TypeError('Not an image obj')

    common_color = find_most_common_color(image)

    #if background_color == None:


    label_map = []
    #get width ,high of image
    w, h = image.size
    data = image.load()
    # print(data)
    #Create a table with w and h of image
    Matrix =  [[0 for x in range(w)] for y in range(h)]

    #Replace background =0 , color = 1
    for x in range(h):
        for y in range(w):
            color = data[y, x]

            if color != common_color: Matrix[x][y] = 1
            else : Matrix[x][y] = 0

    label_map = count_pixel(Matrix)
    label_map, dict_test = reduce_pixel(label_map)
    l , sprites = calculate_sprites_corrdinate(label_map, dict_test)

    return l,sprites


def count_pixel(label_map):
    """The function take a 2D array of label map and count 
    base on Pixel Connectivity
    
    Arguments:
        label_map {list} -- 2D array
    
    Returns:
        label_map {list} -- 2D array with label count
    """
    #width and height of the photo
    width_label_map = len(label_map[0])
    heigh_label_map = len(label_map)


    label = 0
    #label the pixel
    for row in range(heigh_label_map):
        for column in range(width_label_map):

            try:
                x = label_map[row][column]

                if x > 0:
                        #Check connectivity of 4 point
                    if label_map[row][column - 1] == 0 \
                            and label_map[row - 1][column + 1] == 0 \
                            and label_map[row - 1][column] == 0 \
                            and label_map[row - 1][column - 1] == 0:
                        label = label + 1
                        label_map[row][column] = label

                    else:
                        #Check connectivity of 4 point
                        if label_map[row - 1][column - 1] > 0:
                            label_map[row][column] = label_map[row - 1][column - 1]

                        if label_map[row - 1][column] > 0:
                            label_map[row][column] = label_map[row - 1][column]

                        if label_map[row - 1][column + 1] > 0:
                            label_map[row][column] = label_map[row - 1][column + 1]

                        if label_map[row][column - 1] > 0:
                            label_map[row][column] = label_map[row][column - 1]

            except:
                continue

    return label_map


def reduce_pixel(label_map):
    """The funtion reduce labels base on Equivalent Labels
    
    Arguments:
        label_map {list} -- 2D array
    
    Returns:
        label_map {list} -- 2D array with reduced label
        dict_new {dict} -- dict of sprite 's coordinate 
    """
    width_label_map = len(label_map[0])
    heigh_label_map = len(label_map)

    dict_labelid = {}
    for row in range(heigh_label_map):
        for column in range(width_label_map):

            try:
                x = label_map[row][column]

                if x > 0:
                    #Check connectivity of 4 point
                    if label_map[row - 1][column - 1] > 0:
                        dict_labelid.setdefault(x, []).append(label_map[row - 1][column - 1])

                    if label_map[row - 1][column] > 0:
                        dict_labelid.setdefault(x, []).append(label_map[row - 1][column])

                    if label_map[row - 1][column + 1] > 0:
                        dict_labelid.setdefault(x, []).append(label_map[row - 1][column + 1])

                    if label_map[row][column - 1] > 0:
                        dict_labelid.setdefault(x, []).append(label_map[row][column - 1])

                    if (label_map[row - 1][column - 1] + label_map[row - 1][column] + label_map[row - 1][column + 1] +label_map[row][column - 1]) == 0:
                        dict_labelid.setdefault(label_map[row][column], []).append(label_map[row][column])

            except:
                continue

    common_element_list = [] #joint all sublist have same value
    dict_neighborhood = {} #dicttionary of realated labels in a sprite

    for key, value in dict_labelid.items():
        appendkey = sorted(list(set(value)))
        if key not in appendkey:appendkey.append(key)

        common_element_list.append(list(set(value)))

    list_a = return_common_elemens(common_element_list)


    for data in list_a:
        dict_neighborhood.setdefault(min(data), data)

    #dict of cordinate
    dict_new = {}
    #change value to key,key to value
    for key in dict_neighborhood:
        for value in dict_neighborhood[key]:
            dict_new[value] = key

    #if neighbor have min value, reduce current corrdinate to min value
    for row in range(heigh_label_map):
        for column in range(width_label_map):
            if label_map[row][column] > 0:
                label_map[row][column] = dict_new[label_map[row][column]]
    

    return label_map, dict_new

def return_common_elemens(l):
    """The funtion group all sublist if sublist have same element 
    
    Arguments:
        l {list} -- a list of many sublist
    
    Returns:
        common_list -- a list with all grouped sub list
    """

    #Algorithm
    # take first set A from list
    # for each other set B in the list do if B has common element(s) with A join B into A; 
    # remove B from list
    # repeat 2. until no more overlap with A
    # put A into list_merge
    # repeat 1. with rest of list

    common_list = []
    while len(l) > 0:
        #first element of list , and the rest element of the list
        first, *rest = l
        first = set(first)

        #temp variable
        temp_var = 0

        while len(first) > temp_var:
            temp_var = len(first)

            rest2 = []
            for r in rest:
                # if first and rest can intersection , join
                if len(first.intersection(set(r))) > 0:
                    first |= set(r)
                else:
                    rest2.append(r)
            rest = rest2

        common_list.append(list(first))
        l = rest

    return (common_list)






def calculate_sprites_corrdinate(l, dict_of_sprite):
    """The function calculate coordinate of each sprites
    
    Arguments:
        l {list} -- 2d Array
        dict_of_sprite {dict} -- a dict of label after reduce
    
    Returns:
        l {list} -- 2d array of label map 
        dict_sprites{dict} -- dict of sprite objects
    """
  
    dict_cordinate_sprite = {}
    dict_sprites = {}
    # get all coordinate of a sprites
    for row in range(len(l)):
        for column in range(len(l[0])):
            if l[row][column] > 0:
                dict_cordinate_sprite.setdefault(dict_of_sprite[l[row][column]],\
                     []).append((row, column))



    for key, value in dict_cordinate_sprite.items():
        temp_x = []
        temp_y = []
        for x in value:
            if x[0] not in temp_x:temp_x.append(x[0])
            if x[1] not in temp_y:temp_y.append(x[1])

        y1 = min(temp_x)
        y2 = max(temp_x)
        x1 = min(temp_y)
        x2 = max(temp_y)
        #create sprites obj
        sprite = Sprite(key,x1,y1,x2,y2)
        dict_sprites.setdefault(key,sprite)

    return dict_sprites,l


def create_sprite_labels_image(sprites,label_map,background_color = None):
    """
    The function create_sprite_labels_image that takes two arguments sprites and label_map, 
    the same returned by the function find_sprites.
    
    Arguments:
        sprites {dict} -- a dict of sprite objs
        label_map {list} -- 2d array 
    
    Keyword Arguments:
        back_ground {tuple} -- back ground color (default: {(255, 255, 255)})
    
    Returns:
        l {list} -- 2d array of label map 
        dict_sprites{dict} -- dict of sprite objects
    """


    width = len(label_map[0])
    heigh = len(label_map)
    if background_color == None : back_ground = (255,255,255)
    else : back_ground = background_color
    #Create a new image
    img = Image.new('RGB', (width, heigh), color = back_ground)

    pix = img.load()
    dict_image_color = {}

    #set key and color
    for key in sprites.keys():
        random_color = np.random.choice(a = COLOR)
        dict_image_color.setdefault(key,random_color)

    #draw image
    for row in range(heigh):
        for column in range(width):
            if label_map[row][column] in dict_image_color : 
                pix[column,row] = DICT_COLOR[dict_image_color[label_map[row][column]]]

    #draw border
    for key,values in sprites.items():
        top_left = values.top_left
        bottom_right = values.bottom_right
        x1 = top_left[0]
        x2 = bottom_right[0]
        y1 = top_left[1]
        y2 = bottom_right[1]

        shapex1 = [x1,y1,x2,y1]
        shapey1 = [x1,y2,x2,y2]
        shapex2 = [x1,y1,x1,y2]
        shapex3= [x2,y1,x2,y2]
        img1 = ImageDraw.Draw(img)

        img1.line(shapex1, fill = DICT_COLOR[dict_image_color[key]], width = 0)
        img1.line(shapey1, fill = DICT_COLOR[dict_image_color[key]], width = 0)
        img1.line(shapex2, fill = DICT_COLOR[dict_image_color[key]], width = 0)
        img1.line(shapex3, fill = DICT_COLOR[dict_image_color[key]], width = 0)


    return img


class SpriteSheet:
    def __init__(self,fd,background_color= None):
    
        self.__fd = fd
        self.__background_color = background_color

    @property
    def background_color(self):
        
        if self.__background_color == None :
            self.__background_color = self.__find_most_common_color(self.__fd)
            return self.__background_color

        return self.__background_color

    @staticmethod
    def __find_most_common_color(image):
        
        if image.mode == IMAGE_RGBA or image.mode == IMAGE_RGB:

            image = max(image.getcolors(image.size[0] * image.size[1]))
            
            return (image[1])
        else: return(0,0,0,0)


    def find_sprites(self,image):
        common_color = self.__find_most_common_color(self.__fd)
        label_map = []
        #get width ,high of image
        w, h = image.size
        data = image.load()
        #Create a table with w and h of image
        Matrix =  [[0 for x in range(w)] for y in range(h)]

        #Replace background =0 , color = 1
        for x in range(h):
            for y in range(w):
                color = data[y, x]
                if color != common_color: Matrix[x][y] = 1
                else : Matrix[x][y] = 0

        label_map = self.__label_pixel(Matrix)
        label_map, dict_test = self.__sprite(label_map)
        l , sprites = self.__calculate_sprites_corrdinate(label_map, dict_test)

        return l,sprites



    @staticmethod
    def __label_pixel(label_map):
        #width and height of the photo
        width_label_map = len(label_map[0])
        heigh_label_map = len(label_map)


        label = 0
        for row in range(heigh_label_map):
            for column in range(width_label_map):

                try:
                    x = label_map[row][column]

                    if x > 0:
                        if label_map[row][column - 1] == 0 \
                                and label_map[row - 1][column + 1] == 0 \
                                and label_map[row - 1][column] == 0 \
                                and label_map[row - 1][column - 1] == 0:
                            label = label + 1
                            label_map[row][column] = label

                        else:

                            if label_map[row - 1][column - 1] > 0:
                                label_map[row][column] = label_map[row - 1][column - 1]

                            if label_map[row - 1][column] > 0:
                                label_map[row][column] = label_map[row - 1][column]

                            if label_map[row - 1][column + 1] > 0:
                                label_map[row][column] = label_map[row - 1][column + 1]

                            if label_map[row][column - 1] > 0:
                                label_map[row][column] = label_map[row][column - 1]

                except:
                    continue

        return label_map


    def __sprite(self,label_map):
        width_label_map = len(label_map[0])
        heigh_label_map = len(label_map)

        dict_labelid = {}
        for row in range(heigh_label_map):
            for column in range(width_label_map):

                try:
                    x = label_map[row][column]

                    if x > 0:

                        if label_map[row - 1][column - 1] > 0:
                            dict_labelid.setdefault(x, []).append(label_map[row - 1][column - 1])

                        if label_map[row - 1][column] > 0:
                            dict_labelid.setdefault(x, []).append(label_map[row - 1][column])

                        if label_map[row - 1][column + 1] > 0:
                            dict_labelid.setdefault(x, []).append(label_map[row - 1][column + 1])

                        if label_map[row][column - 1] > 0:
                            dict_labelid.setdefault(x, []).append(label_map[row][column - 1])

                        if (label_map[row - 1][column - 1] + label_map[row - 1][column] + label_map[row - 1][column + 1] +label_map[row][column - 1]) == 0:
                            dict_labelid.setdefault(label_map[row][column], []).append(label_map[row][column])

                except:
                    continue

        common_element_list = [] #joint all sublist have same value
        dict_neighborhood = {} #dicttionary of realated labels in a sprite

        for key, value in dict_labelid.items():
            appendkey = sorted(list(set(value)))
            if key not in appendkey:appendkey.append(key)

            common_element_list.append(list(set(value)))

        list_a = self.__return_common_elemens(common_element_list)


        for data in list_a:
            dict_neighborhood.setdefault(min(data), data)


        dict_new = {}
        #change value to key,key to value
        for key in dict_neighborhood:
            for value in dict_neighborhood[key]:
                dict_new[value] = key

        #if neighbor have min value, reduce current corrdinate to min value
        for row in range(heigh_label_map):
            for column in range(width_label_map):
                if label_map[row][column] > 0:
                    label_map[row][column] = dict_new[label_map[row][column]]

        return label_map, dict_new

    @staticmethod
    def __return_common_elemens(l):
        """The funtion group all sublist if sublist have same element 
        
        Arguments:
            l {list} -- a list of many sublist
        
        Returns:
            common_list -- a list with all grouped sub list
        """

        #Algorithm
        # take first set A from list
        # for each other set B in the list do if B has common element(s) with A join B into A; 
        # remove B from list
        # repeat 2. until no more overlap with A
        # put A into list_merge
        # repeat 1. with rest of list

        common_list = []
        while len(l) > 0:
            #first element of list , and the rest element of the list
            first, *rest = l
            first = set(first)

            #temp variable
            temp_var = 0

            while len(first) > temp_var:
                temp_var = len(first)

                rest2 = []
                for r in rest:
                    # if first and rest can intersection , join
                    if len(first.intersection(set(r))) > 0:
                        first |= set(r)
                    else:
                        rest2.append(r)
                rest = rest2

            common_list.append(list(first))
            l = rest

        return (common_list)

    @staticmethod
    def __calculate_sprites_corrdinate(l, dict_of_sprite):


        dict_cordinate_sprite = {}
        dict_sprites = {}
        for row in range(len(l)):
            for column in range(len(l[0])):
                if l[row][column] > 0:
                    dict_cordinate_sprite.setdefault(dict_of_sprite[l[row][column]],\
                        []).append((row, column))



        for key, value in dict_cordinate_sprite.items():
            temp_x = []
            temp_y = []
            for x in value:
                if x[0] not in temp_x:temp_x.append(x[0])
                if x[1] not in temp_y:temp_y.append(x[1])

            y1 = min(temp_x)
            y2 = max(temp_x)
            x1 = min(temp_y)
            x2 = max(temp_y)
            #create sprites obj
            sprite = Sprite(key,x1,y1,x2,y2)
            dict_sprites.setdefault(key,sprite)

        return l , dict_sprites


    def create_sprite_labels_image(self):
        l,sprites = self.find_sprites(self.__fd)
        width = len(l[0])
        heigh = len(l)
 
        img = Image.new('RGB', (width, heigh), color = self.background_color)

        pix = img.load()
        dict_image_color = {}

        for key in sprites.keys():
            random_color = np.random.choice(a = COLOR)
            dict_image_color.setdefault(key,random_color)

        #draw image
        for row in range(heigh):
            for column in range(width):
                if l[row][column] in dict_image_color : 
                    pix[column,row] = DICT_COLOR[dict_image_color[l[row][column]]]

        #draw border
        for key,values in sprites.items():
            top_left = values.top_left
            bottom_right = values.bottom_right
            x1 = top_left[0]
            x2 = bottom_right[0]
            y1 = top_left[1]
            y2 = bottom_right[1]

            shapex1 = [x1,y1,x2,y1]
            shapey1 = [x1,y2,x2,y2]
            shapex2 = [x1,y1,x1,y2]
            shapex3= [x2,y1,x2,y2]
            img1 = ImageDraw.Draw(img)

            img1.line(shapex1, fill = DICT_COLOR[dict_image_color[key]], width = 0)
            img1.line(shapey1, fill = DICT_COLOR[dict_image_color[key]], width = 0)
            img1.line(shapex2, fill = DICT_COLOR[dict_image_color[key]], width = 0)
            img1.line(shapex3, fill = DICT_COLOR[dict_image_color[key]], width = 0)


        img.show()
        return img

def main():
    pass

    #------------------------------------------------------------------------------------------------------------
    # start_time = time.time()

    # image = Image.open('optimized_sprite_sheet.png')
    # sprite = SpriteSheet(image,(255,255,255))
    # sprite = sprite.create_sprite_labels_image()
    # print(sprite)
    # print("--- %s seconds ---" % (time.time() - start_time))
    #print(len(sprites))

if __name__ == "__main__":
    main()
