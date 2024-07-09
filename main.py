import argparse
import os


def setup_env():
    os.environ["MEPHISTO_DEBUG"] = "1" if args.debug else "0"
    os.environ["MEPHISTO_TRACE"] = "1" if args.trace else "0"
    os.environ["MEPHISTO_NO_CONSOLE"] = "1" if args.no_console else "0"
    os.environ["MEPHISTO_NO_DAEMON"] = "1" if args.no_daemon else "0"
    os.environ["MEPHISTO_NO_RICHURU"] = "1" if args.no_richuru else "0"
    os.environ["MEPHISTO_DAEMON_PORT"] = str(args.daemon_port)


def main():
    if os.environ["MEPHISTO_NO_DAEMON"] == "0":
        from mephisto.daemon import launch_daemon

        os.environ["MEPHISTO_DAEMON_TOKEN"] = ""
        launch_daemon(int(os.environ["MEPHISTO_DAEMON_PORT"]))
    else:
        import sys

        from mephisto.__main__ import run

        os.chdir("mephisto")
        sys.path.append(os.path.join(os.getcwd()))

        run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--trace", action="store_true")
    parser.add_argument("--no-console", action="store_true")
    parser.add_argument("--no-daemon", action="store_true")
    parser.add_argument("--no-richuru", action="store_true")
    parser.add_argument("--daemon-port", type=int, default=0)
    args = parser.parse_args()

    setup_env()
    main()
