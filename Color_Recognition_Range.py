# https://github.com/walton-wang929/Color_Recognition
import colorsys

import numpy as np
import cv2
import base64

path = 'tests/images/tumblr1.jpg'
# from base64
b64 = None
with open(path, "rb") as f:
    bytes = f.read()
    b64 = base64.b64encode(bytes)
    print(b64)

bytes = base64.b64decode(b64)
array = np.frombuffer(bytes, np.uint8)
image = cv2.imdecode(array, cv2.IMREAD_COLOR)

# load the image
image = cv2.imread(path)

#==============================================================================
# name = Color_Recognition_Range(image)
# cv2.putText(image,name,(10, 10), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),2)
# cv2.imshow("images", image)
# cv2.waitKey(5000)
# 
# cv2.destroyAllWindows()    
#==============================================================================
image = cv2.GaussianBlur(image, (11, 11), 0) # Optionnel inspiré de color_detect, abaisse le nb de couleur
image_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  
   
dictionary ={ # 16 colors
                    'White':([0, 0, 146], [180, 34, 255]), # /!\ Ce n'est pas du RGB mais du HSV
                    # 'Gray':([0, 0, 22], [180, 34, 146]), # Les angle H sont en degré sur 180 et non 360 mais S V en 255 et non en %
                    'Light-red':([0,157, 25], [6,255,255]),
                    'Light-Pink':([0,0, 25], [6,157,255]),
                    'Orange':([6, 33, 168], [23, 255, 255]),
                    'Brown':([6, 33, 25], [23, 255, 168]),
                    'Yellow':([23, 33, 25], [32, 255, 255]),
                    'Green':([32, 33, 25], [75, 255, 255]), 
                    'Blue-Green':([75, 33, 25], [90, 255, 255]), 
                    'Blue':([90,33, 45], [123, 255, 255]),
                    'Purple':([123, 112, 25], [155, 255, 255]),
                    'Light-Purple':([123, 33, 25], [155, 125, 255]),                   
                    'Pink':([155,34, 25], [180,225,255]),
                    'Deep-Pink':([175,0, 25], [180,157,255]),
                    'Deep-red':([175,157, 25], [180,255,255]),    
                    # 'black':([0, 0, 0], [180, 255, 26]),
                    }

# dictionary ={ # 9 colors
#                     'White':([0, 0, 116], [180, 57, 255]),
#                     'orange':([10, 38, 71], [20, 255, 255]),
#                     'yellow':([18, 28, 20], [33, 255, 255]),
#                     'green':([36, 10, 33], [88, 255, 255]),
#                     'blue':([87,32, 17], [120, 255, 255]),
#                     'purple':([138, 66, 39], [155, 255, 255]),
#                     'red': ([0, 38, 56], [10, 255, 255]),
#                     'red2':([170,112, 45], [180,255,255]),
#                     # 'black':([0, 0, 0], [179, 255, 50]),
#                     }


#     dictionary ={ # 12 colors
#                  'black':([0, 0, 0], [180, 255, 50]), 'blue':([88,70, 17], [112, 255, 255]),
#                 'orange':([0, 75, 0], [39, 255, 255]),'red':([112,131,130], [180,255,255]),
#                 'yellow':([20, 190, 20], [30, 255, 255]),'green':([57, 73, 0], [119, 255, 255]),
#                 'dark-red':([0, 107, 62], [6, 255, 255]),'Grey-blue':([88,70, 17], [112, 255, 255]),
#                 'White':([14, 0, 116], [180, 57, 255]),'Deep-purple':([18, 33, 6], [147, 159, 114]),
#                 'brown':([0, 64, 0], [21, 255, 255]),'Gray':([22, 0, 0], [180, 62, 255]),
#                 }

#     dictionary ={ # 13 colors
#                  'black':([0, 0, 0], [179, 255, 50]), 'blue':([88,70, 17], [112, 255, 255]),
#                 'orange':([0, 75, 0], [39, 255, 255]),'red':([112,131,130], [180,255,255]),
#                 'yellow':([20, 190, 20], [30, 255, 255]),'green':([57, 73, 0], [119, 255, 255]),
#                 'dark-red':([0, 107, 62], [6, 255, 255]),'Grey-blue':([88,70, 17], [112, 255, 255]),
#                 'White':([14, 0, 116], [180, 57, 255]),'Deep-purple':([18, 33, 6], [147, 159, 114]),
#                 'brown':([0, 64, 0], [21, 255, 255]),'Gray':([22, 0, 0], [180, 62, 255]),
#                 'purple':([138, 120, 77], [155, 255, 255])
#                 }



dico_avg = {}
for color in dictionary.keys():
    lower = dictionary[color][0]
    upper = dictionary[color][1]
    h = (lower[0] + upper[0]) / 2
    s = max(lower[1], upper[1])
    v = max(lower[2], upper[2])
    r, g, b = colorsys.hsv_to_rgb(h / 180, s / 255, v / 255)
    dico_avg[color] = (int(np.round(r * 255)), int(np.round(g * 255)), int(np.round(b * 255)))
    
color_name = []
color_count =[]
             
# loop over the boundaries
for key,(lower,upper) in dictionary.items():

    # create NumPy arrays from the boundaries
    lower = np.array(lower, dtype = "uint8")
    upper = np.array(upper, dtype = "uint8")

    # find the colors within the specified boundaries and apply
    # the mask

    # print(key)

    mask = cv2.inRange(image_HSV, lower, upper)
    mask = cv2.erode(mask, None, iterations=3) # Ces 2 lignes optionnelle enleve du bruit lié aux couleurs
    mask = cv2.dilate(mask, None, iterations=3) # Inspiré de color_detect

    # cv2.imshow("mask", mask)
    # cv2.waitKey(1000)
    # cv2.destroyAllWindows()

    count = cv2.countNonZero(mask)

    color_count.append(count)

    color_name.append(key)
        
    
color_count_array = np.array(color_count)
# fusion red et red2 toujours mis à la fin
if "red2" in dictionary:
    color_count_array[-2] += color_count_array[-1]
    color_count_array[-1] = 0

print(color_count_array)

i = 0
for cc in color_count_array:
    print(color_name[i], cc)
    i+=1

idx = np.argmax(color_count_array)

color = color_name[idx]

print ("the dominant color is:", color)
