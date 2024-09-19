import requests
import click
import arrow
import colorama

colorama.just_fix_windows_console()

import os, sys, os.path, pathlib, dbm, time, json, traceback

from websockets.sync.client import connect

try:
    rc_info = requests.get("http://192.168.43.1:8080/js/rcInfo.json").json()
except Exception:
    traceback.print_exc()
    print("Could not connect to robot.")
    sys.exit(4)
print(f"Connected to {rc_info['deviceName']} (SSID: {rc_info['networkName']})")

class TheFileTree:
    def __init__(self):
        self.tree = Directory()

    def add_entry(self, entry):
        is_dir = False
        if entry[-1] == "/":
            is_dir = True
            entry = entry.rstrip("/")
        dirname, basename = entry.rsplit("/", 1)
        if is_dir:
            basename += "/"
        dirname += "/"
        current = self.get_entry(dirname)
        assert basename not in current
        if is_dir:
            current[basename.rstrip("/")] = Directory()
        else:
            current[basename] = File()

    def get_entry(self, entry):
        if entry == "/":
            if "" not in self.tree:
                self.tree[""] = Directory()
            return self.tree[""]
        entry = entry.rstrip("/")
        dirname, basename = entry.rsplit("/", 1)
        current = self.tree
        for dir in dirname.split("/"):
            if dir not in current:
                current[dir] = Directory()
            current = current[dir]
        if basename in current:
            return current[basename]
        return None

class File(int):
    def is_file(self):
        return True

    def is_directory(self):
        return False

class Directory(dict):
    def is_file(self):
        return False

    def is_directory(self):
        return True

session = requests.sessions.Session()

def get(endpoint, **kwargs):
    assert endpoint.startswith("/")
    return session.get(f"http://192.168.43.1:8080{endpoint}", **kwargs)

def post(endpoint, **kwargs):
    assert endpoint.startswith("/")
    return session.post(f"http://192.168.43.1:8080{endpoint}", **kwargs)

def get_tree():
    d = get("/java/file/tree").json()
    tree = TheFileTree()
    for entry in d['src']:
        tree.add_entry(entry)
    return tree

def save_file(file: str, content: bytes):
    payload = {"data": content}
    qs = {"f": "/src" + file}
    f = post("/java/file/save", params=qs, data=payload)
    assert f.status_code == 200, f"{f} -> {f.request.headers} -> {f.content}"
    return f.content

def create_file(file: str):
    payload = {"new": 1, "teamName": "FIRST Tech Challenge Team FTC"}
    qs = {"f": "/src" + file}
    f = post("/java/file/new", params=qs, data=payload)
    assert f.status_code == 200, f"{f} -> {f.request.headers} -> {f.content}"
    assert f.json()['success'] == "true"

def get_file(file: str):
    f = get("/java/file/get", params={"f": "/src" + file})
    if f.status_code == 404:
        assert f.content == b"File Not Found!"
        return None
    assert f.status_code == 200, f"{f} -> {f.content}"
    return f.content

def build():
    with connect("ws://192.168.43.1:8081/") as sock:
        def send(d):
            sock.send(json.dumps(d))

        send({
            "namespace": "system",
            "type": "subscribeToNamespace",
            "payload": "ONBOTJAVA"
        })
        send({
            "namespace": "ONBOTJAVA",
            "type": "build:launch",
            "payload": ""
        })
        status = "WAITING"
        while True:
            msg = json.loads(sock.recv())
            assert msg['namespace'] == "ONBOTJAVA", f"Unexpected namespace in {msg}"
            assert msg['type'] == "build:status", f"Unexpected message type in {msg}"
            payload = json.loads(msg['payload']) # Yo dawg, I heard you like JSON...
            #print("\x1b[H\x1b[2J", end="", flush=True)
            print(f"\n=== Build started {arrow.get(payload['startTimestamp'])} ===")
            status = payload['status']
            if status in ("FAILED", "SUCCESSFUL"):
                break
            print(f"\x1b[2KBuilding is {status}.\x1b[3A")
        if status == "FAILED":
            print("\x1b[1;31m=== BUILD FAILED ===\x1b[0m")
            print(requests.get("http://192.168.43.1:8080/java/build/wait").text)
        elif status == "SUCCESSFUL":
            print("=== BUILD SUCCEEDED ===")
        else:
            raise RuntimeError(f"Unreachable code; status={status}")

config_home = pathlib.Path(os.environ.get('APPDATA') or
             os.environ.get('XDG_CONFIG_HOME') or
             os.path.join(os.environ['HOME'], '.config'),
)
config_home.mkdir(parents=True, exist_ok=True)

@click.command()
@click.argument("indir")
@click.argument("outdir", default="/org/firstinspires/ftc/teamcode")
def main(indir, outdir):
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
    build()

if __name__ == "__main__":
    main()
