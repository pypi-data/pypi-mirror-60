import json
import os

import necxxt.utils.logging


def listCompilers():
    compilers = []

    for path in os.environ["PATH"].split(os.pathsep):
        compilers.extend(
            listFiles(path, filters=["clang++", "g++"], shorten=False))

    return compilers


def listFiles(d, filters=[], shorten=True):
    fs = []

    for path, subdirs, files in os.walk(d):
        for name in files:
            add = False
            if len(filters) == 0:
                add = True
            else:
                for f in filters:
                    if name.endswith(f):
                        add = True

            if add:
                p = os.path.join(path, name)
                if shorten:
                    fs.append(os.path.relpath(p, d))
                else:
                    fs.append(p)

    return fs


def readJson(path):
    if not os.path.isfile(path):
        necxxt.utils.logging.error(
            "ENOENT: no such file or directory, open '{}'".format(path))
        exit(1)

    content = {}
    with open(path, "r") as f:
        content = json.load(f)

    return content


def readModule(dependency=None):
    if dependency:
        module_file = os.path.join(
            os.getcwd(), "necxxt_modules", dependency, "necxxt.json")
    else:
        module_file = os.path.join(os.getcwd(), "necxxt.json")

    return readJson(module_file)


def writeJson(path, content):
    with open(path, "w") as f:
        json.dump(content, f, indent=4)
        f.write("\n")


def writeModule(content):
    path = os.path.join(os.getcwd(), "necxxt.json")
    writeJson(path, content)
