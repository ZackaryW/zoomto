from zoomto.core.zoomto import ZoomTo


z = ZoomTo()
z.share_video(
    path="example/demo.mp4",
    send_to_monitor=4,
    maximize=True
)