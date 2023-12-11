from dataclasses import dataclass


@dataclass
class ZoomConfig:
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

GLOBAL_CONFIG : ZoomConfig = ZoomConfig()
