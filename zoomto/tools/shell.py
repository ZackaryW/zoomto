from time import sleep
import click_shell
import click
import os
import sys
import toml
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

from zoomto import ZoomTo 

@click_shell.shell(prompt='zoomto > ', intro='Welcome to zoomto!', invoke_without_command=True)
@click.pass_context
def shell(ctx : click.Context):
    ctx.ensure_object(dict)
    try:
        ctx.obj["z"] = ZoomTo() 
    except: # noqa
        print("Failed to initialize zoomto, please make sure a meeting is running.")
        os._exit(1)

@shell.command()
@click.argument("path", type=click.Path(exists=True))
@click.pass_context
def loadcfg(ctx, path):
    if "cfg" not in ctx.obj:
        ctx.obj["cfg"] = {}
    
    with open(path, "r") as f:
        ctx.obj["cfg"].update(toml.load(f))
    
@shell.command()
@click.argument("arg", type=click.STRING)
@click.pass_context
def runcfg(ctx : click.Context, arg : str):
    if arg in ctx.obj["cfg"]:
        kwargs = ctx.obj["cfg"][arg]
    elif (arg.isdigit() and int(arg) in ctx.obj["cfg"]):
        kwargs = ctx.obj["cfg"][int(arg)]
    
    click.echo(f"invoking: {arg}", err=True)
    ctx.invoke(sharevid, **kwargs)

@shell.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--send-to-monitor", "-s", type=click.INT, default=None, help="send screen to monitor")
@click.option("--maximize", "-m", type=click.BOOL, default=True, help="maximize window")
@click.option("--time", "-t", type=click.INT, default=None, help="time left to execute")
@click.option("--time-unit", "-u", type=click.Choice(["s", "m", "h"]), default="s", help="time unit")
@click.pass_context
def sharevid(ctx, path, send_to_monitor, maximize, time, time_unit):
    z : ZoomTo = ctx.obj["z"]

    if time is not None:
        time = time if time_unit == "s" else time * 60 if time_unit == "m" else time * 60 * 60
        while time > 0:

            print(
                # pad 00000
                f"Time left: {str(time).zfill(5)}", end="\r",
                flush= True
            )
            time -= 1

            sleep(1)

    z.share_video(path=path, send_to_monitor=send_to_monitor, maximize=maximize)

def runshell():
    shell()

if __name__ == "__main__":
    shell()
