import re
import os

"""
This is a simple code condenser, goes through all the directories to create a single script with resolved
dependencies.

Although it will eradicate the usage of all submodule imports.
"""

re_relative_imports = re.compile(r"(?:from [.]+(.*)) import (.*)")
re_general_imports = re.compile(r"(?:from (.*) )?import (.*)")
re_indentation = re.compile(r"([ ]+)\w+")

includes = ["Asciinpy", "Asciinpy/_2D", "Asciinpy/_3D"]
outputs = "Asciinpy.py"
tab = "    "

code = []
imported = []

general_imports = []
future_imports = []


def put_at_top(lines):
    global code

    for line in lines:
        code[0] = line + ("\n" if not line.endswith("\n") else "") + code[0]


def is_indented(line):
    match = re_indentation.match(line)
    if match:
        return len(match.group(1))
    return False


def is_weird(line):
    if line.strip() == "" or line == "\n":
        return True


def imports(root, file):
    global imported, general_imports, future_imports

    if file in imported:
        return []

    imported.append(file)
    code = []
    ignores_flag = False
    with open(root + "/" + file, "r") as py:
        for line in py.readlines():
            if ignores_flag and is_indented(line) or is_weird(line):
                continue
            elif ignores_flag and not is_indented(line) or is_weird(line):
                ignores_flag = False

            relative_import = re_relative_imports.match(line)
            general_import = re_general_imports.match(line)
            if relative_import:
                if file.startswith("__"):
                    continue
                else:
                    code.extend(
                        imports(
                            root, relative_import.group(1).replace(".", "/", -1) + ".py"
                        )
                    )
            elif general_import:
                if general_import.group(0).startswith("from __"):
                    future_imports.append(line)
                else:
                    general_imports.append(line)
            elif line.startswith("if __name__"):
                ignores_flag = True
                continue
            else:
                code.append(line)
    return code


if __name__ == "__main__":
    for path in includes:
        for file in os.listdir(path):
            if file.endswith(".py") and file != "__init__.py":
                code.extend(imports(path, file))

    put_at_top(imports("Asciinpy", "__init__.py")[::-1])
    put_at_top(general_imports)
    put_at_top(future_imports)

    with open(outputs, "w") as py:
        py.write("".join(code))
