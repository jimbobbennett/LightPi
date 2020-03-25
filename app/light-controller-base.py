from abc import ABC, abstractmethod
from colour import Color
from typing import List

class LightController(ABC):
    @abstractmethod
    def set_single_color(self, color : Color):
        pass
    
    @abstractmethod
    def set_multiple_colors(self, colors : List[Color]):
        pass