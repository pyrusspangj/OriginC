import os
from OriginC import processor, structprocessor
import ctypes


sls = None
doc = True


def documentation():
    if doc:
        print(f"OriginC Documentation (Turn this message of via the statement 'PyCGate.doc = False'):\n"
                f"Rules when writing a C-Representing string to pass through 'PyCGate.read(stringrep=STRING)':\n"
                f"\t1. Do not write your C in any sort of array, just in a string, like this:\n"
                f"\t   Write your C-Representing string with via three single quotes, or parenthesis. Example:\n"
                "\t   '''void hello(){                          ('void hello(){'\\n\n"
                "\t          printf(\"Hello world!\\n\");        '    printf(\"Hello world!\\n\");'\\n\n"
                "\t      }'''                                    '}')\n"
                "\t   ^ Triple quotes do not require \\n ^      ^ Parenthesis strings do require \\n ^"
                f"If you are using OriginC with an existing .c file, feel free to ignore every rule stated.")


def read(stringrep=None, filepath=None):
    if (stringrep is None and filepath is None) or (stringrep is not None and filepath is not None):
        raise Exception("To process your C code, please:\n"
                        "1. Provide a string representing your C code via 'stringrep={STRING}'\n"
                        "2. Provide a filepath to a .c file, or a .txt file which represents C code, all via 'filepath={FILEPATH}\n"
                        "But not both! (At least not at the same time)")
    processor.has_struct = False
    global sls
    sls = ".dll" if os.name == 'nt' else ".so"
    processor.sls = sls
    if stringrep is not None:
        processor.process_str(stringrep)
    elif filepath is not None:
        processor.process_file(filepath)
    processor.compile()


def load_libraries(filepaths):
    processor.compile_lib(filepaths)


def get_library(existing=None):
    if existing is not None:
        return ctypes.CDLL(existing, mode=ctypes.RTLD_GLOBAL)

    lib = None
    if sls is not None:
        fn = "std_dll" if sls == ".dll" else "std_so"
        try:
            lib = ctypes.CDLL(os.getcwd()+f"/{fn}{sls}", mode=ctypes.RTLD_GLOBAL)
        except:
            lib = ctypes.CDLL(f"OriginC/{fn}{sls}", mode=ctypes.RTLD_GLOBAL)
    if lib is not None:
        return lib
    else:
        raise Exception("There was an error processing your share library, and I'm really not quite sure how you got this error.")


def reset_file():
    try:
        processor.clear()
        structprocessor.clear()
    except Exception:
        raise Exception("Error reading from C file to remove method from. Try removing a method from the built-in\n"
                        "C file with OriginC.")


def remove_method(method_name):
    processor.remove_method(method_name)
