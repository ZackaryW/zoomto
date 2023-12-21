# zoomto
zoom automation tools

## Install
```
pip install zoomto
```

## Usage
```py
from zoomto.core.main import ZoomTo

z = ZoomTo()
z.config.debug_all = True

z.share_video(
    "D:\\@download\\video (2160p).mp4",
    send_to_monitor=4,
    maximize=True
)
```