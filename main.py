
from zoomto.core.zoomto import ZoomTo
from zoomto.core.cfg import config

config.debug_all = True

x = ZoomTo()
x.share_video("example/demo.mp4", maximize=True)