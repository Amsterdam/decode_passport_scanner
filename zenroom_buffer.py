import ctypes

_zenroom = ctypes.CDLL('./zenroom/_zenroom.so')

def execute(script, keys, data, verbosity=1, conf=None):
    """
    Execute a Zencode script using the Zenroom 0.8.1 shared library.

    :param string script: a long string containing the script to be executed
    :param string keys: a string, JSON formatted, that contains keys (sensitive information)
    :param string data: a string, also JSON formatted, that contains data
    
    :param number verbosity: a number from 1 to 3 activating more debugging messages
    :param string conf: a short configuration string

    Zenroom embed documentation: https://github.com/DECODEproject/zenroom/wiki/Embed
    """
    stdout_buf = ctypes.create_string_buffer("x" * 20000)
    stdout_len = ctypes.c_size_t(20000)
    stderr_buf = ctypes.create_string_buffer("x" * 1024)
    stderr_len = ctypes.c_size_t(1024)

    _zenroom.zenroom_exec_tobuf(
      script, conf, keys, data, verbosity,
      stdout_buf, stdout_len, stderr_buf, stderr_len)
    
    # if(stderr_buf.value is not None):
    #     return stderr_buf.value
    
    return stdout_buf.value
