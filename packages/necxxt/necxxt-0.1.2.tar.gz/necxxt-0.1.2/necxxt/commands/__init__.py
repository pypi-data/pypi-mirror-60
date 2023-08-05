import copy
import json
import os
import pathlib
import shutil

from .build import checkIfModulesAreInstalled, precompileModules, compileModules, compileSources, buildStatic

import necxxt.dependencies
from necxxt.version import __executable__


class Command:
    def __init__(self):
        self._name = None

    def run(self):
        pass

    def __str__(self):
        return self._name


class HelpCommand(Command):
    def __init__(self):
        self._name = "help"
        self._executable = "necxxt"

    def run(self):
        print()
        print("Usage: {} <command>".format(__executable__))
        print()
        print("where <command> is one of:")
        print("    build, help, install")
        print()
        # print("Specify configs in the ini-formatted file:")
        # print("    {}".format(os.path.join(
        #     pathlib.Path.home(), ".{}rc".format(__executable__))))
        # print(
        #     "or on the command line via: {} < command > --key value".format(__executable__))
        # print("Config info can be viewed via: {} help config".format(__executable__))
        # print()
        print("{}@{} {}".format(__executable__, necxxt.__version__, __file__))


class BuildCommand(Command):
    def __init__(self):
        self._name = "build"

    def run(self):
        if os.path.isdir("build"):
            shutil.rmtree("build")

        lock_path = os.path.join(os.getcwd(), "necxxt-lock.json")
        if not os.path.isfile(lock_path):
            necxxt.utils.logging.error(
                "ENOENT: no such file or directory, open '{}'".format(lock_path))
            exit(1)

        with open(lock_path, "r") as f:
            lock = json.load(f)

        modules = {}
        for dependency in lock["dependencies"].keys():
            requires = lock["dependencies"][dependency].get("requires", {})
            modules[dependency] = list(requires.keys())

        build_modules = copy.deepcopy(modules)

        order = []
        i = 0
        while i < len(modules.keys()):
            keys = list(modules.keys())
            key = keys[i]
            dependencies = modules[key]

            if len(dependencies) == 0:
                order.append(key)
                del modules[key]
                for d in modules.keys():
                    if key in modules[d]:
                        modules[d].remove(key)

            i += 1

            length = len(modules.keys())
            if length > 0 and i >= length:
                i = 0

        checkIfModulesAreInstalled(order)
        precompileModules(order, build_modules)
        compileModules(order, build_modules)
        compileSources(order, build_modules)
        buildStatic(order, build_modules)


class InstallCommand(Command):
    def __init__(self):
        self._name = "install"

    def run(self):
        necxxt.dependencies.installDependencies()
