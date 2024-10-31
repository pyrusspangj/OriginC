import os
import ctypes
import subprocess


def get_system_compatible_library_extension():
	# return a .dll extension if the user's system is Windows, for all else cases, it returns a .so extension
	return '.dll' if os.name == "nt" else '.so'


sls = get_system_compatible_library_extension()
cwd = os.getcwd()
me = os.path.abspath(__file__)
mydir = os.path.dirname(me)
lib = None


def readc(filepaths):
	global lib
	if isinstance(filepaths, str):
		compilec([filepaths])
	else:
		compilec(filepaths)
	alert()


def compilec(filepaths):
	global sls, cwd, lib

	paths = []
	for filepath in filepaths:
		if os.path.isabs(filepath):
			paths.append(filepath)
		else:
			paths.append(os.path.abspath(filepath))

	ccompiler = ['gcc', 'clang']

	for compiler in ccompiler:
		command = [
			compiler, '-shared', '-fPIC', '-o',
			f'OriginC_shared{sls}'
		] + paths
		cwd = os.path.dirname(me)
		print(f"Compiling in directory: {cwd}")
		result = subprocess.run(command, capture_output=True, text=True, cwd=mydir)
		if result.returncode == 0:
			lib = get_library()
			break
		else:
			print(f"Compilation failed with {compiler}:\n{result.stderr}")
			exit(1)



def get_library(existing=None):
	global mydir, sls
	library_path = f"{mydir}/OriginC_shared{sls}"
	if existing is not None:
		return ctypes.CDLL(existing, mode=ctypes.RTLD_GLOBAL)

	try:
		clib = ctypes.CDLL(library_path, mode=ctypes.RTLD_GLOBAL)
		print(f"Loaded library from {library_path}")
		return clib
	except OSError as e:
		print(f"Failed to load library from {library_path}: {e}")
		exit(1)


def alert():
	"""
	The purpose of this method is as follows:
	You cannot process a shared library, and then immediately use it. This alert terminates the program immediately
	upon compilation of the shared library, ensuring that for any following executions, the shared library will
	be available for use.
	"""
	print("PLEASE COMMENT OUT OR REMOVE YOUR 'readc([filepaths])' STATEMENT!!!\n"
			"This message indicates that your shared library has been compiled and created successfully!\n"
			"This exception has been raised to prevent further errors due to attempted access of an unloaded library file.\n"
			"Commenting out, or removing your 'readc([filepaths])' statement is necessary before running your program again.")
	exit(0)


def clib(existing=None):
	global sls, mydir
	if existing is None:
		return get_library(f"{mydir}/OriginC_shared{sls}")
	else:
		return get_library(existing)