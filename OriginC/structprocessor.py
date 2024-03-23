import re
import json
import ctypes
from OriginC.casts import *


structs = {}


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


def get_struct_name(stringrep, i):
    lines = stringrep[i:]
    if len(lines) == 0:
        return
    line = lines[0].strip()
    if not line.startswith("typedef"):
        return line[line.find("struct") + 6:line.find("{")].strip()
    oc = {"{": 0, "}": 0}
    for line in lines:
        if line.strip() == "":
            continue
        if "{" in line or "}" in line:
            val, let = is_valid_curlybrace(line)
            if val:
                oc[let] += 1
                if oc["{"] == oc["}"] and oc["{"] > 0:
                    return line[line.find("{")+2:line.find(";")].strip()
    raise Exception("Invalid struct declaration or name.")


def is_struct(line):
    return "struct" in line and is_valid_curlybrace(line)[0]


def process_struct(filepath=None, stringrep=None):
    if filepath is not None:
        with open(filepath, "r") as f:
            lines = f.readlines()
    elif stringrep is not None:
        lines = stringrep.split("\n")
    else:
        return
    currstruct = ""
    oc = {"{": 0, "}": 0}
    for i, line in enumerate(lines):
        if is_struct(line) and (oc["{"] == oc["}"]):
            oc["{"] = 1
            currstruct = get_struct_name(lines, i)
            ensure_no_duplicate_structures(currstruct)
            structs[currstruct] = []
            structs[currstruct].append(line)
        elif currstruct != "":
            structs[currstruct].append(line)
            if "{" in line or "}" in line:
                val, let = is_valid_curlybrace(line)
                if val:
                    oc[let] += 1
                    if oc["{"] == oc["}"]:
                        currstruct = ""
                        oc["{"], oc["}"] = 0, 0

    info = getfromj(full=True)
    ss = []
    for st in structs.keys():
        ss.append(st)
    info['structs'] = ss
    writej(info)

    with open("OriginC/CustomStructures.py", "a+") as file:
        file.seek(0)
        content = file.read()
        if "import ctypes" not in content:
            file.write("import ctypes\n")
            file.write("from OriginC.casts import *\n")
    for st in structs.keys():
        build(st)
    freshen()


def format_c_line(line):
    pattern = r'\s*(\w+)\s*([\*]*)\s*(\w+)\s*([\[\]\d]*)\s*;.*'
    match = re.match(pattern, line.strip())

    if not match:
        return "Invalid input or format not supported."

    datatype, pointer, name, brackets = match.groups()
    formatted_line = f"{datatype}{pointer} {name}{brackets};"
    return formatted_line


def get_arr_info(line):
    line = line.replace(" ", "")[line.find('['):line.find(';')]
    lengths = line.split("]")
    vals = []
    for length in lengths:
        vals.append(int(length.replace("[", "")))
    if len(vals) == 1:
        return None, None, vals[0]
    elif len(vals) == 2:
        return None, vals[0], vals[1]
    elif len(vals) == 3:
        return vals[0], vals[1], vals[2]


def getfield(line, stringrep, i):
    line = format_c_line(line)
    def first_alpha_ind(name):
        for i, ch in enumerate(name):
            if 'a' <= ch <= 'z' or 'A' <= ch <= 'Z':
                return i
        return -1

    def last_alpha_ind(name, ind):
        for i in range(ind, len(name)):
            ch = name[i]
            if not ('a' <= ch <= 'z' or 'A' <= ch <= 'Z' or '0' <= ch <= '9' or ch == '_'):
                return i
        return len(name)

    def count_ptr(info):
        return info.count("*")

    def count_arr(name):
        return name.count("[")

    if "}" in line or ";" not in line:
        return None, None

    line = line[:line.find(";")].strip()
    reverse_index = line[::-1].find(" ")
    name = line[-reverse_index:].strip()

    bracket = count_arr(name)
    pointer = count_ptr(line)

    info = line[:-(reverse_index + 1)].strip()

    if "[" in name or "*" in name:
        fai = first_alpha_ind(name)
        lai = last_alpha_ind(name, fai)
        name = name[fai:lai]

    #print(f"Name: {name}")
    #print(f"Info: {info}")

    if not pointer:
        typec = c_types_dict[info]
    else:
        c = count_ptr(info)
        try:
            typec = c_types_dict[info[:info.rfind("*")].strip()]
        except KeyError:
            typec = c_types_dict[info[:info.find("*")].strip()]
        typec = f"{'ctypes.POINTER(' * c}{typec}{')' * c}"

        #specific types
        if typec == "ctypes.POINTER(ctypes.c_char)":
            typec = "ctypes.c_char_p"
        elif typec == "ctypes.POINTER(ctypes.c_void_p)":
            typec = "ctypes.c_void_p"
        elif typec == "ctypes.POINTER(ctypes.c_wchar)":
            typec = "ctypes.c_wchar_p"
    if bracket:
        depth, rows, cols = get_arr_info(line)
        #typec = f"{'(' * bracket}{typec}{')' * bracket}" ??? HELP
        typec = f"{'(' * bracket}{typec}"
        for leng in [cols, rows, depth]:
            if leng is not None:
                typec += f" * {leng})"

    return name, typec


