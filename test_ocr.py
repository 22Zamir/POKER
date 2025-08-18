import pytesseract
from PIL import ImageGrab
import cv2
import numpy as np

from interface.screen_reader import ScreenReader

# Укажи путь к tesseract вручную
reader = ScreenReader()
stacks = reader.detect_stacks()
print(stacks)