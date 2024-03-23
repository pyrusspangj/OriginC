This is OriginC release 1.0, the first release of OriginC.

OriginC is a Python package that allows for the implementation of C code to be executed alongside your Python code directly inside your Python program and IDE!
Using ctypes, OriginC does practically all the work for you; simply write your C code in a .c file or just as a Python string, and pass it through the Python-C-Gate (PyCGate).

To get started with OriginC, (a pip installation currently being worked on), import OriginC into your program like so:

```py
from OriginC import *

hello_world = '''
  #include <stdio.h>
  void hello() {
    printf("Hello, world!\n");
  }
  '''

PyCGate.read(stringrep=hello_world)
cLib = PyCGate.get_library()

cLib.hello()

# Output:
# Hello, world!
```

I will continue documenting the README later, as I must go to bed.
