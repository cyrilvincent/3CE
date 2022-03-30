from colordetect.color_detect import ColorDetect
path = "tests/images/tumblr1.jpg"
my_image = ColorDetect(path)
print(my_image.get_color_count(color_format="rgb"))
my_image = ColorDetect(path)
print(my_image.get_color_count(color_format="human_readable"))
my_image = ColorDetect(path)
print(my_image.get_color_count(color_format="css2"))
my_image = ColorDetect(path)
print(my_image.get_color_count(color_format="css21"))