def build_char_decode_ifnec(current_struct_fields, ind):
    wr = ""
    for tup in current_struct_fields:
        prop = tup[0].replace("'", "")
        if prop == "":
            continue
        if 'ctypes.c_char_p' in tup[1] or 'ctypes.c_char' in tup[1] or 'ctypes.c_buffer' in tup[1]:
            wr += ("\n"
                       f"{"\t" * ind}@property\n"
                       f"{"\t" * ind}def _{prop}(self):\n"
                       f"{"\t" * (ind + 1)}try:\n"
                       f"{"\t" * (ind + 2)}return self.{prop}.decode() if self.{prop} is not None else None\n"
                       f"{"\t" * (ind + 1)}except Exception:\n"
                       f"{"\t" * (ind + 2)}return 'The value in which you are trying to reach is not applicable to this object.'\n")

            wr += ("\n"
                   f"{"\t" * ind}@property\n"
                   f"{"\t" * ind}def _{prop}_ARR(self):\n"
                   f"{"\t" * (ind + 1)}try:\n"
                   f"{"\t" * (ind + 2)}return [item for item in self.{prop}] if self.{prop} is not None else None\n"
                   f"{"\t" * (ind + 1)}except Exception:\n"
                   f"{"\t" * (ind + 2)}return 'The value in which you are trying to reach is not applicable to this object.'\n")
        elif 'ctypes.' in tup[1]:
            if ".POINTER" in tup[1] or tup[1].endswith("_p"):
                wr += ("\n"
                   f"{"\t" * ind}@property\n"
                   f"{"\t" * ind}def _{prop}_ARR(self):\n"
                   f"{"\t" * (ind + 1)}try:\n"
                   f"{"\t" * (ind + 2)}return [item for item in self.{prop}] if self.{prop} is not None else None\n"
                   f"{"\t" * (ind + 1)}except Exception:\n"
                   f"{"\t" * (ind + 2)}return 'The value in which you are trying to reach is not applicable to this object.'\n")

                wr += ("\n"
                       f"{"\t" * ind}@property\n"
                       f"{"\t" * ind}def _{prop}(self):\n"
                       f"{"\t" * (ind + 1)}try:\n"
                       f"{"\t" * (ind + 2)}return self.{prop}.contents.value if self.{prop} is not None else None\n"
                       f"{"\t" * (ind + 1)}except Exception:\n"
                       f"{"\t" * (ind + 2)}return 'The value in which you are trying to reach is not applicable to this object.'\n")
            else:
                wr += ("\n"
                       f"{"\t" * ind}@property\n"
                       f"{"\t" * ind}def _{prop}(self):\n"
                       f"{"\t" * (ind + 1)}return self.{prop} if self.{prop} is not None else None\n")
        else:  # a struct
            wr += ("\n"
                   f"{"\t" * ind}@property\n"
                   f"{"\t" * ind}def _{prop}(self):\n"
                   f"{"\t" * (ind + 1)}return self.{prop}.contents if self.{prop} is not None else None\n")
    return wr


def build(strct):
    with open("OriginC/CustomStructures.py", "a") as file:
        arr = structs[strct]
        cls_indent = 0
        cls_info = {}
        on = []
        ogname = None
        name = None
        for i, line in enumerate(arr):
            if len(on) > 0:
                this = on[len(on) - 1]
            if is_struct(line):
                ogname = name if name is not None else None
                name = get_struct_name(arr, i)
                if cls_indent > 0:
                    cls_info[this].append((name, name))
                on.append(name)
                cls_info[name] = []
                file.write(f"{"\t" * cls_indent}class {name}(ctypes.Structure):\n")
                cls_indent += 1
                continue
            elif "}" in line and is_valid_curlybrace(line)[0]:
                if ogname is not None:
                    name = ogname
                    ogname = None
                file.write(f"{"\t" * cls_indent}_fields_ = {cls_info[this]}\n")
                wr = build_char_decode_ifnec(cls_info[this], cls_indent)
                if wr is not None:
                    file.write(wr)
                on.pop()
                cls_indent -= 1
                continue
            else:
                inf = getfield(line, arr, i)
                if inf != (None, None):
                    cls_info[this].append(getfield(line, arr, i))


def freshen():
    with open("OriginC/CustomStructures.py", "r") as file:
        lines = file.readlines()

    modified_lines = []
    for line in lines:
        if "_fields_" in line:
            start = line.find("[(")
            end = line.find(")]") + 2
            if start != -1 and end != -1:
                tuple_str = line[start:end]
                tuples = eval(tuple_str)
                modified_tuples = []
                for t in tuples:
                    if len(t) >= 1 and t[0] == '':
                        continue
                    #print(t)
                    modified_tuple = f"('{t[0]}', {t[1].replace("'", '')})"
                    modified_tuples.append(modified_tuple)
                modified_tuple_str = "[" + ", ".join(modified_tuples) + "]"
                modified_line = line[:start] + modified_tuple_str + line[end:]
                modified_lines.append(modified_line)
            else:
                modified_lines.append(line)
        else:
            modified_lines.append(line)

    with open("OriginC/CustomStructures.py", "w") as file:
        file.writelines(modified_lines)


def remove_struct(name):
    with open("OriginC/CustomStructures.py", "r") as file:
        lines = file.readlines()
        clearing = False
        for i, line in enumerate(lines):
            if clearing:
                if not line.startswith("\t") and "class" in line and "(ctypes.Structure)" in line:
                    clearing = False
                    break
                else:
                    lines[i] = ""
            elif f"class {name}" in line:
                clearing = True
                lines[i] = ""
                data = getfromj(full=True)
                data['structs'].remove(f"{name}")
                writej(data)
        with open("OriginC/CustomStructures.py", "w") as wfile:
            wfile.writelines(lines)


def ensure_no_duplicate_structures(structname):
    with open("OriginC/CustomStructures.py", "r") as file:
        lines = file.readlines()
        for line in lines:
            if f"class {structname}" in line:
                remove_struct(structname)
                return


def clear():
    with open("OriginC/CustomStructures.py", "w") as file:
        pass
    data = getfromj(full=True)
    data['structs'] = []
    writej(data)

