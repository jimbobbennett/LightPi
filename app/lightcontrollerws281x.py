import board, neopixel
from lightcontrollerbase import LightController
from hexcolor import HexColor
from typing import List

class LightController_WS281x(LightController):

    def __init__(self, pixel_count):
        super(LightController_WS281x, self).__init__(pixel_count)        
        self.__pixels = neopixel.NeoPixel(board.D18, self._pixel_count, auto_write=False)

    def set_single_color(self, color: HexColor):
        self.__pixels.fill(color.rgb)
        self.__pixels.show()
    
    def set_multiple_colors(self, colors: List[HexColor]):
        color_count = len(colors)
        index = 0

        for x in range(self._pixel_count):
            color = colors[index]
            self.__pixels[x] = color.rgb
            index = index + 1
            if index >= color_count:
                index = 0

        self.__pixels.show()