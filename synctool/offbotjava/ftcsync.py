import click
import arrow
import colorama

colorama.just_fix_windows_console()

from . import *

import os, sys, os.path, pathlib, dbm, time, json, traceback

try:
    rc_info = get_rc_info()
except Exception:
    traceback.print_exc()
    print("Could not connect to robot.")
    sys.exit(4)
print(f"Connected to {rc_info['deviceName']} (SSID: {rc_info['networkName']})")

config_home = pathlib.Path(os.environ.get('APPDATA') or
             os.environ.get('XDG_CONFIG_HOME') or
             os.path.join(os.environ['HOME'], '.config'),
)
config_home.mkdir(parents=True, exist_ok=True)

@click.group()
def main():
    pass

def build_wrap():
    status = "WAITING"
    for payload in build_stream():
        #print("\x1b[H\x1b[2J", end="", flush=True)
        print(f"\n=== Build started {arrow.get(payload.start_ts)} ===")
        status = payload.status
        if status in ("FAILED", "SUCCESSFUL"): break
        print(f"\x1b[2KBuilding is {status}.\x1b[3A")
    if status == "FAILED":
        print("\x1b[1;31m=== BUILD FAILED ===\x1b[0m")
        print(get_build_log())
    elif status == "SUCCESSFUL":
        print("=== BUILD SUCCEEDED ===")
    else:
        assert False, f"Unreachable code! status={status}"

@main.command()
@click.argument("indir")
@click.argument("outdir", default="/org/firstinspires/ftc/teamcode")
def deploydir(indir, outdir):
    if not outdir.endswith("/"):
        outdir += "/"
    if not outdir.startswith("/"):
        outdir = "/" + outdir
    if sys.stdin.isatty():
        input("WARNING: This software will OVERWRITE any files that already exist on the robot.\n"
              "Press ENTER to continue. ")
    for entry in os.scandir(indir):
        with dbm.open(os.path.join(config_home, "OffBotJava.dbm"), "c") as db:
            entry: os.DirEntry = entry
            if not entry.name.endswith(".java"):
                continue
            if not entry.is_file(follow_symlinks=False):
                continue
            key = f"{indir}&-{outdir}:-{entry.name}$-{time.time()}-%s"
            print("Backing up", entry.name)
            contents = get_file(outdir + entry.name)
            if contents is None:
                print(entry.name, "does not exist on the robot, creating...")
                create_file(outdir + entry.name)
                contents = b""
            db[key % "before"] = contents
            print("Uploading", entry.name)
            with open(entry.path) as file:
                data = file.read()
                db[key % "after"] = data
                save_file(outdir + entry.name, data.encode())
    build_wrap()

if __name__ == "__main__":
    main()
