import os
import pathlib
import subprocess

import necxxt.utils
import necxxt.utils.logging

__env__ = {
    "CXX": "docker run -ti -v {}:/necxxt --rm necxxt/clang".format(os.getcwd()),
    "CXXFLAGS": "-std=c++2a -fmodules-ts"
}


def runCompiler(cmds):
    proc = subprocess.Popen(cmds)
    proc.communicate()

    if proc.returncode != 0:
        exit(proc.returncode)


def checkIfModulesAreInstalled(modules):
    for m in modules:
        p = os.path.join("necxxt_modules", m)
        if not os.path.isdir(p):
            necxxt.utils.logging.error(
                "Module {} is not installed".format({m}))
            exit(1)


def precompileModules(order, build_modules):
    for dependency in order:
        p = os.path.join("necxxt_modules", dependency)
        for f in necxxt.utils.listFiles(p, filters=[".cxxm"], shorten=False):
            i = f
            d = os.path.dirname(f)
            f = os.path.basename(f)
            name, extension = os.path.splitext(f)
            o = os.path.join("build", d, name + ".pcm")
            pathlib.Path(os.path.dirname(o)).mkdir(parents=True)

            modules = []
            for _m in build_modules.get(dependency, []):
                for _f in necxxt.utils.listFiles(os.path.join("build", "necxxt_modules",
                                                              _m), filters=[".pcm"], shorten=False):
                    if _f not in modules:
                        modules.append(_f)

            cmds = __env__["CXX"].split(" ")
            cmds.extend(__env__["CXXFLAGS"].split(" "))
            cmds.append("--precompile")
            cmds.append(i)

            for m in modules:
                cmds.append("-fmodule-file={}".format(m))

            cmds.append("-o")
            cmds.append(o)

            necxxt.utils.logging.debug(" ".join(cmds))
            runCompiler(cmds)


def compileModules(order, build_modules):
    for f in necxxt.utils.listFiles(os.getcwd(), filters=[".pcm"]):
        i = f
        d = os.path.dirname(f)
        f = os.path.basename(f)
        name, extension = os.path.splitext(f)
        o = os.path.join(d, name + ".pcm.o")

        cmds = __env__["CXX"].split(" ")
        cmds.extend(__env__["CXXFLAGS"].split(" "))
        cmds.append("-c")
        cmds.append(i)
        cmds.append("-o")
        cmds.append(o)

        necxxt.utils.logging.debug(" ".join(cmds))
        runCompiler(cmds)


def compileSources(order, build_modules):
    modules = []
    for f in necxxt.utils.listFiles(os.getcwd(), filters=[".pcm"]):
        if f not in modules:
            modules.append(f)

    for f in necxxt.utils.listFiles(os.getcwd(), filters=[".cxx"]):
        i = f
        d = os.path.dirname(f)
        f = os.path.basename(f)
        name, extension = os.path.splitext(f)
        o = os.path.join("build", d, name + ".cxx.o")
        pathlib.Path(os.path.dirname(o)).mkdir(parents=True)

        cmds = __env__["CXX"].split(" ")
        cmds.extend(__env__["CXXFLAGS"].split(" "))
        cmds.append("-c")
        cmds.append(i)

        for m in modules:
            cmds.append("-fmodule-file={}".format(m))

        cmds.append("-o")
        cmds.append(o)

        necxxt.utils.logging.debug(" ".join(cmds))
        runCompiler(cmds)


def buildStatic(order, build_modules):
    cmds = __env__["CXX"].split(" ")
    cmds.extend(__env__["CXXFLAGS"].split(" "))

    module_paths = {}
    objects = []
    for o in order:
        for f in necxxt.utils.listFiles(os.getcwd(), filters=[".pcm.o"]):
            d = os.path.dirname(f)
            if o in d:
                if d not in module_paths:
                    module_paths[d] = []

                if f not in module_paths[d]:
                    module_paths[d].append(f)

    for f in necxxt.utils.listFiles(os.getcwd(), filters=[".cxx.o"]):
        if f not in objects:
            objects.append(f)

    for module_path in module_paths.keys():
        cmds.append("-fprebuilt-module-path={}".format(module_path))

        for o in module_paths.get(module_path, []):
            cmds.append(o)

    for o in objects:
        cmds.append(o)

    cmds.append("-o")

    module = necxxt.utils.readModule()
    cmds.append(os.path.join("build", module["name"]))
    cmds.append("-static")

    necxxt.utils.logging.debug(" ".join(cmds))
    runCompiler(cmds)
