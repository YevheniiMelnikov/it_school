import os

from aiogram.types import FSInputFile

current_dir = os.path.dirname(os.path.abspath(__file__))

img_1 = FSInputFile(path=rf"{current_dir}\1.jpg")
img_2 = FSInputFile(path=rf"{current_dir}\2.jpg")
img_3 = FSInputFile(path=rf"{current_dir}\3.jpg")
