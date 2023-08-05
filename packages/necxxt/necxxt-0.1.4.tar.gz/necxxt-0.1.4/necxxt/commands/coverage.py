import os
import re
import shutil
import subprocess

import necxxt.utils
import necxxt.utils.logging


def checkCoverage(config=None, coverage_info=None):
    if not config:
        config = necxxt.utils.readModule()

    if not coverage_info:
        coverage_info = os.path.join(os.getcwd(), "build", "coverage.info")

    if not os.path.isfile(coverage_info):
        necxxt.utils.logging.error(
            "Could not read coverage file \"{}\"".format(coverage_info))
        exit(2)

    lcov_exe = shutil.which("lcov")
    if not lcov_exe:
        necxxt.utils.logging.error("lcov is not installed")
        exit(3)

    cmd = [
        lcov_exe,
        "--rc",
        "lcov_branch_coverage=1",
        "--summary",
        coverage_info
    ]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate()[0].decode("utf-8")

    re_lines = re.compile(".*lines.*:\s*(.*)%.*")
    re_functions = re.compile(".*functions.*:\s*(.*)%.*")
    re_branches = re.compile(".*branches.*:\s*(.*)%.*")

    lines = None
    functions = None
    branches = None
    for line in output.split("\n"):
        match = re_lines.match(line)
        if match:
            lines = float(match.group(1))

        match = re_functions.match(line)
        if match:
            functions = float(match.group(1))

        match = re_branches.match(line)
        if match:
            branches = float(match.group(1))

    coverageThresholdsLines = config.get("coverage", {}).get(
        "thresholds", {}).get("lines", 0.0)
    coverageThresholdsFunctions = config.get(
        "coverage", {}).get("thresholds", {}).get("functions", 0.0)
    coverageThresholdsBranches = config.get(
        "coverage", {}).get("thresholds", {}).get("branches", 0.0)

    necxxt.utils.logging.debug("Current line coverage: {:.2f}%".format(lines))
    necxxt.utils.logging.debug(
        "Current function coverage: {:.2f}%".format(functions))
    necxxt.utils.logging.debug(
        "Current branch coverage: {:.2f}%".format(branches))

    return_code = 100

    if coverageThresholdsLines:
        if lines < coverageThresholdsLines:
            if return_code == 100:
                print()

            necxxt.utils.logging.error(
                "Line coverage dropped under {:.2f}% --> {:.2f}%".format(coverageThresholdsLines, lines))
            return_code += 1

    if coverageThresholdsFunctions:
        if functions < coverageThresholdsFunctions:
            if return_code == 100:
                print()

            necxxt.utils.logging.error(
                "Function coverage dropped under {:.2f}% --> {:.2f}%".format(coverageThresholdsFunctions, functions))
            return_code += 1

    if coverageThresholdsBranches:
        if branches < coverageThresholdsBranches:
            if return_code == 100:
                print()

            necxxt.utils.logging.error(
                "Branch coverage dropped under {:.2f}% --> {:.2f}%".format(coverageThresholdsBranches, branches))
            return_code += 1

    if return_code > 100:
        exit(return_code)
