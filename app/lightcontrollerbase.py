from abc import ABC, abstractmethod
from hexcolor import HexColor
from typing import List

class LightController(ABC):
    def __init__(self, pixel_count):
        self._pixel_count = pixel_count

    @abstractmethod
    def set_single_color(self, color: HexColor):
        pass
    
    @abstractmethod
    def set_multiple_colors(self, colors: List[HexColor]):
        pass