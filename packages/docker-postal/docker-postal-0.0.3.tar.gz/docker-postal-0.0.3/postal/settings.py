import os
import re

project = re.sub('[^0-9a-zA-Z]+', '-', os.path.basename(os.getcwd())).strip('-')
mode = 'development'
compose = f'stack/{mode}.yml'
