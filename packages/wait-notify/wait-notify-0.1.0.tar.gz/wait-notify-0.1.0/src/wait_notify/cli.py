import click
import psutil
from halo import Halo
from pushover import Client

pushover = Client()

@click.command()
@click.argument("pid", type=int)
def main(pid):
  assert pid is not 0
  proc = psutil.Process(pid)
  cmdline = proc.exe() + " " + " ".join(proc.cmdline())
  with Halo(f"Waiting for {pid}", spinner="line"):
    proc.wait()
    pushover.send_message(cmdline, title=f"Waited for {pid} to complete")

