import requests

import os.path, errno, logging, stat, functools, io

from refuse.high import FUSE, FuseOSError, Operations

def nim():
    raise FuseOSError(errno.ENOSYS)

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
        is_dir = False
        if entry[-1] == "/":
            is_dir = True
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

class ENOENT(Exception): pass

class OffBotJava:
    def __init__(self):
        self.session = requests.sessions.Session()
        self.session.request = functools.partial(self.session.request, timeout=1)

    def __call__(self, op, *args):
        if not hasattr(self, op):
            raise FuseOSError(errno.ENOSYS)
        return getattr(self, op)(*args)

    def _get(self, endpoint, **kwargs):
        assert endpoint.startswith("/")
        return self.session.get(f"http://192.168.43.1:8080{endpoint}", **kwargs)

    def _post(self, endpoint, **kwargs):
        assert endpoint.startswith("/")
        return self.session.post(f"http://192.168.43.1:8080{endpoint}", **kwargs)

    def __get_tree(self):
        d = self._get("/java/file/tree").json()
        tree = TheFileTree()
        for entry in d['src']:
            tree.add_entry(entry)
        return tree

    def _get_tree(self, *args, **kwargs):
        try:
            return self.__get_tree(*args, **kwargs)
        except FuseOSError:
            raise
        except Exception:
            raise FuseOSError(errno.EIO)

    def __get_file(self, file: str):
        f = self._get("/java/file/get", params={"f": "/src" + file})
        if f.status_code == 404:
            raise ENOENT()
        assert f.status_code == 200, f"{f} -> {f.content}"
        return f.content

    def _get_file(self, file: str):
        try:
            return self.__get_file(file)
        except ENOENT:
            raise
        except Exception:
            raise FuseOSError(errno.EIO)

    def __save_file(self, file: str, content: bytes):
        payload = {"data": content}
        qs = {"f": "/src" + file}
        f = self._post("/java/file/save", params=qs, data=payload)
        assert f.status_code == 200, f"{f} -> {f.request.headers} -> {f.content}"
        return f.content

    def _save_file(self, file: str, content: bytes):
        try:
            return self.__save_file(file, content)
        except Exception:
            raise FuseOSError(errno.EIO)

    def __create_file(self, file: str):
        payload = {"new": 1, "teamName": "FIRST Tech Challenge Team FTC"}
        qs = {"f": "/src" + file}
        f = self._post("/java/file/new", params=qs, data=payload)
        assert f.status_code == 200, f"{f} -> {f.request.headers} -> {f.content}"
        assert f.json()['success'] == "true"

    def _create_file(self, file: str):
        try:
            return self.__create_file(file)
        except Exception:
            raise FuseOSError(errno.EIO)

    def _get_file_size(self, file):
        # HEAD doesn't work (content-length is missing) and GET uses transfer encoding,
        # so we really do have to read the entire file.
        # (Not necessarily into RAM, but we might as well at this point.)
        return len(self._get_file(file))

    def access(self, path, amode):
        return 0

    def create(self, path, mode, fi=None):
        raise FuseOSError(errno.EIO)

    def flush(self, path, fh):
        return 0

    def fsync(self, path, datasync, fh):
        return 0

    def fsyncdir(self, path, datasync, fh):
        return 0

    def getattr(self, path, fh=None):
        '''
        Returns a dictionary with keys identical to the stat C structure of
        stat(2).

        st_atime, st_mtime and st_ctime should be floats.

        NOTE: There is an incompatibility between Linux and Mac OS X
        concerning st_nlink of directories. Mac OS X counts all files inside
        the directory, while Linux counts only the subdirectories.
        '''
        tree: TheFileTree = self._get_tree()
        ent = tree.get_entry(path)
        if ent is None:
            raise FuseOSError(errno.ENOENT)
        if ent.is_directory():
            # st_nlink includes . and ..
            return dict(st_mode=(stat.S_IFDIR | 0o644), st_nlink=2 + len(ent.values()))
        return dict(st_mode=(stat.S_IFREG | 0o666), st_nlink=0, st_size=self._get_file_size(path))

    def readdir(self, path, fh):
        tree = self._get_tree()
        dir = tree.get_entry(path)
        if dir is None:
            raise FuseOSError(errno.ENOENT)
        if not dir.is_directory():
            raise FuseOSError(errno.ENOTDIR)
        contents = list(dir.keys())
        return [".", ".."] + contents

    def read(self, path, size, offset, fh):
        try:
            file = self._get_file(path)
        except ENOENT:
            raise FuseOSError(errno.ENOENT)
        bio = io.BytesIO(file)
        bio.seek(offset)
        return bio.read(size)

    def write(self, path, data, offset, fh):
        try:
            file = self._get_file(path)
        except ENOENT:
            file = b""
        bio = io.BytesIO(file)
        bio.seek(offset)
        r = bio.write(data)
        bio.seek(0)
        self._save_file(path, bio.read())
        return r

    def create(self, path, mode):
        if mode | stat.S_IFREG:
            # File
            self._create_file(path)
            self._save_file(path, b"")
            return 0
        return nim()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('mount')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(OffBotJava(), args.mount, foreground=True, allow_other=True, nothreads=False)
