import copy
import json
import os
import pathlib
import shutil
import subprocess

from .build import checkIfModulesAreInstalled, precompileModules, compileModules, compileSources, buildStatic
from .coverage import checkCoverage
from .init import initialize

import necxxt.dependencies


class Command:
    def help(self):
        raise NotImplementedError

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def __str__(self):
        return self._name


class BuildCommand(Command):
    def help(self):
        print("Build a necxxt compatible project")

    def run(self, *args, **kwargs):
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


class CheckCoverageCommand(Command):
    def help(self):
        print("Check the coverage of a project")

    def run(self, *args, **kwargs):
        config = None
        coverage_info = None
        for key, value in kwargs.items():
            if key == "config":
                config = necxxt.utils.readJson(value)
            elif key == "coverage-info":
                coverage_info = value

        checkCoverage(config=config, coverage_info=coverage_info)


class InitCommand(Command):
    def help(self):
        print("Initialize a necxxt project")

    def run(self, *args, **kwargs):
        initialize()


class InstallCommand(Command):
    def help(self):
        print("Install the dependencies of a necxxt compatible project")

    def run(self, *args, **kwargs):
        necxxt.dependencies.installDependencies()


class RunCommand(Command):
    def help(self):
        print("Run the executable of a necxxt compatible project")

    def run(self, *args, **kwargs):
        lock_path = os.path.join(os.getcwd(), "necxxt-lock.json")
        if not os.path.isfile(lock_path):
            necxxt.utils.logging.error(
                "ENOENT: no such file or directory, open '{}'".format(lock_path))
            exit(1)

        with open(lock_path, "r") as f:
            lock = json.load(f)

        exe = os.path.join(os.getcwd(), "build", lock.get("name", ""))
        if not os.path.isfile(exe):
            necxxt.utils.logging.error(
                "ENOENT: no such file or directory, open '{}'".format(exe))
            exit(1)

        subprocess.call([exe])
