import json
import os

import necxxt.utils


def initialize():
    print("This utility will walk you through creating a necxxt.json file.")
    print("It only covers the most common items, and tries to guess sensible defaults.")
    print()
    print("Use `necxxt install <pkg>` afterwards to install a package and")
    print("save it as a dependency in the necxxt.json file.")
    print()
    print("Press ^C at any time to quit.")

    module = {
        "name": os.path.basename(os.path.normpath(os.getcwd())),
        "version": "1.0.0",
        "description": "",
        "author": "",
        "license": "MIT"
    }

    module["name"] = input("package name: ({}) ".format(
        module["name"])).strip() or module["name"]
    module["version"] = input("version: ({}) ".format(
        module["version"])).strip() or module["version"]
    module["description"] = input(
        "description: ").strip() or module["description"]
    git_repository = input("git repository: ").strip()
    if git_repository:
        module["repository"] = {
            "type": "git",
            "url": git_repository
        }
    module["author"] = input(
        "author: ").strip() or module["author"]
    module["license"] = input("license: ({}) ".format(
        module["license"])).strip() or module["license"]
    print("About to write to {}:".format(
        os.path.join(os.getcwd(), "necxxt.json")))
    print()
    print(json.dumps(module, indent=4))
    print()
    response = input("Is this OK? (yes) ") or "yes"
    if not response in ["yes"]:
        print("Aborted.")
        print()
        exit(1)

    necxxt.utils.writeModule(module)
