import os, sys, select, ctypes

### source: https://stackoverflow.com/questions/9488560/capturing-print-output-from-shared-library-called-from-python-with-ctypes-module #
def _setup_pipe():
    global pipe_out, pipe_in, stdout
    sys.stdout.write(' \b')
    pipe_out, pipe_in = os.pipe()
    stdout = os.dup(1)
    os.dup2(pipe_in, 1)

def _more_data():
    r, _, _ = select.select([pipe_out], [], [], 0)
    return bool(r)

def _read_pipe():
    out = ''
    while _more_data():
        out += os.read(pipe_out, 1024)

    return out
###

# Init Zenroom shared library
_zenroom = ctypes.CDLL('zenroom/_zenroom.so')
 
def execute(script, keys, data):
    _setup_pipe()
    _zenroom.zenroom_exec(
        # script, conf, keys, data, verbosity
          script, None, keys, data, 1,        ) 
    os.dup2(stdout, 1)
    return _read_pipe()