import requests, json, dataclasses

from websockets.sync.client import connect

def get_rc_info():
    rc_info = _get("/js/rcInfo.json").json()
    return rc_info

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

def _get(endpoint, **kwargs):
    assert endpoint.startswith("/")
    return session.get(f"http://192.168.43.1:8080{endpoint}", timeout=1, **kwargs)

def _post(endpoint, **kwargs):
    assert endpoint.startswith("/")
    return session.post(f"http://192.168.43.1:8080{endpoint}", timeout=1, **kwargs)

def get_tree():
    d = _get("/java/file/tree").json()
    tree = TheFileTree()
    for entry in d['src']:
        tree.add_entry(entry)
    return tree

def save_file(file: str, content: bytes):
    payload = {"data": content}
    qs = {"f": "/src" + file}
    f = _post("/java/file/save", params=qs, data=payload)
    assert f.status_code == 200, f"{f} -> {f.request.headers} -> {f.content}"
    return f.content

def create_file(file: str):
    payload = {"new": 1, "teamName": "FIRST Tech Challenge Team FTC"}
    qs = {"f": "/src" + file}
    f = _post("/java/file/new", params=qs, data=payload)
    assert f.status_code == 200, f"{f} -> {f.request.headers} -> {f.content}"
    assert f.json()['success'] == "true"

def get_file(file: str):
    f = _get("/java/file/get", params={"f": "/src" + file})
    if f.status_code == 404:
        assert f.content == b"File Not Found!"
        return None
    assert f.status_code == 200, f"{f} -> {f.content}"
    return f.content

def get_build_log():
    return _get("/java/build/wait").text

@dataclasses.dataclass
class BuildStatus:
    status: str
    start_ts: int

def build_stream():
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

        while True:
            msg = json.loads(sock.recv())
            assert msg['namespace'] == "ONBOTJAVA", f"Unexpected namespace in {msg}"
            assert msg['type'] == "build:status", f"Unexpected message type in {msg}"
            payload = json.loads(msg['payload']) # Yo dawg, I heard you like JSON...
            yield BuildStatus(payload['status'], payload['startTimestamp'])

class BuildFailedException(Exception): pass

def build():
    status = "WAITING"
    for payload in build_stream():
        status = payload.status
        if status == "FAILED":
            raise BuildFailedException(get_build_log())
        if status == "SUCCESSFUL":
            return

