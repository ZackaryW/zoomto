from dataclasses import dataclass
from zrcl3.singleton import SingletonMeta

@dataclass
class _ZoomConfig(metaclass=SingletonMeta):
    debug_image :       bool = False
    debug_screeninfo :  bool = False
    debug_log :         bool = False

    @property
    def debug_all(self):
        return all(v is True for k, v in self.__dict__.items() if k.startswith("debug_"))
    
    @debug_all.setter
    def debug_all(self, value):
        for k, v in self.__dict__.items():
            if k.startswith("debug_"):
                self.__dict__[k] = value

config = _ZoomConfig()

__all__ = [
    "config",
]