import ctypes
import os
import subprocess
import json
import re
from OriginC import structprocessor


sls = None
methods = []
has_struct = False


def getfromj(full=False, attribute_name=None):
    with open("OriginC/shared_info.json", "r") as file:
        file_data = json.load(file)
    if attribute_name is not None:
        return file_data[attribute_name]
    if full:
        return file_data


def writej(dicti):
    with open("OriginC/shared_info.json", "w") as outfile:
        json.dump(dicti, outfile, indent=1)


def is_valid_curlybrace(line):
    inside_quot = False
    valid = "{" in line or "}" in line
    brace = ""
    for let in line:
        if let == "\"":
            inside_quot = not inside_quot
        elif let == "{" or let == "}":
            valid = not inside_quot
            brace = let
    return valid, brace


def remove_method(method_name):
    info = getfromj(full=True)
    try:
        method_name = method_name[:method_name.index("(")+1]  # method(
    except Exception:
        raise Exception("Invalid method name format. Format: 'method()'")

    try:
        with open("OriginC/mainc.c", "r") as file:
            filetxt = file.readlines()
    except Exception:
        raise Exception("Error reading from C file to remove method from. Try removing a method from the built-in\n"
                        "C file with OriginC.")

    clearing = False
    oc = {"{": 0, "}": 0}
    for i, line in enumerate(filetxt):
        if clearing:
            val, let = is_valid_curlybrace(line)
            if val and let != "":
                oc[let] += 1
            filetxt[i] = ""
            if oc["{"] == oc["}"]:
                break
        elif method_name in line and not clearing:
            filetxt[i] = ""
            oc["{"] = 1
            clearing = True
            continue

    info['methods'].remove(method_name)
    writej(info)

    with open("OriginC/mainc.c", "w") as file:
        for line in filetxt:
            file.write(line)


def extract(filetxt):
    mthds = []
    currmeth = ""
    for i, line in enumerate(filetxt.split("\n")):
        if is_method(line=line):
            if currmeth != "":
                mthds.append(currmeth)
                currmeth = ""
                currmeth += line
            else:
                currmeth += line
        else:
            currmeth += line
    else:
        mthds.append(currmeth)
    return mthds


def compile():
    # OriginC/mainc.c

    if has_struct:
        structprocessor.process_struct(filepath="OriginC/mainc.c")

    ccomp = 'gcc'
    ext = sls[1:]

    command = [
        ccomp, '-shared', '-fPIC', '-o',
        f'std_{ext}.{ext}', 'mainc.c'
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, cwd="OriginC")
    except Exception:
        try:
            ccomp = 'clang'
            command = [
                ccomp, '-shared', '-fPIC', '-o',
                f'std_{ext}.{ext}', 'mainc.c'
            ]
            result = subprocess.run(command, capture_output=True, text=True, cwd="OriginC")
        except Exception:
            raise Exception("This error has been raised very likely because you do not have an OriginC valid\n"
                            "C compiler installed on your system (gcc or clang).")


def compile_lib(filepaths):
    global sls
    sls = ".dll" if os.name == 'nt' else ".so"
    for path in filepaths:
        path = path.replace('\\', '/')
        structprocessor.process_struct(filepath=path)
        chfile = path[::-1][:path[::-1].find('/')][::-1]
        cwdir = path[::-1][path[::-1].find('/')+1:][::-1]
        ccomp = 'gcc'
        ext = sls[1:]

        command = [
            ccomp, '-shared', '-fPIC', '-o',
            f'std_{ext}.{ext}', chfile
        ]

        try:
            result = subprocess.run(command, capture_output=True, text=True, cwd=cwdir)
        except Exception:
            try:
                ccomp = 'clang'
                command = [
                    ccomp, '-shared', '-fPIC', '-o',
                    f'std_{ext}.{ext}', chfile
                ]
                result = subprocess.run(command, capture_output=True, text=True, cwd=cwdir)
            except Exception:
                raise Exception("This error has been raised very likely because you do not have an OriginC valid\n"
                                "C compiler installed on your system (gcc or clang).")


def is_method(line=None, name=None, all=False):
    if line is not None:
        if "(" in line:
            ls = line.split("(")
        else:
            return False
        kw = ["if", "while", "switch", "for", "return", "sizeof", "do"]
        if is_valid_curlybrace(line)[0] and not any(ls[0].strip().endswith(i) for i in kw):
            rev = ls[0][::-1].strip()
            if len(rev.split(" ")) < 2:
                return False
            mn = rev[:rev.index(" ")][::-1] + "("
            if all:
                return True, mn  # Yes, and method name
            else:
                return True
    if name is not None:
        d = getfromj(attribute_name="methods")
        return name in d


def ensure_no_duplicates(stringrep):
    info = getfromj(full=True)
    for line in stringrep.split('\n'):
        if "struct" in line and is_valid_curlybrace(line)[0]:
            global has_struct
            has_struct = True
        if "(" in line:
            ls = line.split("(")
        else:
            continue
        kw = ["if", "while", "switch", "for", "return", "sizeof", "do"]
        if is_valid_curlybrace(line)[0] and not any(ls[0].strip().endswith(i) for i in kw):
            rev = ls[0][::-1].strip()
            if len(rev.split(" ")) < 2:
                continue
            mn = rev[:rev.index(" ")][::-1] + "("
            if mn not in info['methods']:
                info['methods'].append(mn)
            else:
                remove_method(mn)
    writej(info)


def process_str(stringrep):
    mthds = extract(stringrep)
    ensure_no_duplicates(stringrep)
    with open("OriginC/mainc.c", "w") as file:
        file.write(stringrep)


def process_file(filepath):
    try:
        with open(filepath, "r") as file:
            prog = file.readlines()
        with open("OriginC/mainc.c", "w") as file:
            file.writelines(prog)
            ensure_no_duplicates(''.join(prog))
    except Exception:
        raise Exception("File path provided for existing .c file appears to be invalid?")


def clear():
    with open("OriginC/mainc.c", "w") as file:
        pass
    data = getfromj(full=True)
    data['methods'] = []
    writej(data)
