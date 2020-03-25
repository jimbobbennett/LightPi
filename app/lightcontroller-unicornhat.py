import unicornhat as uh
from colour import Color

class LightController:

    def __init__(self):
        uh.set_layout(uh.PHAT)
        uh.brightness(1)
    
    def set_single_color(color : Color):
        uh.set_all(r_value, g_value, b_value)
        uh.show()
    
    def set_multiple_colors(colors : Color):
        uh.set_all(r_value, g_value, b_value)
        uh.show()