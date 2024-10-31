OriginC is a Python package developed to make the ```ctypes``` package beginner-friendly.

OriginC allows for the seamless implementation of C code into your Python projects.

Exactly as it sounds, here's how to get started with OriginC:
* First, import all from the OriginC package.
* Next, call ```readc()``` and pass in your .c file, or list of .c files.
* Run the program.

Once you've done this, OriginC will compile your C code into a shared library file compatible with your system.
To ensure that the program will be able to read the shared library file, OriginC will then exit the program, and prompt
you to comment out your ```readc()``` line to prevent unnecessary recompilation. 

When your shared library file is compiled and loaded, you can then call it, and access your methods along with the
provided OriginC casts if necessary.
* Access the shared library by calling ```clib()```
  * If you have a shared library of your own already, you can call ```clib(existing="YOUR_LIBRARY_NAME[.dll/.so]")```.
  * Otherwise, leaving it as is will automatically access the library file created by OriginC.
* Call your method!

---

`Example 1`:
```py
# main.py
from OriginC import *

readc("main.c")
```
* Import all from OriginC.
* ```readc(filename)```

Running this will print the message:
```commandline
Compiling in directory: [YOUR DIRECTORY]
Loaded library from [YOUR DIRECTORY]/OriginC_shared.dll
PLEASE COMMENT OUT OR REMOVE YOUR 'readc([filepaths])' STATEMENT!!!
This message indicates that your shared library has been compiled and created successfully!
This exception has been raised to prevent further errors due to attempted access of an unloaded library file.
Commenting out, or removing your 'readc([filepaths])' statement is necessary before running your program again.

Process finished with exit code 0
```
* Now, you can call ```clib()``` and access the methods within your .c file.
* If your .c file looked like this, for example:
```c
// main.c
#include <stdio.h>

void originc(const char* message) {
    printf("%s\n", message);
}
```
* Call ```clib().originc(char_p("Hello, world!"))``` to access the method, like so:
```py 
from OriginC import *

#readc("main.c")

clib().originc(char_p("Hello, world!"))
```
```commandline
Hello, world!

Process finished with exit code 0
```
---
