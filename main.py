import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--no-console", action="store_true")
parser.add_argument("--no-daemon", action="store_true")
args = parser.parse_args()


if __name__ == "__main__":
    if args.no_console:
        os.environ["MEPHISTO_NO_CONSOLE"] = "1"

    if not args.no_daemon:
        from mephisto.daemon import launch_daemon

        launch_daemon()
    else:
        import sys

        from mephisto.__main__ import run

        os.chdir("mephisto")
        sys.path.append(os.path.join(os.getcwd()))

        run()
