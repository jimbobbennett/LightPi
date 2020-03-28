import unicornhat as uh
from lightcontrollerbase import LightController
from color import Color
from typing import List

class LightController_UnicornHat(LightController):

    def __init__(self, pixel_count):
        super(LightController_UnicornHat, self).__init__(pixel_count)  
        uh.set_layout(uh.PHAT)
        uh.brightness(1)
    
    def set_single_color(self, color: Color):
        #uh.set_all(r_value, g_value, b_value)
        uh.show()
    
    def set_multiple_colors(self, colors: List[Color]):
        #uh.set_all(r_value, g_value, b_value)
        uh.show()