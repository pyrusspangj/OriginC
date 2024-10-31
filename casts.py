import ctypes

# Casts:
cint = ctypes.c_int
cbyte = ctypes.c_byte
cshort = ctypes.c_short
clong = ctypes.c_long
cfloat = ctypes.c_float
cdouble = ctypes.c_double
cbool = ctypes.c_bool


def cchar(val):
    return val.encode()


def char_p(val):
    return ctypes.c_char_p(val.encode())


def cstring(val):
    return char_p(val)


struct = ctypes.Structure
int8 = ctypes.c_int8
int16 = ctypes.c_int16
int32 = ctypes.c_int32
int64 = ctypes.c_int64
longlong = ctypes.c_longlong
longdouble = ctypes.c_longdouble
size_t = ctypes.c_size_t
ssize_t = ctypes.c_ssize_t
uint = ctypes.c_uint
uint8 = ctypes.c_uint8
uint16 = ctypes.c_uint16
uint32 = ctypes.c_uint32
uint64 = ctypes.c_uint64
ulong = ctypes.c_ulong
ulonglong = ctypes.c_ulonglong
ubyte = ctypes.c_ubyte
ushort = ctypes.c_ushort
void_p = ctypes.c_void_p
wchar = ctypes.c_wchar
wchar_p = ctypes.c_wchar_p


def buf(val):
    buffer = ctypes.create_string_buffer(val.encode(), len(val) + 1)  # +1: \0
    return buffer.raw


def array(ctype, length, val=None):
    """
    Create a 1D array of ctype elements, optionally initialized to val.

    Args:
        ctype (ctypes._SimpleCData): The ctypes type of the elements in the array.
        length (int): The number of elements in the array.
        val (optional): The initial value for each element in the array.

    Returns:
        ctypes.Array: An array of ctype elements.
    """

    if str(ctype)[0] == '<':
        ctype = str(ctype)
        if ctype.split(" ")[1] == 'char_p' or ctype.split(" ")[1] == 'cstring':
            ctype = ctypes.c_char_p
        elif ctype.split(" ")[1] == 'cchar':
            ctype = ctypes.c_char
    arr_type = ctype * length
    if val is None:
        return arr_type()
    else:
        return arr_type(*([val] * length))


def array2d(ctype, rows, cols, val=None):
    """
    Create a 2D array of ctype elements, optionally initialized to val.

    Args:
        ctype (ctypes._SimpleCData): The ctypes type of the elements in the array.
        rows (int): The number of rows in the 2D array.
        cols (int): The number of columns in each row.
        val (optional): The initial value for each element in the array.

    Returns:
        list: A 2D array where each element is a ctypes.Array of ctype elements.
    """
    if str(ctype)[0] == '<':
        ctype = str(ctype)
        if ctype.split(" ")[1] == 'char_p' or ctype.split(" ")[1] == 'cstring':
            ctype = ctypes.c_char_p
        elif ctype.split(" ")[1] == 'cchar':
            ctype = ctypes.c_char
    row_type = ctype * cols
    arr_type = row_type * rows
    if val is None:
        return arr_type()
    else:
        return arr_type(*([row_type(*([val] * cols)) for _ in range(rows)]))


def array3d(ctype, depth, rows, cols, val=None):
    """
    Create a 3D array of ctype elements, optionally initialized to val.

    Args:
        ctype (ctypes._SimpleCData): The ctypes type of the elements in the array.
        depth (int): The number of 2D arrays.
        rows (int): The number of rows in each 2D array.
        cols (int): The number of columns in each row.
        val (optional): The initial value for each element in the array.

    Returns:
        list: A 3D array where each element is a 2D array of ctype elements.
    """
    if str(ctype)[0] == '<':
        ctype = str(ctype)
        if ctype.split(" ")[1] == 'char_p' or ctype.split(" ")[1] == 'cstring':
            ctype = ctypes.c_char_p
        elif ctype.split(" ")[1] == 'cchar':
            ctype = ctypes.c_char
    col_type = ctype * cols
    row_type = col_type * rows
    arr_type = row_type * depth
    if val is None:
        return arr_type()
    else:
        return arr_type(*([row_type(*([col_type(*([val] * cols)) for _ in range(rows)])) for _ in range(depth)]))


address = ctypes.addressof
resize = ctypes.resize
alignment = ctypes.alignment
cast = ctypes.cast
ptr = ctypes.pointer

"""def ptr(val):
    if isinstance(val, bytes):
        # if it's bytes, we need to create a ctypes string buffer from it
        # and then cast the buffer's address to c_char_p
        buffer = ctypes.create_string_buffer(val)
        cst = ctypes.cast(ctypes.byref(buffer), ctypes.c_char_p)
        return array(cst, len(val.decode()), val=val.decode())
    else:
        return ctypes.pointer(val)"""


memset = ctypes.memset
memmove = ctypes.memmove
sizeof = ctypes.sizeof
ref = ctypes.byref

kw = [cint, cbyte, cshort, cfloat, cdouble, cchar, char_p, cbool, cstring, struct,
      int8, int16, int32, int64, longlong, longdouble, size_t, ssize_t, uint, uint8, uint16, uint32, uint64,
      ulong, ulonglong, ubyte, ushort, void_p, wchar, wchar_p,
      buf, address, resize, alignment, cast, ptr, memset, memmove, sizeof, ref, array, array2d, array3d]

c_types_dict = {
    'int': 'ctypes.c_int',
    'char': 'ctypes.c_char',
    #'char*': 'ctypes.c_char_p',
    'float': 'ctypes.c_float',
    'double': 'ctypes.c_double',
    'long': 'ctypes.c_long',
    'short': 'ctypes.c_short',
    'unsigned int': 'ctypes.c_uint',
    'unsigned char': 'ctypes.c_ubyte',
    'unsigned long': 'ctypes.c_ulong',
    'unsigned short': 'ctypes.c_ushort',
    'int8_t': 'ctypes.c_int8',
    'int16_t': 'ctypes.c_int16',
    'int32_t': 'ctypes.c_int32',
    'int64_t': 'ctypes.c_int64',
    'uint8_t': 'ctypes.c_uint8',
    'uint16_t': 'ctypes.c_uint16',
    'uint32_t': 'ctypes.c_uint32',
    'uint64_t': 'ctypes.c_uint64',
    'size_t': 'ctypes.c_size_t',
    'ssize_t': 'ctypes.c_ssize_t',
    'long long': 'ctypes.c_longlong',
    'unsigned long long': 'ctypes.c_ulonglong',
    'bool': 'ctypes.c_bool',
    'wchar_t': 'ctypes.c_wchar',
    #'wchar_t*': 'ctypes.c_wchar_p',
    'struct': 'ctypes.Structure',
    'signed char': 'ctypes.c_byte',
    'void': 'ctypes.c_void_p',
    #'void*': 'ctypes.c_void_p',
    'long double': 'ctypes.c_longdouble'
}




