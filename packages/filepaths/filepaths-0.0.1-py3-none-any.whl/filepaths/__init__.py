import os
from addict import Dict


class BadDirectoryName(Exception):
    pass


def path_recursion(path, ignore_hidden=True):
    result = Dict()
    root = [x for x in os.walk(path)][0][0]
    dirs = [x for x in os.walk(path)][0][1]
    all_files = [x for x in os.walk(path)][0][2]

    exceptions = ['files', 'dirs', 'path', 'filepaths']
    for exception in exceptions:
        if exception in dirs:
            raise BadDirectoryName('\nUse of '
                                   f'"{exception}" '
                                   'as a directory name is ambiguous.')

    if ignore_hidden:
        files = [f for f in all_files if f[0] != '.' and f[0] != '_']
        dirs[:] = [d for d in dirs if d[0] != '.' and d[0] != '_']
    else:
        files = all_files

    result['files'] = files
    result['path'] = root
    result['dirs'] = dirs
    filepaths = []
    if len(files):
        for file in files:
            filepaths.append(os.path.join(root, file))
    result['filepaths'] = filepaths

    for folder in dirs:
        result[folder] = path_recursion(os.path.join(root, folder))

    return result


class Root():

    def __init__(self, depth=1, ignore_hidden=True):
        self.depth = depth
        self.ignore_hidden = ignore_hidden
        self.set_basepath()

    def set_basepath(self):
        if self.depth:
            for _ in range(self.depth):
                os.chdir('..')

        self.basepath = os.path.abspath('')

    def paths(self):
        return path_recursion(self.basepath, self.ignore_hidden)


if __name__ == "__main__":
    root = Root(0).paths()
    print(root.testfolder.insidetest.filepaths)
