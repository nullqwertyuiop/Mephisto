import argparse
import os

from mephisto.daemon import launch_daemon

parser = argparse.ArgumentParser()
parser.add_argument("--no-console", action="store_true")
args = parser.parse_args()

if args.no_console:
    os.environ["MEPHISTO_NO_CONSOLE"] = "1"


launch_daemon()
