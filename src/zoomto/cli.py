import os
import click

from zoomto.hook import share_video
from zoomto.utils import wait_timer

@click.group()
def cli():
    pass

@cli.command()
@click.argument("video_path")
@click.option("--timer", "-t", help="wait timer in seconds")
@click.option("--no-start", "-n", is_flag = True, help="Don't start the video")
def video(video_path, timer, no_start):
    if timer:
        wait_timer(timer)

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"File {video_path} does not exist")

    full_path = os.path.abspath(video_path)

    share_video(full_path, not no_start)

@cli.command()
@click.option("--port", default=5001, help="Port to run server on")
def server(port):
    from zoomto.server import start_server
    start_server(port=port)

if __name__ == "__main__":
    cli()